"""
MetaInsight-style structured knowledge extraction.

This module consumes a CSV dataset (and optionally pre-computed basic insights)
to summarise homogeneous data scopes into commonnesses and exceptions, closely
following the ideas from the SIGMOD'21 MetaInsight paper.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict, field
from math import log
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import pandas as pd

try:
    import agentic_eda.advanced_insightpilot_recreation.qin as qin_module
except ModuleNotFoundError:  # pragma: no cover - fallback
    import qin as qin_module  # type: ignore

Insight = qin_module.Insight  # reuse definition


@dataclass(frozen=True)
class DataScope:
    subspace: tuple[tuple[str, Any], ...]
    breakdown: str
    measure: str

    @staticmethod
    def from_insight(insight: Insight) -> "DataScope":
        sub_items = tuple(sorted(insight.subject.subspace.items()))
        return DataScope(sub_items, insight.subject.breakdown, insight.subject.measure)

    def subspace_dict(self) -> dict[str, Any]:
        return dict(self.subspace)


@dataclass
class PatternResult:
    pattern_type: str
    highlight: dict[str, Any]
    support_members: list[dict[str, Any]]
    support_weight: float
    score: float


@dataclass
class Commonness:
    type: str
    highlight: dict[str, Any]
    support_ratio: float
    members: list[dict[str, Any]]


@dataclass
class MetaInsight:
    homogeneous_scope: dict[str, Any]
    commonnesses: list[Commonness]
    exceptions: dict[str, list[dict[str, Any]]]
    scores: dict[str, float]


class PatternEvaluator:
    pattern_type: str = ""

    def evaluate(self, grouped: pd.DataFrame, dimension: str, measure: str) -> PatternResult | None:
        raise NotImplementedError


class TrendEvaluator(PatternEvaluator):
    pattern_type = "Trend"

    def evaluate(self, grouped: pd.DataFrame, dimension: str, measure: str) -> PatternResult | None:
        if len(grouped) < 3:
            return None
        index = grouped.index
        try:
            if np.issubdtype(index.dtype, np.number):
                order = np.argsort(index)
            elif np.issubdtype(index.dtype, np.datetime64):
                order = np.argsort(index)
            else:
                order = np.argsort(index.astype(str))
        except Exception:
            order = np.arange(len(index))

        means = grouped["mean"].to_numpy()[order]
        counts = grouped["count"].to_numpy()[order]
        if len(means) < 3:
            return None

        diff = np.diff(means)
        tol = np.std(means) * 0.05 + 1e-9
        inc = np.all(diff >= -tol)
        dec = np.all(diff <= tol)
        if not inc and not dec:
            return None

        direction = "increasing" if inc and not dec else "decreasing"
        x = np.arange(len(means))
        corr = np.corrcoef(x, means)[0, 1]
        slope = (means[-1] - means[0]) / max(len(means) - 1, 1)

        members = []
        for idx, row in grouped.iterrows():
            members.append({dimension: idx, "mean": round(float(row["mean"]), 4), "count": int(row["count"])})

        highlight = {
            "pattern": "Trend",
            "direction": direction,
            "slope": round(float(slope), 6),
            "support_categories": [members[i][dimension] for i in range(len(members))],
        }

        return PatternResult(
            pattern_type="TrendUp" if direction == "increasing" else "TrendDown",
            highlight=highlight,
            support_members=members,
            support_weight=float(grouped["count"].sum()),
            score=float(abs(corr)),
        )


class UnimodalityEvaluator(PatternEvaluator):
    pattern_type = "Unimodality"

    def evaluate(self, grouped: pd.DataFrame, dimension: str, measure: str) -> PatternResult | None:
        if grouped.empty:
            return None
        means = grouped["mean"]
        peak_category = means.idxmax()
        peak_mean = float(means.loc[peak_category])
        if peak_mean == 0:
            return None
        members = []
        support_members = []
        support_weight = 0.0
        for idx, row in grouped.iterrows():
            entry = {dimension: idx, "mean": round(float(row["mean"]), 4), "count": int(row["count"])}
            members.append(entry)
            if float(row["mean"]) >= peak_mean * 0.9:
                support_members.append(entry)
                support_weight += float(row["count"])
        if not support_members:
            support_members.append({dimension: peak_category, "mean": round(peak_mean, 4), "count": int(grouped.loc[peak_category, "count"])})
            support_weight = float(grouped.loc[peak_category, "count"])

        highlight = {
            "pattern": "Unimodality",
            "peak_category": peak_category,
            "peak_mean": round(peak_mean, 4),
            "support_categories": [m[dimension] for m in support_members],
        }

        return PatternResult(
            pattern_type="UnimodalityPeak",
            highlight=highlight,
            support_members=support_members,
            support_weight=support_weight,
            score=float(peak_mean),
        )


class OutlierEvaluator(PatternEvaluator):
    pattern_type = "Outlier"

    def evaluate(self, grouped: pd.DataFrame, dimension: str, measure: str) -> PatternResult | None:
        total_weight = grouped["count"].sum()
        if total_weight == 0:
            return None
        weighted_mean = float((grouped["mean"] * grouped["count"]).sum() / total_weight)
        variance = float(((grouped["mean"] - weighted_mean) ** 2 * grouped["count"]).sum() / total_weight)
        std = float(np.sqrt(max(variance, 0.0)))
        if std == 0:
            return None
        support_members: list[dict[str, Any]] = []
        support_weight = 0.0
        zscores: list[float] = []
        for idx, row in grouped.iterrows():
            delta = float(row["mean"]) - weighted_mean
            if abs(delta) >= std:
                entry = {dimension: idx, "mean": round(float(row["mean"]), 4), "count": int(row["count"])}
                support_members.append(entry)
                support_weight += float(row["count"])
                zscores.append(abs(delta) / std)
        if not support_members:
            return None
        highlight = {
            "pattern": "Outlier",
            "threshold": round(weighted_mean + std, 4),
            "support_categories": [m[dimension] for m in support_members],
        }
        score = float(np.mean(zscores)) if zscores else 0.0
        return PatternResult(
            pattern_type="Outlier",
            highlight=highlight,
            support_members=support_members,
            support_weight=support_weight,
            score=score,
        )


PATTERN_EVALUATORS: tuple[PatternEvaluator, ...] = (
    TrendEvaluator(),
    UnimodalityEvaluator(),
    OutlierEvaluator(),
)


def _ensure_insights(df: pd.DataFrame, insights: Sequence[Insight] | None) -> list[Insight]:
    if insights is not None:
        return list(insights)
    from .qin import run_quickinsights  # lazy import to avoid circular

    return run_quickinsights(df, max_insights=20)


def _apply_subspace(df: pd.DataFrame, subspace: tuple[tuple[str, Any], ...]) -> pd.DataFrame:
    subset = df
    for col, value in subspace:
        if col not in subset.columns:
            return subset.iloc[0:0]
        series = subset[col]
        comp_value = value
        if pd.api.types.is_numeric_dtype(series):
            comp_value = pd.to_numeric([value], errors="coerce")[0]
        elif pd.api.types.is_datetime64_any_dtype(series):
            comp_value = pd.to_datetime(value, errors="coerce")
        mask = series == comp_value
        if mask.sum() == 0:
            mask = series.astype(str) == str(value)
        subset = subset[mask]
    return subset


def _scopes_from_insights(insights: Sequence[Insight]) -> list[DataScope]:
    scopes: set[DataScope] = set()
    for ins in insights:
        if not ins.subject.measure or not ins.subject.breakdown:
            continue
        scopes.add(DataScope.from_insight(ins))
    return list(scopes)


def _exceptions_dict() -> dict[str, list[dict[str, Any]]]:
    return {
        "HighlightChange": [],
        "TypeChange": [],
        "NoPattern": [],
    }


def _entropy(counts: list[float]) -> float:
    total = sum(counts)
    if total <= 0:
        return 0.0
    probs = [c / total for c in counts if c > 0]
    if not probs:
        return 0.0
    return -sum(p * log(p) for p in probs)


def _evaluate_scope(
    df: pd.DataFrame,
    scope: DataScope,
    tau: float,
) -> list[MetaInsight]:
    df_scope = _apply_subspace(df, scope.subspace)
    if df_scope.empty:
        return []
    grouped = df_scope.groupby(scope.breakdown)[scope.measure].agg(["mean", "count"])
    if len(grouped) < 2:
        return []

    results: list[MetaInsight] = []
    total_weight = float(grouped["count"].sum())
    global_mean = float((grouped["mean"] * grouped["count"]).sum() / total_weight)
    variance = float(((grouped["mean"] - global_mean) ** 2 * grouped["count"]).sum() / total_weight)
    global_std = float(np.sqrt(max(variance, 0.0)))

    for evaluator in PATTERN_EVALUATORS:
        pattern = evaluator.evaluate(grouped, scope.breakdown, scope.measure)
        if pattern is None or pattern.support_weight <= 0:
            continue
        support_weight = float(pattern.support_weight)
        support_ratio = support_weight / total_weight if total_weight else 0.0
        if support_ratio < tau:
            continue

        support_categories = {member[scope.breakdown] for member in pattern.support_members}
        exceptions = _exceptions_dict()
        total_exception_weight = 0.0
        for idx, row in grouped.iterrows():
            if idx in support_categories:
                continue
            entry = {scope.breakdown: idx, "mean": round(float(row["mean"]), 4), "count": int(row["count"]) }
            deviation = float(row["mean"]) - global_mean
            if abs(deviation) <= max(global_std * 0.5, 1e-9):
                bucket = "HighlightChange"
            elif global_std > 0 and abs(deviation) >= global_std:
                bucket = "TypeChange"
            else:
                bucket = "NoPattern"
            total_exception_weight += float(row["count"])
            exceptions[bucket].append(entry)

        counts = [support_weight]
        exception_totals = {key: sum(item["count"] for item in value) for key, value in exceptions.items() if value}
        counts.extend(exception_totals.values())

        S = _entropy(counts)
        k = len([c for c in counts if c > 0])
        S_star = log(k) if k > 1 else 1.0
        gamma = 0.1
        I = 1.0 if total_exception_weight <= 0 else 0.0
        conciseness = 1.0 - (S / S_star if S_star > 0 else 0.0) - gamma * I
        conciseness = float(max(0.0, min(1.0, conciseness)))
        impact = float(total_weight / len(df)) if len(df) else 0.0
        score_total = float(max(0.0, impact * conciseness))

        highlight = dict(pattern.highlight)
        highlight["support_ratio"] = round(float(support_ratio), 4)
        highlight["measure"] = scope.measure

        commonness = Commonness(
            type=pattern.pattern_type,
            highlight=highlight,
            support_ratio=round(float(support_ratio), 4),
            members=pattern.support_members,
        )

        meta = MetaInsight(
            homogeneous_scope={
                "root_scope": {
                    "subspace": scope.subspace_dict(),
                    "breakdown": scope.breakdown,
                    "measure": scope.measure,
                },
                "extension": f"{scope.breakdown} ⊕ {pattern.pattern_type}",
            },
            commonnesses=[commonness],
            exceptions=exceptions,
            scores={
                "impact": round(impact, 4),
                "conciseness": round(conciseness, 4),
                "total": round(score_total, 4),
            },
        )
        results.append(meta)

    return results


def generate_meta_insights(
    df: pd.DataFrame,
    base_insights: Sequence[Insight] | None = None,
    tau: float = 0.5,
) -> list[MetaInsight]:
    print(f"[MetaInsight] generate_meta_insights -> df shape={df.shape}, base_insights={len(base_insights or [])}, tau={tau}")
    insights = _ensure_insights(df, base_insights)
    scopes = _scopes_from_insights(insights)
    print(f"[MetaInsight] Candidate scopes: {len(scopes)}")
    metas: list[MetaInsight] = []

    for scope in scopes:
        print(f"[MetaInsight] Evaluating scope measure={scope.measure} breakdown={scope.breakdown} subspace={scope.subspace}")
        if scope.measure not in df.columns or scope.breakdown not in df.columns:
            print("[MetaInsight] -> skipped (columns missing)")
            continue
        metas.extend(_evaluate_scope(df, scope, tau))

    metas.sort(key=lambda m: m.scores.get("total", 0.0), reverse=True)
    print(f"[MetaInsight] Produced {len(metas)} meta insights")
    return metas


def _jsonable(meta: MetaInsight) -> dict[str, Any]:
    return {
        "homogeneous_scope": meta.homogeneous_scope,
        "commonnesses": [
            {
                **asdict(common),
                "support_ratio": float(common.support_ratio),
            }
            for common in meta.commonnesses
        ],
        "exceptions": meta.exceptions,
        "scores": meta.scores,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="MetaInsight-inspired summariser.")
    parser.add_argument("--path", type=Path, required=True)
    parser.add_argument("--tau", type=float, default=0.5)
    parser.add_argument("--json-out", type=Path, help="Optional JSON dump.")
    args = parser.parse_args(argv)

    df = pd.read_csv(args.path)
    metas = generate_meta_insights(df, tau=args.tau)
    payload = [_jsonable(meta) for meta in metas]
    print(json.dumps(payload, indent=2, default=float))

    if args.json_out:
        args.json_out.write_text(json.dumps(payload, indent=2, default=float))


if __name__ == "__main__":
    main()
