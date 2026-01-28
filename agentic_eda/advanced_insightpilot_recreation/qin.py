"""
QuickInsights-like mining over tabular CSV data.

This is a faithful but lightweight re-imagining of the SIGMOD'19 QuickInsights
workflow: we scan multi-dimensional data, compute impact measures, and surface
high-scoring subjects (subspace + breakdown + measure) together with insight
types such as "OutstandingTop1" and "Outlier".

Usage
-----
python qin.py --path agentic_eda/T1.csv --max-insights 5 --json-out insights.json
"""

from __future__ import annotations

import argparse
import heapq
import json
import math
import re
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator, List, Mapping, Optional, Sequence

import numpy as np
import pandas as pd

import helpers.hpandas as hpandas

# Stores the most recently normalised dataset for downstream inspection / visualisation.
LAST_NORMALISED_DATASET: pd.DataFrame | None = None


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class InsightSubject:
    subspace: dict[str, Any]
    breakdown: str
    measure: str


@dataclass
class Insight:
    subject: InsightSubject
    insight_type: str
    impact: float
    significance: float
    score: float
    highlight: dict[str, Any]


@dataclass(order=True)
class SubjectTask:
    priority: float
    impact: float = field(compare=False)
    subspace: dict[str, Any] = field(compare=False)
    breakdown: Optional[str] = field(compare=False)
    df_view: pd.DataFrame = field(compare=False)
    depth: int = field(compare=False)


@dataclass
class AggregationPayload:
    frame: pd.DataFrame
    group_columns: Sequence[str]
    expanding: Optional[str] = None

    def is_trivial_group(self) -> bool:
        if not self.group_columns:
            return False
        last = self.group_columns[-1]
        if last not in self.frame.columns:
            return False
        return self.frame[last].nunique(dropna=True) <= 1


@dataclass
class GlobalStats:
    means: Mapping[str, float]
    stds: Mapping[str, float]
    counts: Mapping[str, int]


@dataclass
class TaskContext:
    subspace: Mapping[str, Any]
    breakdown: Optional[str]
    measure: str
    impact: float
    df_view: pd.DataFrame
    payload: AggregationPayload
    global_stats: GlobalStats


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _compute_global_stats(df: pd.DataFrame, measures: Sequence[str]) -> GlobalStats:
    means: dict[str, float] = {}
    stds: dict[str, float] = {}
    counts: dict[str, int] = {}
    for measure in measures:
        if measure not in df.columns:
            continue
        series = pd.to_numeric(df[measure], errors="coerce")
        means[measure] = float(series.mean(skipna=True))
        stds[measure] = _safe_std(series)
        counts[measure] = int(series.count())
    return GlobalStats(means=means, stds=stds, counts=counts)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _subspace_key(subspace: Mapping[str, Any]) -> tuple[tuple[str, Any], ...]:
    return tuple(sorted(subspace.items(), key=lambda item: item[0]))


def _apply_subspace(df: pd.DataFrame, subspace: Mapping[str, Any]) -> pd.DataFrame:
    if not subspace:
        return df
    mask = pd.Series(True, index=df.index)
    for column, value in subspace.items():
        if column not in df.columns:
            return df.iloc[0:0]
        mask = mask & (df[column] == value)
    return df.loc[mask]


