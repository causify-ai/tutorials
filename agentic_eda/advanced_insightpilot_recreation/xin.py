"""
XInsight-inspired explanation engine.

This module implements a pragmatic version of the SIGMOD'23 XInsight workflow
tailored to tabular CSV data. Given a Why Query (two sibling subspaces whose
aggregation differs), it surfaces causal-style predicates that explain the gap.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Iterable, Sequence

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

import helpers.hpandas as hpandas


@dataclass
class Explanation:
    variable: str
    kind: str  # "causal" or "non_causal"
    qualitative: str
    quantitative: dict[str, Any]


@dataclass(frozen=True)
class Predicate:
    variable: str
    kind: str
    params: tuple[Any, ...]

    def mask(self, df: pd.DataFrame) -> pd.Series:
        series = df[self.variable]
        if self.kind == "eq":
            value = self.params[0]
            return series.astype(str) == str(value)
        if self.kind == "ge":
            threshold = float(self.params[0])
            return pd.to_numeric(series, errors="coerce") >= threshold
        if self.kind == "le":
            threshold = float(self.params[0])
            return pd.to_numeric(series, errors="coerce") <= threshold
        if self.kind == "between":
            lower, upper = map(float, self.params)
            numeric = pd.to_numeric(series, errors="coerce")
            return (numeric >= lower) & (numeric <= upper)
        raise ValueError(f"Unsupported predicate kind '{self.kind}'")

    def describe(self) -> str:
        if self.kind == "eq":
            return f"{self.variable} == {self.params[0]}"
        if self.kind == "ge":
            return f"{self.variable} >= {self.params[0]:.4f}"
        if self.kind == "le":
            return f"{self.variable} <= {self.params[0]:.4f}"
        if self.kind == "between":
            return f"{self.variable} between {self.params[0]:.4f} and {self.params[1]:.4f}"
        return f"{self.variable} {self.kind} {self.params}"


@dataclass
class PredicateOutcome:
    predicate: Predicate
    delta_after: float
    reduction: float
    subset_delta: float


@dataclass
class VariableContext:
    variable: str
    causal_label: str
    predicates: list[Predicate] = field(default_factory=list)


@dataclass
class WhyQuery:
    measure: str
    dimension: str
    left_value: Any
    right_value: Any
    agg: str
    epsilon: float = 1e-3
    sigma: float = 0.2


def _aggregate(df: pd.DataFrame, measure: str, agg: str) -> float:
    if measure not in df.columns:
        series = pd.Series(dtype=float)
    else:
        series = hpandas.as_series(df[[measure]])
        series = pd.to_numeric(series, errors="coerce")
    if agg.lower() in {"avg", "mean"}:
        return float(series.mean(skipna=True))
    if agg.lower() == "sum":
        return float(series.sum(skipna=True))
    raise ValueError(f"Unsupported aggregation: {agg}")


def _filter(df: pd.DataFrame, filters: dict[str, Any]) -> pd.DataFrame:
    subset = df
    for col, value in filters.items():
        if col not in subset.columns:
            raise ValueError(f"Column '{col}' not found in dataset.")
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


def _encode_column(series: pd.Series) -> np.ndarray:
    if pd.api.types.is_numeric_dtype(series):
        numeric = pd.to_numeric(series, errors="coerce")
        if numeric.isna().all():
            return np.zeros(len(series))
        mean = numeric.mean()
        fill_value = 0.0 if np.isnan(mean) else float(mean)
        return numeric.fillna(fill_value).to_numpy()
    encoder = LabelEncoder()
    return encoder.fit_transform(series.astype(str).fillna("nan"))


def _partial_corr(df: pd.DataFrame, x: str, y: str, control: str) -> float:
    try:
        x_vec = _encode_column(df[x])
        y_vec = _encode_column(df[y])
        z_vec = _encode_column(df[control])
    except Exception:
        return 0.0
    z_aug = np.column_stack([np.ones(len(z_vec)), z_vec])
    try:
        beta_x = np.linalg.lstsq(z_aug, x_vec, rcond=None)[0]
        beta_y = np.linalg.lstsq(z_aug, y_vec, rcond=None)[0]
    except np.linalg.LinAlgError:
        return 0.0
    resid_x = x_vec - z_aug @ beta_x
    resid_y = y_vec - z_aug @ beta_y
    if np.std(resid_x) < 1e-9 or np.std(resid_y) < 1e-9:
        return 0.0
    corr = np.corrcoef(resid_x, resid_y)[0, 1]
    if np.isnan(corr):
        return 0.0
    return float(corr)


def _delta(df: pd.DataFrame, query: WhyQuery) -> float:
    left_df = _filter(df, {query.dimension: query.left_value})
    right_df = _filter(df, {query.dimension: query.right_value})
    if left_df.empty or right_df.empty:
        return 0.0
    try:
        left_metric = _aggregate(left_df, query.measure, query.agg)
        right_metric = _aggregate(right_df, query.measure, query.agg)
    except ValueError:
        return 0.0
    if np.isnan(left_metric) or np.isnan(right_metric):
        return 0.0
    return float(left_metric - right_metric)


def _generate_predicates(df: pd.DataFrame, variable: str, max_bins: int = 4) -> list[Predicate]:
    series = df[variable]
    predicates: list[Predicate] = []
    if pd.api.types.is_numeric_dtype(series):
        numeric = pd.to_numeric(series, errors="coerce").dropna()
        if numeric.empty:
            return predicates
        quantiles = np.unique(
            np.clip(numeric.quantile(np.linspace(0.2, 0.8, max_bins)).to_numpy(), numeric.min(), numeric.max())
        )
        for value in quantiles:
            predicates.append(Predicate(variable, "ge", (float(value),)))
            predicates.append(Predicate(variable, "le", (float(value),)))
        if len(quantiles) >= 2:
            for lower, upper in zip(quantiles[:-1], quantiles[1:]):
                if upper - lower > 1e-9:
                    predicates.append(Predicate(variable, "between", (float(lower), float(upper))))
    else:
        counts = series.astype(str).value_counts()
        for value in counts.index[: max_bins * 2]:
            predicates.append(Predicate(variable, "eq", (value,)))
    return predicates


def _remove_predicates(df: pd.DataFrame, predicates: Sequence[Predicate]) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)
    for predicate in predicates:
        mask &= ~predicate.mask(df)
    return df[mask]


def _score_predicate(
    df: pd.DataFrame,
    predicate: Predicate,
    query: WhyQuery,
    base_delta: float,
) -> PredicateOutcome | None:
    reduced_df = _remove_predicates(df, [predicate])
    delta_removed = _delta(reduced_df, query)
    reduction = abs(base_delta) - abs(delta_removed)
    subset_df = df[predicate.mask(df)]
    subset_delta = _delta(subset_df, query)
    if np.isnan(reduction):
        return None
    return PredicateOutcome(predicate, float(delta_removed), float(reduction), float(subset_delta))


def _greedy_cover(
    df: pd.DataFrame,
    predicate_outcomes: list[PredicateOutcome],
    query: WhyQuery,
    base_delta: float,
) -> tuple[list[PredicateOutcome], float]:
    remaining = predicate_outcomes.copy()
    selected: list[PredicateOutcome] = []
    working_df = df
    current_delta = base_delta
    max_size = max(1, min(len(remaining), int(1 / max(query.sigma, 1e-3))))

    for _ in range(max_size):
        if abs(current_delta) <= query.epsilon or not remaining:
            break
        best: PredicateOutcome | None = None
        best_delta: float | None = None
        for outcome in remaining:
            candidate_df = _remove_predicates(working_df, [outcome.predicate])
            candidate_delta = _delta(candidate_df, query)
            if best is None or abs(candidate_delta) < abs(best_delta):   # type: ignore[arg-type]
                best = outcome
                best_delta = candidate_delta
        if best is None:
            break
        selected.append(best)
        working_df = _remove_predicates(working_df, [best.predicate])
        current_delta = _delta(working_df, query)
        remaining = [out for out in remaining if out.predicate != best.predicate]

    return selected, float(current_delta)


def _contingency_effect(
    df: pd.DataFrame,
    query: WhyQuery,
    predicate_set: Sequence[Predicate],
    contingency: Sequence[Predicate],
) -> float:
    without_predicates = _remove_predicates(df, predicate_set)
    delta_without = _delta(without_predicates, query)
    without_both = _remove_predicates(df, list(predicate_set) + list(contingency))
    delta_without_both = _delta(without_both, query)
    return abs(delta_without) - abs(delta_without_both)


def _evaluate_variable(
    df: pd.DataFrame,
    query: WhyQuery,
    base_delta: float,
    predicate_outcomes: list[PredicateOutcome],
) -> tuple[list[Predicate], float, float] | None:
    if not predicate_outcomes:
        return None
    greedy_selected, _ = _greedy_cover(df, predicate_outcomes, query, base_delta)
    if not greedy_selected:
        return None

    predicate_list = [outcome.predicate for outcome in greedy_selected]
    best_score = -np.inf
    best_subset: list[Predicate] | None = None
    best_delta = base_delta

    for k in range(1, len(predicate_list) + 1):
        subset = predicate_list[:k]
        contingency = [pred for pred in predicate_list if pred not in subset]
        diff = _contingency_effect(df, query, subset, contingency)
        rho_hat = max(diff / (abs(base_delta) + 1e-9), 0.0)
        score = rho_hat - query.sigma * len(subset)
        if score > best_score:
            best_score = score
            best_subset = subset
            best_delta = _delta(_remove_predicates(df, subset), query)

    if best_subset is None:
        return None
    return best_subset, float(best_delta), float(best_score)


def _build_variable_contexts(
    df: pd.DataFrame,
    query: WhyQuery,
    candidate_variables: Sequence[str],
) -> dict[str, VariableContext]:
    contexts: dict[str, VariableContext] = {}
    for var in candidate_variables:
        if var in {query.dimension, query.measure}:
            continue
        partial = _partial_corr(df, var, query.measure, query.dimension)
        causal_label = "causal" if abs(partial) >= 0.1 else "non_causal"
        contexts[var] = VariableContext(variable=var, causal_label=causal_label)
    return contexts


def explain_difference(
    df: pd.DataFrame,
    dimension: str,
    left_value: Any,
    right_value: Any,
    measure: str,
    agg: str = "avg",
) -> list[Explanation]:
    print(
        f"[XInsight] explain_difference -> dimension={dimension}, left={left_value}, right={right_value}, "
        f"measure={measure}, agg={agg}, df shape={df.shape}"
    )
    base_left = _filter(df, {dimension: left_value})
    base_right = _filter(df, {dimension: right_value})

    if base_left.empty or base_right.empty:
        raise ValueError("Why Query produced empty subspace.")

    query = WhyQuery(
        measure=measure,
        dimension=dimension,
        left_value=left_value,
        right_value=right_value,
        agg=agg,
    )

    base_delta = _delta(df, query)
    print(f"[XInsight] Base delta={base_delta:.4f}")
    candidate_vars = [col for col in df.columns if col not in {dimension, measure}]
    print(f"[XInsight] Candidate variables: {len(candidate_vars)}")
    contexts = _build_variable_contexts(df, query, candidate_vars)

    explanations: list[Explanation] = []

    for var, context in contexts.items():
        predicates = _generate_predicates(df, var)
        predicate_outcomes: list[PredicateOutcome] = []
        for predicate in predicates:
            outcome = _score_predicate(df, predicate, query, base_delta)
            if outcome is None or outcome.reduction <= 0:
                continue
            predicate_outcomes.append(outcome)
        contexts[var].predicates = [outcome.predicate for outcome in predicate_outcomes]
        evaluation = _evaluate_variable(df, query, base_delta, predicate_outcomes)
        if evaluation is None:
            continue
        subset, delta_after, score = evaluation
        print(f"[XInsight] Variable '{var}' -> subset size={len(subset)}, delta_after={delta_after:.4f}, score={score:.4f}")
        if not subset:
            continue
        responsibility = max(0.0, min(1.0, (abs(base_delta) - abs(delta_after)) / (abs(base_delta) + 1e-9)))
        predicate_text = " AND ".join(pred.describe() for pred in subset)
        qualitative = (
            f"{var} contributes to the gap on {measure}; conditioning on {predicate_text} "
            f"shrinks the difference from {base_delta:.4f} to {delta_after:.4f}."
        )
        quantitative = {
            "predicate": predicate_text,
            "responsibility": round(float(responsibility), 4),
            "delta_effect": {
                "overall_difference": round(float(base_delta), 4),
                "conditioned_difference": round(float(delta_after), 4),
            },
            "score": round(float(score), 4),
        }
        explanations.append(
            Explanation(
                variable=var,
                kind=context.causal_label,
                qualitative=qualitative,
                quantitative=quantitative,
            )
        )

    explanations.sort(
        key=lambda exp: (
            exp.quantitative.get("responsibility", 0.0),
            -abs(exp.quantitative["delta_effect"]["conditioned_difference"]),
        ),
        reverse=True,
    )
    return explanations[:5]


def _jsonable(explanations: Iterable[Explanation]) -> list[dict[str, Any]]:
    return [asdict(exp) for exp in explanations]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="XInsight-inspired explainer.")
    parser.add_argument("--path", type=Path, required=True)
    parser.add_argument("--dimension", required=True, help="Dimension to split on.")
    parser.add_argument("--left", required=True, help="Left value.")
    parser.add_argument("--right", required=True, help="Right value.")
    parser.add_argument("--measure", required=True, help="Measure column.")
    parser.add_argument("--agg", default="avg")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args(argv)

    df = pd.read_csv(args.path)
    explanations = explain_difference(
        df,
        dimension=args.dimension,
        left_value=args.left,
        right_value=args.right,
        measure=args.measure,
        agg=args.agg,
    )
    payload = _jsonable(explanations)
    print(json.dumps(payload, indent=2, default=float))

    if args.json_out:
        args.json_out.write_text(json.dumps(payload, indent=2, default=float))


if __name__ == "__main__":
    main()