def _flatten_columns(frame: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(frame.columns, pd.MultiIndex):
        return frame
    frame = frame.copy()
    frame.columns = ["__".join(col).strip("_") if isinstance(col, tuple) else col for col in frame.columns.values]
    return frame


def _measure_col(measure: str, agg: str) -> str:
    return f"{measure}__{agg}"


def _safe_std(series: pd.Series) -> float:
    if series.count() <= 1:
        return 0.0
    return float(series.std(ddof=0))


def _discover_fd_pairs(df: pd.DataFrame, dimensions: Sequence[str], max_pairs: int = 64) -> dict[str, list[tuple[str, ...]]]:
    """Discover simple functional dependencies dim -> dim by checking uniqueness."""
    discovered: dict[str, list[tuple[str, ...]]] = defaultdict(list)
    checked = 0
    for determinant in dimensions:
        if determinant not in df.columns:
            continue
        grouping = df.groupby(determinant, dropna=True)
        for dependent in dimensions:
            if determinant == dependent or dependent not in df.columns:
                continue
            if grouping[dependent].nunique(dropna=True).max() <= 1:
                discovered[dependent].append((determinant,))
                checked += 1
                if checked >= max_pairs:
                    return discovered
    return discovered


def _is_fd_triggered(
    subspace: Mapping[str, Any],
    breakdown: Optional[str],
    fd_registry: Mapping[str, Sequence[tuple[str, ...]]],
) -> bool:
    if breakdown is None:
        return False
    lhs_options = fd_registry.get(breakdown, ())
    if not lhs_options:
        return False
    subspace_keys = set(subspace.keys())
    for lhs in lhs_options:
        if set(lhs).issubset(subspace_keys):
            return True
    return False


def _merge_fd_registry(
    auto_fd: Mapping[str, Sequence[tuple[str, ...]]],
    manual_fd: Optional[Sequence[tuple[Sequence[str] | str, str]]],
) -> dict[str, tuple[tuple[str, ...], ...]]:
    registry: dict[str, list[tuple[str, ...]]] = defaultdict(list)
    for rhs, lhs_list in auto_fd.items():
        for lhs in lhs_list:
            registry[rhs].append(tuple(lhs))
    if manual_fd:
        for lhs, rhs in manual_fd:
            if isinstance(lhs, str):
                lhs_tuple = (lhs,)
            else:
                lhs_tuple = tuple(lhs)
            registry[rhs].append(lhs_tuple)
    return {rhs: tuple(lhs_list) for rhs, lhs_list in registry.items()}


EPSILON = 1e-9


def _get_group_stats(context: TaskContext) -> pd.DataFrame:
    frame = context.payload.frame
    breakdown = context.breakdown
    measure = context.measure
    if breakdown and breakdown not in frame.columns:
        return pd.DataFrame()

    stats = {}
    if breakdown:
        stats["breakdown"] = frame[breakdown]
    else:
        stats["breakdown"] = pd.Series(["__global__"] * len(frame))

    for stat in ("mean", "count", "std", "sum", "min", "max"):
        col_name = _measure_col(measure, stat)
        if col_name in frame.columns:
            stats[stat] = pd.to_numeric(frame[col_name], errors="coerce")
    if "count" not in stats and "__count__" in frame.columns:
        stats["count"] = pd.to_numeric(frame["__count__"], errors="coerce")

    result = pd.DataFrame(stats)
    if "count" not in result.columns:
        result["count"] = 0
    return result


def _measure_function_of_breakdown(context: TaskContext) -> bool:
    stats = _get_group_stats(context)
    if stats.empty or "std" not in stats.columns:
        return False
    std_series = stats["std"].fillna(0.0)
    counts = stats["count"].fillna(0)
    if (counts >= 2).any():
        return bool((std_series[counts >= 2] <= EPSILON).all())
    return False


# ---------------------------------------------------------------------------
# Top-k buffer for pruning
# ---------------------------------------------------------------------------

class TopKBuffer:
    def __init__(self, capacity: int):
        self.capacity = max(1, capacity)
        self._buffers: dict[str, list[Insight]] = {}

    def should_prune(self, insight_type: str, max_possible_score: float) -> bool:
        buf = self._buffers.get(insight_type)
        if not buf or len(buf) < self.capacity:
            return False
        threshold = min(item.score for item in buf)
        return max_possible_score <= threshold

    def record(self, insight: Insight) -> None:
        buf = self._buffers.setdefault(insight.insight_type, [])
        buf.append(insight)
        buf.sort(key=lambda item: item.score, reverse=True)
        if len(buf) > self.capacity:
            del buf[self.capacity :]


# ---------------------------------------------------------------------------
# Aggregation query engine with caching
# ---------------------------------------------------------------------------

class AggregationQueryEngine:
    """Implements the QuickInsights AggregationQuery API with caching and batching."""

    def __init__(self, df: pd.DataFrame):
        self._df = df
        self._cache: dict[tuple[Any, ...], AggregationPayload] = {}

    def query(
        self,
        subspace: Mapping[str, Any],
        expanding_dimension: Optional[str],
        breakdown: Optional[str],
        measures: Sequence[str],
        order_by: Optional[str] = None,
    ) -> AggregationPayload:
        key = (frozenset(subspace.items()), expanding_dimension, breakdown, tuple(sorted(measures)))
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        base_df = _apply_subspace(self._df, subspace)

        group_columns: list[str] = []
        if expanding_dimension:
            group_columns.append(expanding_dimension)
        if breakdown:
            group_columns.append(breakdown)

        payload_frame: pd.DataFrame
        if not group_columns:
            # Aggregate full subspace
            stats = {}
            for measure in measures:
                if measure not in base_df.columns:
                    continue
                series = pd.to_numeric(base_df[measure], errors="coerce")
                stats[f"{measure}__mean"] = float(series.mean(skipna=True))
                stats[f"{measure}__sum"] = float(series.sum(skipna=True))
                stats[f"{measure}__count"] = int(series.count())
                stats[f"{measure}__std"] = _safe_std(series)
                stats[f"{measure}__min"] = float(series.min(skipna=True)) if series.count() else float("nan")
                stats[f"{measure}__max"] = float(series.max(skipna=True)) if series.count() else float("nan")
            stats["__count__"] = int(len(base_df))
            payload_frame = pd.DataFrame([stats])
        else:
            agg_spec: dict[str, list[str]] = {}
            for measure in measures:
                if measure in base_df.columns:
                    agg_spec[measure] = ["mean", "sum", "count", "std", "min", "max"]
            if agg_spec:
                grouped = base_df.groupby(group_columns, dropna=False)
                payload_frame = _flatten_columns(grouped.agg(agg_spec).reset_index())
            else:
                grouped = base_df.groupby(group_columns, dropna=False)
                payload_frame = grouped.size().reset_index(name="__count__")

        if order_by and order_by in payload_frame.columns:
            payload_frame = payload_frame.sort_values(order_by, ascending=False).reset_index(drop=True)

        payload = AggregationPayload(frame=payload_frame, group_columns=tuple(group_columns), expanding=expanding_dimension)
        self._cache[key] = payload

        if expanding_dimension and expanding_dimension in payload_frame.columns:
            # Populate cache for sibling subspaces (smart batching)
            root_subspace = {k: v for k, v in subspace.items() if k != expanding_dimension}
            for value, sub_df in payload_frame.groupby(expanding_dimension, dropna=False):
                new_subspace = dict(root_subspace)
                new_subspace[expanding_dimension] = value
                sibling_key = (frozenset(new_subspace.items()), None, breakdown, tuple(sorted(measures)))
                sibling_frame = sub_df.drop(columns=[expanding_dimension]) if expanding_dimension in sub_df.columns else sub_df
                self._cache[sibling_key] = AggregationPayload(
                    frame=sibling_frame.reset_index(drop=True),
                    group_columns=tuple(col for col in group_columns if col != expanding_dimension),
                    expanding=None,
                )

        return payload


# ---------------------------------------------------------------------------
# Subject searcher (best-first with impact-driven queue)
# ---------------------------------------------------------------------------

@dataclass(order=True)
class SubspaceCandidate:
    priority: float
    subspace: dict[str, Any] = field(compare=False)
    df_view: pd.DataFrame = field(compare=False)
    impact: float = field(compare=False)
    depth: int = field(compare=False)


class SubjectSearcher:
    """Enumerate subspaces and breakdown dimensions using best-first search."""

    def __init__(
        self,
        df: pd.DataFrame,
        dimensions: Sequence[str],
        min_support: float,
        max_depth: int,
        max_tasks: int,
    ):
        self._df = df
        self._dimensions = [dim for dim in dimensions if dim in df.columns]
        self._min_support = min_support
        self._max_depth = max_depth
        self._max_tasks = max_tasks
        self._total_rows = max(1, len(df))

    def iter_tasks(self) -> Iterator[SubjectTask]:
        if self._df.empty:
            return

        seed = SubspaceCandidate(
            priority=-1.0,
            subspace={},
            df_view=self._df,
            impact=1.0,
            depth=0,
        )
        heap: list[SubspaceCandidate] = [seed]
        seen: set[tuple[tuple[str, Any], ...]] = set()
        tasks_yielded = 0

        while heap and tasks_yielded < self._max_tasks:
            candidate = heapq.heappop(heap)
            if candidate.impact < self._min_support:
                continue

            for breakdown in self._dimensions:
                if breakdown in candidate.subspace:
                    continue
                df_view = candidate.df_view
                impact = candidate.impact
                task = SubjectTask(
                    priority=candidate.priority,
                    impact=impact,
                    subspace=dict(candidate.subspace),
                    breakdown=breakdown,
                    df_view=df_view,
                    depth=candidate.depth,
                )
                tasks_yielded += 1
                yield task
                if tasks_yielded >= self._max_tasks:
                    break

            if candidate.depth >= self._max_depth:
                continue

            for dimension in self._dimensions:
                if dimension in candidate.subspace:
                    continue
                counts = candidate.df_view[dimension].value_counts(dropna=False).head(32)
                for value, count in counts.items():
                    if pd.isna(value):
                        continue
                    new_subspace = dict(candidate.subspace)
                    new_subspace[dimension] = value
                    key = _subspace_key(new_subspace)
                    if key in seen:
                        continue
                    seen.add(key)
                    new_df_view = candidate.df_view[candidate.df_view[dimension] == value]
                    impact = count / self._total_rows
                    if impact < self._min_support:
                        continue
                    heapq.heappush(
                        heap,
                        SubspaceCandidate(
                            priority=-impact,
                            subspace=new_subspace,
                            df_view=new_df_view,
                            impact=impact,
                            depth=candidate.depth + 1,
                        ),
                    )


# ---------------------------------------------------------------------------
# Insight evaluators
# ---------------------------------------------------------------------------


class BaseInsightEvaluator:
    insight_type: str = "Base"

    def can_evaluate(self, context: TaskContext) -> bool:
        if context.breakdown is None:
            return False
        stats = _get_group_stats(context)
        return not stats.empty and stats["count"].fillna(0).sum() > 0

    def evaluate(self, context: TaskContext) -> list[Insight]:
        raise NotImplementedError


class OutstandingTop1Evaluator(BaseInsightEvaluator):
    insight_type = "OutstandingTop1"

    def evaluate(self, context: TaskContext) -> list[Insight]:
        stats = _get_group_stats(context).dropna(subset=["mean"])
        if stats.empty or stats["breakdown"].nunique(dropna=True) <= 1:
            return []
        top_row = stats.sort_values("mean", ascending=False).iloc[0]
        global_mean = float(context.global_stats.means.get(context.measure, float("nan")))
        global_std = float(context.global_stats.stds.get(context.measure, 0.0))
        group_count = float(top_row.get("count", 0.0))
        local_support = group_count / max(1.0, float(len(context.df_view)))
        if math.isfinite(global_std) and global_std <= EPSILON:
            significance = max(0.0, float(top_row["mean"] - global_mean))
        else:
            significance = max(0.0, float((top_row["mean"] - global_mean) / (global_std + EPSILON)))
        significance *= max(local_support, EPSILON)
        significance = min(1.0, significance)
        impact = float(context.impact * max(local_support, EPSILON))
        score = float(impact * significance)
        if score <= 0:
            return []
        insight = Insight(
            subject=InsightSubject(subspace=dict(context.subspace), breakdown=context.breakdown or "", measure=context.measure),
            insight_type=self.insight_type,
            impact=float(round(impact, 4)),
            significance=float(round(significance, 4)),
            score=float(round(score, 4)),
            highlight={
                "top_category": top_row["breakdown"],
                "category_mean": round(float(top_row["mean"]), 4),
                "global_mean": round(float(global_mean), 4),
                "category_count": int(top_row.get("count", 0)),
                "category_support": round(local_support, 4),
            },
        )
        return [insight]


class OutlierEvaluator(BaseInsightEvaluator):
    insight_type = "Outlier"

    def evaluate(self, context: TaskContext) -> list[Insight]:
        stats = _get_group_stats(context).dropna(subset=["mean"])
        if stats.empty or stats["breakdown"].nunique(dropna=True) <= 1:
            return []
        global_mean = float(context.global_stats.means.get(context.measure, float("nan")))
        global_std = float(context.global_stats.stds.get(context.measure, 0.0))
        if not math.isfinite(global_std) or global_std <= EPSILON:
            return []
        threshold = global_mean + global_std
        candidates = stats[stats["mean"] >= threshold]
        if candidates.empty:
            return []
        row = candidates.sort_values("mean", ascending=False).iloc[0]
        group_count = float(row.get("count", 0.0))
        local_support = group_count / max(1.0, float(len(context.df_view)))
        significance = max(0.0, float((row["mean"] - global_mean) / (global_std + EPSILON)))
        significance *= max(local_support, EPSILON)
        significance = min(1.0, significance)
        impact = float(context.impact * max(local_support, EPSILON))
        score = float(impact * significance)
        if score <= 0:
            return []
        insight = Insight(
            subject=InsightSubject(subspace=dict(context.subspace), breakdown=context.breakdown or "", measure=context.measure),
            insight_type=self.insight_type,
            impact=float(round(impact, 4)),
            significance=float(round(significance, 4)),
            score=float(round(score, 4)),
            highlight={
                "outlier_category": row["breakdown"],
                "category_mean": round(float(row["mean"]), 4),
                "threshold": round(float(threshold), 4),
                "category_support": round(local_support, 4),
            },
        )
        return [insight]


class TrendEvaluator(BaseInsightEvaluator):
    insight_type = "Trend"

    def can_evaluate(self, context: TaskContext) -> bool:
        if not super().can_evaluate(context):
            return False
        stats = _get_group_stats(context).dropna(subset=["mean"])
        if stats["breakdown"].nunique(dropna=True) < 4:
            return False
        if stats["count"].fillna(0).min() < 3:
            return False
        try:
            parsed = pd.to_datetime(stats["breakdown"], errors="coerce")
            if parsed.notna().all():
                return True
        except Exception:
            pass
        dtype = stats["breakdown"].dtype
        return pd.api.types.is_numeric_dtype(dtype) or pd.api.types.is_datetime64_any_dtype(dtype)

    def evaluate(self, context: TaskContext) -> list[Insight]:
        stats = _get_group_stats(context).dropna(subset=["mean"])
        if stats.empty:
            return []

        # Sort by breakdown with best effort at ordering
        try:
            ordered = stats.assign(_key=pd.to_datetime(stats["breakdown"], errors="coerce"))
            if ordered["_key"].notna().all():
                stats = ordered.sort_values("_key").drop(columns=["_key"]).reset_index(drop=True)
            else:
                stats = stats.sort_values("breakdown").reset_index(drop=True)
        except Exception:
            stats = stats.sort_values("breakdown").reset_index(drop=True)

        y = stats["mean"].to_numpy(dtype=float)
        if np.all(np.isnan(y)):
            return []
        x = np.arange(len(y), dtype=float)

        coeffs = np.polyfit(x, y, deg=1)
        slope = coeffs[0]
        y_pred = slope * x + coeffs[1]
        ss_res = float(np.sum((y - y_pred) ** 2))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2)) if len(y) > 1 else 0.0
        r_squared = 1.0 - ss_res / (ss_tot + EPSILON) if ss_tot > 0 else 0.0
        direction = "increasing" if slope > 0 else "decreasing"

        global_std = float(context.global_stats.stds.get(context.measure, 0.0))
        if not math.isfinite(global_std):
            global_std = 0.0

        slope_norm = abs(slope) / (global_std + EPSILON)
        significance = max(0.0, min(1.0, 0.5 * slope_norm + 0.5 * r_squared))
        score = float(context.impact * significance)

        if score <= 0 or significance < 0.2:
            return []

        insight = Insight(
            subject=InsightSubject(subspace=dict(context.subspace), breakdown=context.breakdown or "", measure=context.measure),
            insight_type=self.insight_type,
            impact=float(round(context.impact, 4)),
            significance=float(round(significance, 4)),
            score=float(round(score, 4)),
            highlight={
                "direction": direction,
                "slope": round(float(slope), 4),
                "r_squared": round(float(r_squared), 4),
            },
        )
        return [insight]


class ChangePointEvaluator(BaseInsightEvaluator):
    insight_type = "ChangePoint"

    def can_evaluate(self, context: TaskContext) -> bool:
        if not super().can_evaluate(context):
            return False
        stats = _get_group_stats(context).dropna(subset=["mean"])
        if len(stats) < 3:
            return False
        if stats["count"].fillna(0).min() < 3:
            return False
        try:
            parsed = pd.to_datetime(stats["breakdown"], errors="coerce")
            if parsed.notna().all():
                return True
        except Exception:
            pass
        dtype = stats["breakdown"].dtype
        return pd.api.types.is_numeric_dtype(dtype) or pd.api.types.is_datetime64_any_dtype(dtype)

    def evaluate(self, context: TaskContext) -> list[Insight]:
        stats = _get_group_stats(context).dropna(subset=["mean"])
        if stats.empty:
            return []

        try:
            ordered = stats.assign(_key=pd.to_datetime(stats["breakdown"], errors="coerce"))
            if ordered["_key"].notna().all():
                stats = ordered.sort_values("_key").drop(columns=["_key"]).reset_index(drop=True)
            else:
                stats = stats.sort_values("breakdown").reset_index(drop=True)
        except Exception:
            stats = stats.sort_values("breakdown").reset_index(drop=True)

        means = stats["mean"].to_numpy(dtype=float)
        if len(means) < 3:
            return []

        diffs = np.abs(np.diff(means))
        if np.all(diffs <= EPSILON):
            return []

        idx = int(np.argmax(diffs))
        change_from = stats.iloc[idx]
        change_to = stats.iloc[idx + 1]
        delta = float(change_to["mean"] - change_from["mean"])
        global_std = float(context.global_stats.stds.get(context.measure, 0.0))

        if not math.isfinite(global_std) or global_std <= EPSILON:
            significance = min(1.0, abs(delta) / (abs(change_from["mean"]) + EPSILON))
        else:
            significance = min(1.0, abs(delta) / (global_std + EPSILON))
        combined_count = float(change_from.get("count", 0.0) + change_to.get("count", 0.0))
        local_support = combined_count / max(1.0, 2.0 * float(len(context.df_view)))
        significance *= max(local_support, EPSILON)
        significance = min(1.0, significance)
        impact = float(context.impact * max(local_support, EPSILON))
        score = float(impact * significance)

        if score <= 0 or significance < 0.2:
            return []

        direction = "up" if delta > 0 else "down"
        insight = Insight(
            subject=InsightSubject(subspace=dict(context.subspace), breakdown=context.breakdown or "", measure=context.measure),
            insight_type=self.insight_type,
            impact=float(round(impact, 4)),
            significance=float(round(significance, 4)),
            score=float(round(score, 4)),
            highlight={
                "change_point_from": change_from["breakdown"],
                "change_point_to": change_to["breakdown"],
                "delta": round(delta, 4),
                "direction": direction,
                "category_support": round(local_support, 4),
            },
        )
        return [insight]


EVALUATORS: tuple[BaseInsightEvaluator, ...] = (
    OutstandingTop1Evaluator(),
    OutlierEvaluator(),
    TrendEvaluator(),
    ChangePointEvaluator(),
)

# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def _load_dataset(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    print(f"[QuickInsights] _load_dataset -> '{path.name}' shape={df.shape}")

    # Drop metadata rows such as "Transform:" that occasionally appear in FRED exports
    if not df.empty and df.iloc[0].astype(str).str.contains("Transform", case=False).any():
        df = df.iloc[1:].reset_index(drop=True)
        print(f"[QuickInsights] Dropped metadata row, new shape={df.shape}")

    iso_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}:\d{2})?$")

    for col in df.columns:
        series = df[col]
        if not pd.api.types.is_object_dtype(series):
            continue

        name_lower = col.lower()
        str_values = series.astype(str).str.strip()
        str_values = str_values.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
        non_null = str_values.dropna()
        if non_null.empty:
            continue

        parsed: pd.Series | None = None

        iso_ratio = non_null.str.match(iso_pattern).mean()
        if iso_ratio >= 0.8:
            strict_parsed = pd.to_datetime(
                str_values,
                format="%Y-%m-%d %H:%M:%S",
                errors="coerce",
            )
            if strict_parsed.notna().mean() >= 0.8:
                parsed = strict_parsed

        if parsed is None and any(token in name_lower for token in ("date", "time", "timestamp", "datetime")):
            loose_parsed = pd.to_datetime(
                str_values,
                errors="coerce",
                dayfirst=False,
                infer_datetime_format=True,
            )
            if loose_parsed.notna().mean() >= 0.8:
                parsed = loose_parsed

        if parsed is not None:
            df[col] = parsed
            print(f"[QuickInsights] Parsed datetime column '{col}'")
            continue

        converted = pd.to_numeric(str_values, errors="coerce")
        if converted.notna().mean() >= 0.9:
            df[col] = converted
            print(f"[QuickInsights] Parsed numeric column '{col}'")

    datetime_cols = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
    if datetime_cols:
        primary = datetime_cols[0]
        print(f"[QuickInsights] Primary datetime column selected: '{primary}'")
        try:
            hpandas.dassert_index_is_datetime(df.set_index(primary))
        except Exception as err:
            print(f"[QuickInsights] Warning: primary datetime column '{primary}' is not a proper datetime index: {err}")
        if "Year" not in df.columns:
            df["Year"] = df[primary].dt.year
        if "Month" not in df.columns:
            df["Month"] = df[primary].dt.month
        if "Quarter" not in df.columns:
            df["Quarter"] = df[primary].dt.quarter
        if "Date" not in df.columns:
            df["Date"] = df[primary].dt.date.astype(str)
        if "Hour" not in df.columns:
            df["Hour"] = df[primary].dt.hour

    # Store the cleaned dataset so downstream tools (e.g., visualisation) can reuse it
    # without having to repeat preprocessing.
    global LAST_NORMALISED_DATASET
    LAST_NORMALISED_DATASET = df.copy()
    print(f"[QuickInsights] Normalised dataset ready shape={df.shape}")

    return df


def _guess_schema(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    """
    Split columns into dimension vs measure according to QuickInsights
    heuristics: numerical columns become measures, categoricals/datetimes
    become dimensions. Datetime strings are expanded into Hour and Date keys.
    """
    dimensions: list[str] = []
    measures: list[str] = []

    for col in df.columns:
        series = df[col]
        if pd.api.types.is_numeric_dtype(series):
            measures.append(col)
            continue

        parsed = None
        if pd.api.types.is_datetime64_any_dtype(series):
            parsed = series
        elif pd.api.types.is_string_dtype(series):
            try:
                parsed = pd.to_datetime(series, errors="raise", dayfirst=True)
            except Exception:
                parsed = None

        if parsed is not None:
            if "Hour" not in df.columns:
                df["Hour"] = parsed.dt.hour
            if "Date" not in df.columns:
                df["Date"] = parsed.dt.date.astype(str)
            if "Year" not in df.columns:
                df["Year"] = parsed.dt.year
            if "Month" not in df.columns:
                df["Month"] = parsed.dt.month
            dimensions.extend([col, "Hour", "Date", "Year", "Month"])
        else:
            nunique = series.nunique(dropna=True)
            if nunique <= max(32, len(series) // 10):
                dimensions.append(col)
            else:
                # High-cardinality, try treating as measure via count
                measures.append(col)

    # Deduplicate while preserving order
    seen = set()
    dim_clean = [c for c in dimensions if not (c in seen or seen.add(c))]
    seen.clear()
    meas_clean = [c for c in measures if not (c in seen or seen.add(c))]
    print(f"[QuickInsights] Schema guess -> dimensions={len(dim_clean)}, measures={len(meas_clean)}")
    return dim_clean, meas_clean


def run_quickinsights(
    df: pd.DataFrame,
    max_insights: int = 10,
    min_support: float = 0.01,
    max_subspace_depth: int = 2,
    max_tasks: int = 500,
    topk_buffer: int = 20,
    functional_dependencies: Optional[Sequence[tuple[Sequence[str] | str, str]]] = None,
    evaluators: Sequence[BaseInsightEvaluator] = EVALUATORS,
) -> List[Insight]:
    """
    Mine high-impact insights using a QuickInsights-inspired workflow.
    """
    if df.empty:
        return []

    dimensions, measures = _guess_schema(df)
    if not measures:
        raise ValueError("No numeric measures detected for QuickInsights.")
    print(f"[QuickInsights] run_quickinsights -> dimensions={len(dimensions)}, measures={len(measures)}")

    global_stats = _compute_global_stats(df, measures)
    auto_fd = _discover_fd_pairs(df, dimensions)
    fd_registry = _merge_fd_registry(auto_fd, functional_dependencies)

    searcher = SubjectSearcher(
        df=df,
        dimensions=dimensions,
        min_support=min_support,
        max_depth=max_subspace_depth,
        max_tasks=max_tasks,
    )
    query_engine = AggregationQueryEngine(df)
    topk = TopKBuffer(capacity=topk_buffer)

    best_by_signature: dict[tuple[str, str, str], Insight] = {}
    evaluated_tasks = 0

    for task in searcher.iter_tasks():
        evaluated_tasks += 1
        if evaluated_tasks % 50 == 0:
            print(f"[QuickInsights] Evaluating task #{evaluated_tasks} subspace={task.subspace} breakdown={task.breakdown}")
        for measure in measures:
            if measure not in df.columns:
                continue

            max_possible_score = float(task.impact)
            if all(topk.should_prune(evaluator.insight_type, max_possible_score) for evaluator in evaluators):
                continue

            payload = query_engine.query(task.subspace, None, task.breakdown, [measure])
            if payload.frame.empty or payload.is_trivial_group():
                continue

            context = TaskContext(
                subspace=dict(task.subspace),
                breakdown=task.breakdown,
                measure=measure,
                impact=task.impact,
                df_view=task.df_view,
                payload=payload,
                global_stats=global_stats,
            )

            if _is_fd_triggered(context.subspace, context.breakdown, fd_registry):
                continue
            if _measure_function_of_breakdown(context):
                continue

            for evaluator in evaluators:
                if topk.should_prune(evaluator.insight_type, max_possible_score):
                    continue
                if not evaluator.can_evaluate(context):
                    continue
                produced = evaluator.evaluate(context)
                if not produced:
                    continue
                for insight in produced:
                    key = (insight.insight_type, insight.subject.breakdown, insight.subject.measure)
                    existing = best_by_signature.get(key)
                    if existing is not None and existing.score >= insight.score:
                        continue
                    best_by_signature[key] = insight
                    topk.record(insight)

    top_insights = sorted(best_by_signature.values(), key=lambda item: (item.score, item.impact), reverse=True)
    print(f"[QuickInsights] Completed mining. Produced {len(top_insights)} candidates, returning top {max_insights}.")
    return top_insights[:max_insights]


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def _to_jsonable(insights: Iterable[Insight]) -> list[dict[str, Any]]:
    return [
        {
            **asdict(insight),
            "subject": asdict(insight.subject),
        }
        for insight in insights
    ]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="QuickInsights-inspired miner.")
    parser.add_argument("--path", type=Path, required=True, help="Path to CSV file.")
    parser.add_argument("--max-insights", type=int, default=10)
    parser.add_argument("--json-out", type=Path, help="Optional path to dump JSON insights.")
    args = parser.parse_args(argv)

    df = _load_dataset(args.path)
    insights = run_quickinsights(df, max_insights=args.max_insights)

    jsonable = _to_jsonable(insights)
    print(json.dumps(jsonable, indent=2, default=float))

    if args.json_out:
        args.json_out.write_text(json.dumps(jsonable, indent=2, default=float))


if __name__ == "__main__":
    main()
