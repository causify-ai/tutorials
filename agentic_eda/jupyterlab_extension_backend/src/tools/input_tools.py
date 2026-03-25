"""
Import as:

import src.tools.input_tools as tinptool
"""

import json
import itertools
import pathlib
import re
from typing import Any

import langchain.tools as ltools
import numpy as np
import pandas as pd
import pydantic

_VALID_HEADER_START_RE = re.compile(r"^[A-Za-z_]")


def _trace_root() -> pathlib.Path:
    """
    Return the backend-level trace directory.

    :return: absolute trace root
    """
    trace_root = pathlib.Path(__file__).resolve().parents[2] / "traces"
    trace_root.mkdir(parents=True, exist_ok=True)
    return trace_root


def load_dataset(path: pathlib.Path) -> pd.DataFrame:
    """
    Load a supported dataset from disk.

    :param path: path to dataset file
    :return: dataset as dataframe
    """
    ext = path.suffix.lower()
    if ext == ".csv":
        dataset = pd.read_csv(path)
    else:
        raise ValueError(f"Unsupported file extension='{ext}'")
    return dataset


def _sample_values(series: pd.Series, *, limit: int = 5) -> list[str]:
    """
    Return a small deterministic sample of distinct non-null values.

    Theory:
    A short value sample gives downstream logic human-interpretable evidence
    about whether a column behaves like a flag, identifier, category, or
    free-form measurement, without depending on the column name alone.

    :param series: input series
    :param limit: max number of sample values
    :return: stringified sample values
    """
    values: list[str] = []
    seen: set[str] = set()
    for value in series.dropna().tolist():
        key = str(value)
        if key in seen:
            continue
        seen.add(key)
        values.append(key)
        if len(values) >= limit:
            break
    return values


def _normalized_non_null_fraction(series: pd.Series) -> float:
    """
    Compute the non-null fraction for a series.

    Theory:
    Missingness changes how much confidence we should place in any inferred
    semantic role. Columns with very little observed data provide weak evidence
    for type inference, so completeness is a foundational statistic.

    :param series: input series
    :return: non-null fraction
    """
    if len(series) == 0:
        return 0.0
    return float(series.notna().mean())


def _coerce_numeric(series: pd.Series) -> pd.Series:
    """
    Convert a series to numeric values where possible.

    Theory:
    Many semantic distinctions begin with whether values actually behave like
    numbers in the data, not whether the declared dtype says so. Numeric
    coercion exposes columns that are numerically meaningful even when loaded
    as strings.

    :param series: input series
    :return: numeric series with NaN for non-numeric values
    """
    return pd.to_numeric(series, errors="coerce")


def _is_integer_like(series: pd.Series) -> bool:
    """
    Check whether numeric values are effectively integers.

    Theory:
    Count variables and encoded flags often live on the integers, whereas
    continuous measurements usually do not. Integer support is therefore a
    useful deterministic signal for separating counts from continuous values.

    :param series: numeric-like series
    :return: true when all observed values are close to integers
    """
    numeric = _coerce_numeric(series).dropna()
    if numeric.empty:
        return False
    rounded = numeric.round()
    return bool((numeric - rounded).abs().le(1e-9).all())


def _is_binary_like(series: pd.Series) -> bool:
    """
    Check whether a column behaves like a binary flag.

    Theory:
    Binary indicators are characterized by two logical states regardless of
    whether they are stored as booleans, strings, or numeric codes. Recognizing
    this two-state support helps prevent flags from being misclassified as
    general categoricals or counts.

    :param series: input series
    :return: true when the column has exactly two logical states
    """
    non_null = series.dropna()
    if non_null.empty:
        return False
    unique_raw = {str(value).strip().lower() for value in non_null.unique()}
    binary_vocab = {
        "0",
        "1",
        "true",
        "false",
        "t",
        "f",
        "yes",
        "no",
        "y",
        "n",
    }
    if unique_raw and unique_raw.issubset(binary_vocab) and len(unique_raw) <= 2:
        return True
    return len(unique_raw) == 2


def _build_column_profiles(dataset: pd.DataFrame) -> dict[str, dict[str, Any]]:
    """
    Build deterministic per-column profiles used by downstream schema tools.

    Theory:
    Robust schema inference should summarize how each column behaves in the
    observed data: completeness, cardinality, numeric support, integer support,
    binary support, and value examples. Those empirical signals are what later
    stages use to infer keys and semantic feature types in a reproducible way.

    :param dataset: input dataframe
    :return: map of column name to summary statistics
    """
    profiles: dict[str, dict[str, Any]] = {}
    n_rows = int(dataset.shape[0])
    for col in dataset.columns:
        series = dataset[col]
        non_null = series.dropna()
        n_non_null = int(non_null.shape[0])
        n_unique = int(non_null.nunique(dropna=True))
        unique_ratio = 0.0 if n_non_null == 0 else float(n_unique / n_non_null)
        numeric = _coerce_numeric(series)
        numeric_non_null = numeric.dropna()
        numeric_fraction = (
            0.0 if n_non_null == 0 else float(numeric_non_null.shape[0] / n_non_null)
        )
        integer_like = _is_integer_like(series)
        nonnegative_like = (
            False
            if numeric_non_null.empty
            else bool((numeric_non_null >= 0).all())
        )
        profile = {
            "dtype": str(series.dtype),
            "n_rows": n_rows,
            "n_non_null": n_non_null,
            "non_null_fraction": _normalized_non_null_fraction(series),
            "n_unique": n_unique,
            "unique_ratio": unique_ratio,
            "is_numeric_like": bool(numeric_fraction >= 0.95 and not numeric_non_null.empty),
            "numeric_fraction": numeric_fraction,
            "is_integer_like": integer_like,
            "is_binary_like": _is_binary_like(series),
            "is_nonnegative_like": nonnegative_like,
            "sample_values": _sample_values(series),
        }
        if not numeric_non_null.empty:
            profile["min_numeric"] = float(numeric_non_null.min())
            profile["max_numeric"] = float(numeric_non_null.max())
        else:
            profile["min_numeric"] = None
            profile["max_numeric"] = None
        profiles[str(col)] = profile
    return profiles


def write_stage_trace(path: str, stage: str, payload: dict[str, Any]) -> str:
    """
    Persist diagnostic findings for one pipeline stage to a backend-local trace
    file.

    :param path: dataset path
    :param stage: pipeline stage name
    :param payload: JSON-serializable diagnostic payload
    :return: absolute trace file path
    """
    dataset_path = pathlib.Path(path)
    filename = f"{dataset_path.stem}.{stage}.json"
    trace_path = _trace_root() / filename
    trace_payload = {
        "dataset_path": str(dataset_path),
        "stage": stage,
        "payload": payload,
    }
    trace_path.write_text(
        json.dumps(trace_payload, default=str, indent=2),
        encoding="utf-8",
    )
    return str(trace_path)


def write_stage_dataset(path: str, stage: str, dataset: pd.DataFrame) -> str:
    """
    Persist a stage-produced dataset artifact alongside trace files.

    :param path: source dataset path
    :param stage: pipeline stage name
    :param dataset: dataframe to serialize
    :return: absolute output dataset path
    """
    dataset_path = pathlib.Path(path)
    filename = f"{dataset_path.stem}.{stage}.csv"
    output_path = _trace_root() / filename
    dataset.to_csv(output_path, index=False)
    return str(output_path)


def write_stage_plot(path: str, stage: str, plot_name: str, fig: Any) -> str:
    """
    Persist a stage-produced plot under the backend trace directory.

    :param path: source dataset path
    :param stage: pipeline stage name
    :param plot_name: plot-specific filename stem
    :param fig: matplotlib figure
    :return: absolute output plot path
    """
    dataset_path = pathlib.Path(path)
    plot_dir = _trace_root() / f"{dataset_path.stem}.{stage}"
    plot_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", plot_name).strip("_")
    if not safe_name:
        safe_name = "plot"
    output_path = plot_dir / f"{safe_name}.png"
    fig.savefig(output_path, dpi=140, bbox_inches="tight")
    return str(output_path)


def _parse_time_series(
    dataset: pd.DataFrame,
    time_col: str,
    winner_formatter: dict[str, Any] | None = None,
) -> pd.Series:
    """
    Parse the selected time column with the best-known formatter settings.

    Theory:
    Temporal statistics are only meaningful once the time axis has been mapped
    into a consistent datetime representation. Reusing the formatter selected
    earlier in the pipeline avoids accidental drift between schema inference and
    downstream coverage/frequency calculations.

    :param dataset: input dataframe
    :param time_col: selected time column
    :param winner_formatter: optional datetime parsing kwargs
    :return: parsed timestamp series
    """
    format_args = winner_formatter or {}
    format_args = {key: val for key, val in format_args.items() if val is not None}
    try:
        return pd.to_datetime(dataset[time_col], errors="coerce", **format_args)
    except Exception:
        return pd.to_datetime(dataset[time_col], errors="coerce")


def _format_timedelta(delta: pd.Timedelta | None) -> str | None:
    """
    Convert a timedelta into a stable string representation.

    Theory:
    Frequency and gap summaries are easier to compare across stages when they
    are rendered into a canonical textual duration rather than leaking pandas-
    specific objects into the public payload.

    :param delta: input timedelta
    :return: normalized string or None
    """
    if delta is None or pd.isna(delta):
        return None
    return str(delta)


def _series_identifier(keys: list[str], values: tuple[Any, ...]) -> dict[str, Any] | None:
    """
    Package one composite entity identifier as a JSON-friendly mapping.

    Theory:
    Coverage and frequency statistics are naturally computed per series. When a
    panel uses composite entity keys, the identifier must preserve every key
    component so the reported findings still point back to the original series.

    :param keys: entity key column names
    :param values: grouped key values
    :return: key-value mapping or None for single-series data
    """
    if not keys:
        return None
    return {key: value for key, value in zip(keys, values, strict=True)}


def _ordered_dataset(
    dataset: pd.DataFrame,
    time_col: str,
    secondary_keys: list[str] | None = None,
    winner_formatter: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Return a stable, time-aware ordering for sequential quality operations.

    :param dataset: input dataframe
    :param time_col: selected time column
    :param secondary_keys: optional entity key columns
    :param winner_formatter: optional datetime parsing kwargs
    :return: ordered dataframe with helper columns
    """
    ordered = dataset.copy()
    ordered["_row_order"] = range(int(ordered.shape[0]))
    if time_col in ordered.columns:
        ordered["_ts"] = _parse_time_series(ordered, time_col, winner_formatter)
    else:
        ordered["_ts"] = pd.NaT
    valid_secondary_keys = [
        key
        for key in (secondary_keys or [])
        if key in ordered.columns and key != time_col
    ]
    sort_cols = list(valid_secondary_keys)
    if ordered["_ts"].notna().any():
        sort_cols.append("_ts")
    sort_cols.append("_row_order")
    ordered = ordered.sort_values(sort_cols, na_position="last").reset_index(drop=True)
    return ordered


def _iter_series_frames(
    dataset: pd.DataFrame,
    secondary_keys: list[str] | None = None,
) -> list[tuple[dict[str, Any] | None, pd.DataFrame]]:
    """
    Yield one frame per inferred series.

    :param dataset: ordered dataframe
    :param secondary_keys: optional entity keys
    :return: list of entity/frame pairs
    """
    valid_secondary_keys = [
        key for key in (secondary_keys or []) if key in dataset.columns
    ]
    if not valid_secondary_keys:
        return [(None, dataset)]
    items: list[tuple[dict[str, Any] | None, pd.DataFrame]] = []
    grouped = dataset.groupby(valid_secondary_keys, dropna=False, sort=False)
    for raw_key, frame in grouped:
        key_tuple = raw_key if isinstance(raw_key, tuple) else (raw_key,)
        items.append((_series_identifier(valid_secondary_keys, key_tuple), frame))
    return items


def _mask_run_lengths(mask: pd.Series) -> list[int]:
    """
    Return lengths of consecutive true runs in a boolean mask.

    :param mask: boolean mask
    :return: run lengths
    """
    run_lengths: list[int] = []
    current = 0
    for is_true in mask.fillna(False).astype(bool).tolist():
        if is_true:
            current += 1
        elif current > 0:
            run_lengths.append(current)
            current = 0
    if current > 0:
        run_lengths.append(current)
    return run_lengths


def _safe_float(value: Any) -> float | None:
    """
    Convert a numeric-like value into a JSON-friendly float.

    :param value: input value
    :return: float or None
    """
    if value is None or pd.isna(value):
        return None
    return float(value)


def _candidate_univariate_numeric_cols(
    dataset: pd.DataFrame,
    *,
    time_col: str,
    secondary_keys: list[str] | None = None,
    numeric_continuous_cols: list[str] | None = None,
    numeric_count_cols: list[str] | None = None,
    binary_flag_cols: list[str] | None = None,
) -> list[str]:
    """
    Return deterministic numeric columns suitable for univariate analysis.

    :param dataset: input dataframe
    :param time_col: selected time column
    :param secondary_keys: optional entity key columns
    :param numeric_continuous_cols: inferred continuous numeric columns
    :param numeric_count_cols: inferred count columns
    :param binary_flag_cols: inferred binary columns
    :return: ordered numeric analysis columns
    """
    excluded = {time_col, *(secondary_keys or [])}
    candidates = list(
        dict.fromkeys(
            [
                *[col for col in (numeric_continuous_cols or []) if col in dataset.columns],
                *[col for col in (numeric_count_cols or []) if col in dataset.columns],
                *[col for col in (binary_flag_cols or []) if col in dataset.columns],
            ]
        )
    )
    if not candidates:
        candidates = [
            str(col)
            for col in dataset.columns
            if str(col) not in excluded and pd.to_numeric(dataset[col], errors="coerce").notna().any()
        ]
    return [col for col in candidates if col not in excluded]


def _tail_ratio(series: pd.Series) -> float | None:
    """
    Compute a simple deterministic tail ratio.

    :param series: numeric series
    :return: tail ratio or None
    """
    valid = pd.to_numeric(series, errors="coerce").dropna()
    if valid.empty:
        return None
    p50 = valid.quantile(0.50)
    p99 = valid.quantile(0.99)
    if pd.isna(p50) or pd.isna(p99):
        return None
    if float(abs(p50)) <= 1e-12:
        return None if float(abs(p99)) <= 1e-12 else float(abs(p99))
    return float(abs(p99) / abs(p50))


def _univariate_summary(series: pd.Series) -> dict[str, Any]:
    """
    Compute deterministic univariate summary statistics.

    :param series: numeric-like series
    :return: summary stats
    """
    numeric = pd.to_numeric(series, errors="coerce")
    valid = numeric.dropna()
    n_total = int(series.shape[0])
    n_non_null = int(valid.shape[0])
    n_missing = max(0, n_total - n_non_null)
    if valid.empty:
        return {
            "n_total": n_total,
            "n_non_null": 0,
            "n_missing": n_missing,
            "missing_pct": None if n_total == 0 else float(100.0 * n_missing / n_total),
            "n_unique": 0,
            "mean": None,
            "std": None,
            "min": None,
            "p01": None,
            "p05": None,
            "p25": None,
            "p50": None,
            "p75": None,
            "p95": None,
            "p99": None,
            "max": None,
            "iqr": None,
            "zero_fraction": None,
            "skew": None,
            "kurtosis": None,
            "tail_ratio_p99_p50": None,
        }
    q = valid.quantile([0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99])
    return {
        "n_total": n_total,
        "n_non_null": n_non_null,
        "n_missing": n_missing,
        "missing_pct": None if n_total == 0 else float(100.0 * n_missing / n_total),
        "n_unique": int(valid.nunique(dropna=True)),
        "mean": _safe_float(valid.mean()),
        "std": _safe_float(valid.std()),
        "min": _safe_float(valid.min()),
        "p01": _safe_float(q.loc[0.01]),
        "p05": _safe_float(q.loc[0.05]),
        "p25": _safe_float(q.loc[0.25]),
        "p50": _safe_float(q.loc[0.50]),
        "p75": _safe_float(q.loc[0.75]),
        "p95": _safe_float(q.loc[0.95]),
        "p99": _safe_float(q.loc[0.99]),
        "max": _safe_float(valid.max()),
        "iqr": _safe_float(q.loc[0.75] - q.loc[0.25]),
        "zero_fraction": float((valid == 0).mean()),
        "skew": _safe_float(valid.skew()),
        "kurtosis": _safe_float(valid.kurt()),
        "tail_ratio_p99_p50": _tail_ratio(valid),
    }


def _gaussian_kde_curve(series: pd.Series, *, n_points: int = 256) -> tuple[np.ndarray, np.ndarray] | None:
    """
    Compute a simple Gaussian KDE curve without scipy.

    :param series: numeric series
    :param n_points: number of evaluation points
    :return: x/y arrays or None when KDE is not appropriate
    """
    valid = pd.to_numeric(series, errors="coerce").dropna().to_numpy(dtype=float)
    if valid.size < 30:
        return None
    unique = np.unique(valid)
    if unique.size < 10:
        return None
    std = float(np.std(valid, ddof=1))
    iqr = float(np.subtract(*np.percentile(valid, [75, 25])))
    scale = min(std, iqr / 1.34) if iqr > 0.0 else std
    if not np.isfinite(scale) or scale <= 0.0:
        return None
    bandwidth = 0.9 * scale * (valid.size ** (-1.0 / 5.0))
    if not np.isfinite(bandwidth) or bandwidth <= 0.0:
        return None
    x_grid = np.linspace(float(valid.min()), float(valid.max()), n_points)
    diffs = (x_grid[:, None] - valid[None, :]) / bandwidth
    density = np.exp(-0.5 * diffs**2).sum(axis=1)
    density /= float(valid.size * bandwidth * np.sqrt(2.0 * np.pi))
    return x_grid, density


def _transform_candidates(series: pd.Series) -> dict[str, pd.Series]:
    """
    Build deterministic transform candidates for one numeric series.

    :param series: numeric series
    :return: map of candidate name to transformed series
    """
    numeric = pd.to_numeric(series, errors="coerce")
    candidates: dict[str, pd.Series] = {"none": numeric}
    valid = numeric.dropna()
    if valid.empty:
        return candidates
    candidates["cuberoot"] = numeric.apply(
        lambda value: np.cbrt(value) if pd.notna(value) else value
    )
    if float(valid.min()) >= 0.0:
        candidates["sqrt"] = numeric.apply(
            lambda value: np.sqrt(value) if pd.notna(value) else value
        )
        candidates["log1p"] = pd.Series(np.log1p(numeric), index=numeric.index)
    return candidates


def _transform_score(series: pd.Series) -> dict[str, Any]:
    """
    Score one transformed series using deterministic shape criteria.

    :param series: transformed numeric series
    :return: score details
    """
    summary = _univariate_summary(series)
    valid = pd.to_numeric(series, errors="coerce").dropna()
    if valid.empty:
        return {
            "summary": summary,
            "score": None,
        }
    abs_skew = abs(float(summary["skew"])) if summary["skew"] is not None else 99.0
    abs_kurtosis = abs(float(summary["kurtosis"])) if summary["kurtosis"] is not None else 99.0
    tail_ratio = float(summary["tail_ratio_p99_p50"]) if summary["tail_ratio_p99_p50"] is not None else 99.0
    score = float(abs_skew + 0.25 * abs_kurtosis + 0.10 * tail_ratio)
    return {
        "summary": summary,
        "score": score,
    }


class _TemporalStatsArgs(pydantic.BaseModel):
    """
    Store arguments for deterministic temporal statistics.
    """

    model_config = pydantic.ConfigDict(extra="forbid")
    path: str
    time_col: str
    secondary_keys: list[str] | None = None
    winner_formatter: dict[str, Any] | None = None


@ltools.tool(args_schema=_TemporalStatsArgs)
def compute_temporal_stats(
    path: str,
    time_col: str,
    secondary_keys: list[str] | None = None,
    winner_formatter: dict[str, Any] | None = None,
) -> dict:
    """
    Compute deterministic temporal range, coverage, and sampling-frequency
    statistics.

    Theory:
    Time-series coverage is defined relative to an expected sampling interval.
    Once the timestamps are parsed, the empirical deltas between consecutive
    observations reveal the dominant cadence of the data. That cadence becomes
    the expected frequency against which we can measure irregular sampling,
    missing timestamps, longest gaps, and per-entity coverage. For panel data,
    these statistics must be computed per entity (or per composite entity key),
    because a dataset can be well covered overall while still containing weak or
    sparse individual series.

    :param path: dataset path
    :param time_col: selected time column
    :param secondary_keys: optional entity key columns
    :param winner_formatter: optional datetime parsing kwargs
    :return: temporal statistics payload
    """
    dataset_path = pathlib.Path(path)
    dataset = load_dataset(dataset_path)
    if time_col not in dataset.columns:
        raise KeyError(f"time_col '{time_col}' not found in dataset")
    secondary_keys = [
        key for key in (secondary_keys or []) if key in dataset.columns and key != time_col
    ]
    timestamp = _parse_time_series(dataset, time_col, winner_formatter)
    valid_rows = dataset.copy()
    valid_rows["_ts"] = timestamp
    valid_rows = valid_rows.dropna(subset=["_ts"])
    if secondary_keys:
        grouped_iter = valid_rows.groupby(secondary_keys, dropna=True)
        group_items = list(grouped_iter)
    else:
        group_items = [(tuple(), valid_rows)]

    all_deltas: list[pd.Timedelta] = []
    per_entity: list[dict[str, Any]] = []
    global_min = None if valid_rows.empty else valid_rows["_ts"].min()
    global_max = None if valid_rows.empty else valid_rows["_ts"].max()

    for raw_key, frame in group_items:
        key_tuple = raw_key if isinstance(raw_key, tuple) else (raw_key,)
        unique_ts = (
            frame["_ts"].dropna().drop_duplicates().sort_values().reset_index(drop=True)
        )
        n_observed = int(unique_ts.shape[0])
        if n_observed >= 2:
            deltas = unique_ts.diff().dropna()
            positive_deltas = deltas[deltas > pd.Timedelta(0)]
        else:
            positive_deltas = pd.Series(dtype="timedelta64[ns]")
        all_deltas.extend(list(positive_deltas.tolist()))
        per_entity.append(
            {
                "entity": _series_identifier(secondary_keys, key_tuple),
                "n_observed_timestamps": n_observed,
                "min_time": None if unique_ts.empty else str(unique_ts.min()),
                "max_time": None if unique_ts.empty else str(unique_ts.max()),
                "_positive_deltas": positive_deltas,
            }
        )

    if all_deltas:
        delta_series = pd.Series(all_deltas, dtype="timedelta64[ns]")
        mode_candidates = delta_series.mode()
        mode_delta = None if mode_candidates.empty else mode_candidates.iloc[0]
        median_delta = delta_series.median()
        dominant_fraction = (
            0.0
            if mode_delta is None
            else float((delta_series == mode_delta).mean())
        )
        expected_delta = mode_delta if dominant_fraction >= 0.5 else median_delta
        is_irregular_sampling = bool(
            expected_delta is not None
            and float((delta_series == expected_delta).mean()) < 0.8
        )
    else:
        delta_series = pd.Series(dtype="timedelta64[ns]")
        mode_delta = None
        median_delta = None
        dominant_fraction = 0.0
        expected_delta = None
        is_irregular_sampling = False

    coverage_values: list[float] = []
    total_gaps = 0
    for item in per_entity:
        positive_deltas = item.pop("_positive_deltas")
        n_observed = item["n_observed_timestamps"]
        if n_observed == 0 or expected_delta is None or pd.isna(expected_delta):
            coverage_pct = None
            n_expected = n_observed
            gap_mask = pd.Series(dtype=bool)
            longest_gap = None
        else:
            span = pd.Timestamp(item["max_time"]) - pd.Timestamp(item["min_time"])
            if expected_delta <= pd.Timedelta(0):
                n_expected = n_observed
            else:
                n_expected = int(span / expected_delta) + 1
            n_expected = max(n_expected, n_observed, 1)
            coverage_pct = float(100.0 * n_observed / n_expected)
            gap_mask = positive_deltas > expected_delta
            longest_gap = (
                None if positive_deltas.empty else positive_deltas.max()
            )
        n_gaps = int(gap_mask.sum()) if not gap_mask.empty else 0
        total_gaps += n_gaps
        if coverage_pct is not None:
            coverage_values.append(coverage_pct)
        item["n_expected_timestamps"] = int(n_expected)
        item["coverage_pct"] = coverage_pct
        item["n_gaps"] = n_gaps
        item["longest_gap"] = _format_timedelta(longest_gap)

    if expected_delta is None:
        resampling_decision = "insufficient_data"
    elif is_irregular_sampling:
        resampling_decision = "keep_irregular_gap_aware"
    elif coverage_values and min(coverage_values) < 99.0:
        resampling_decision = "resample_to_regular_grid"
    else:
        resampling_decision = "already_regular"

    coverage_summary = {
        "n_series": len(per_entity),
        "mean_coverage_pct": (
            None if not coverage_values else float(pd.Series(coverage_values).mean())
        ),
        "min_coverage_pct": (
            None if not coverage_values else float(pd.Series(coverage_values).min())
        ),
        "max_coverage_pct": (
            None if not coverage_values else float(pd.Series(coverage_values).max())
        ),
        "total_gaps": int(total_gaps),
    }

    return {
        "time_col": time_col,
        "secondary_keys": secondary_keys,
        "n_nat_time": int(timestamp.isna().sum()),
        "min_time": None if global_min is None else str(global_min),
        "max_time": None if global_max is None else str(global_max),
        "typical_delta_mode": _format_timedelta(mode_delta),
        "typical_delta_median": _format_timedelta(median_delta),
        "expected_frequency": _format_timedelta(expected_delta),
        "dominant_frequency_fraction": dominant_fraction,
        "is_irregular_sampling": is_irregular_sampling,
        "resampling_decision": resampling_decision,
        "coverage_summary": coverage_summary,
        "coverage_per_entity": per_entity,
    }


class _MissingnessAuditArgs(pydantic.BaseModel):
    """
    Store arguments for deterministic missingness auditing.
    """

    model_config = pydantic.ConfigDict(extra="forbid")
    path: str
    time_col: str
    secondary_keys: list[str] | None = None
    winner_formatter: dict[str, Any] | None = None


@ltools.tool(args_schema=_MissingnessAuditArgs)
def audit_missingness(
    path: str,
    time_col: str,
    secondary_keys: list[str] | None = None,
    winner_formatter: dict[str, Any] | None = None,
) -> dict:
    """
    Audit missingness as two distinct problems: missing values and missing
    timestamps.

    Theory:
    Missing cells inside observed rows and missing timestamps in the implied
    time grid are different failure modes. Value missingness tells us which
    variables are incomplete at observed observation times. Timestamp
    missingness tells us whether observations are absent from the expected
    sampling cadence. The former guides imputation choices per feature; the
    latter guides reindexing, coverage assessment, and gap-aware modeling.

    :param path: dataset path
    :param time_col: selected time column
    :param secondary_keys: optional entity key columns
    :param winner_formatter: optional datetime parsing kwargs
    :return: missingness audit payload
    """
    dataset_path = pathlib.Path(path)
    dataset = load_dataset(dataset_path)
    ordered = _ordered_dataset(
        dataset,
        time_col=time_col,
        secondary_keys=secondary_keys,
        winner_formatter=winner_formatter,
    )
    temporal_report = compute_temporal_stats.invoke(
        {
            "path": path,
            "time_col": time_col,
            "secondary_keys": secondary_keys or [],
            "winner_formatter": winner_formatter or {},
        }
    )
    profiles = _build_column_profiles(dataset)
    value_missingness_by_column: list[dict[str, Any]] = []
    total_missing_cells = int(dataset.isna().sum().sum())
    all_series_frames = _iter_series_frames(ordered, secondary_keys)
    for col in [str(value) for value in dataset.columns]:
        missing_mask = dataset[col].isna()
        n_missing = int(missing_mask.sum())
        missing_pct = 0.0 if dataset.empty else float(100.0 * n_missing / len(dataset))
        run_lengths: list[int] = []
        for _, frame in all_series_frames:
            frame_run_lengths = _mask_run_lengths(frame[col].isna())
            run_lengths.extend(frame_run_lengths)
        eligible_strategies = ["leave_as_nan", "drop_rows"]
        profile = profiles[col]
        if n_missing > 0 and col != time_col:
            eligible_strategies.append("forward_fill")
            if profile["is_numeric_like"]:
                eligible_strategies.append("interpolate")
            if (
                profile["is_numeric_like"]
                and profile["is_integer_like"]
                and profile["is_nonnegative_like"]
            ):
                eligible_strategies.append("zero_fill")
        value_missingness_by_column.append(
            {
                "col": col,
                "dtype": profile["dtype"],
                "n_missing": n_missing,
                "missing_pct": missing_pct,
                "n_missing_runs": int(len(run_lengths)),
                "longest_missing_run": int(max(run_lengths, default=0)),
                "eligible_strategies": eligible_strategies,
                "sample_values": profile["sample_values"],
            }
        )
    value_missingness_by_column.sort(
        key=lambda item: (item["n_missing"], item["longest_missing_run"]),
        reverse=True,
    )
    worst_value_col = next(
        (item for item in value_missingness_by_column if item["n_missing"] > 0),
        None,
    )
    timestamp_missingness_by_entity: list[dict[str, Any]] = []
    total_expected_timestamps = 0
    total_observed_timestamps = 0
    total_missing_timestamps = 0
    n_series_with_timestamp_gaps = 0
    for item in temporal_report["coverage_per_entity"]:
        n_observed = int(item.get("n_observed_timestamps") or 0)
        n_expected = int(item.get("n_expected_timestamps") or n_observed)
        n_missing_timestamps = max(0, n_expected - n_observed)
        total_expected_timestamps += n_expected
        total_observed_timestamps += n_observed
        total_missing_timestamps += n_missing_timestamps
        if n_missing_timestamps > 0:
            n_series_with_timestamp_gaps += 1
        timestamp_missingness_by_entity.append(
            {
                "entity": item.get("entity"),
                "n_observed_timestamps": n_observed,
                "n_expected_timestamps": n_expected,
                "n_missing_timestamps": n_missing_timestamps,
                "coverage_pct": item.get("coverage_pct"),
                "n_gaps": int(item.get("n_gaps") or 0),
                "longest_gap": item.get("longest_gap"),
            }
        )
    timestamp_missingness_by_entity.sort(
        key=lambda item: (
            item["n_missing_timestamps"],
            item["n_gaps"],
            item["coverage_pct"] if item["coverage_pct"] is not None else -1.0,
        ),
        reverse=True,
    )
    return {
        "time_col": time_col,
        "secondary_keys": [
            key for key in (secondary_keys or []) if key in dataset.columns and key != time_col
        ],
        "n_rows": int(dataset.shape[0]),
        "n_cols": int(dataset.shape[1]),
        "value_missingness_summary": {
            "total_missing_cells": total_missing_cells,
            "total_missing_fraction": (
                0.0
                if dataset.empty
                else float(100.0 * total_missing_cells / max(1, int(dataset.size)))
            ),
            "columns_with_missing_values": int(sum(item["n_missing"] > 0 for item in value_missingness_by_column)),
            "worst_column": None if worst_value_col is None else worst_value_col["col"],
            "worst_column_missing_pct": (
                None if worst_value_col is None else worst_value_col["missing_pct"]
            ),
        },
        "value_missingness_by_column": value_missingness_by_column,
        "timestamp_missingness_summary": {
            "expected_frequency": temporal_report["expected_frequency"],
            "is_irregular_sampling": temporal_report["is_irregular_sampling"],
            "resampling_decision": temporal_report["resampling_decision"],
            "n_nat_time": temporal_report["n_nat_time"],
            "total_expected_timestamps": total_expected_timestamps,
            "total_observed_timestamps": total_observed_timestamps,
            "total_missing_timestamps": total_missing_timestamps,
            "n_series_with_timestamp_gaps": n_series_with_timestamp_gaps,
        },
        "timestamp_missingness_by_entity": timestamp_missingness_by_entity,
        "column_profiles": profiles,
    }


class MissingnessActionSpec(pydantic.BaseModel):
    """
    Store one bounded missingness action.
    """

    model_config = pydantic.ConfigDict(extra="forbid")
    col: str
    strategy: str
    create_missingness_flag: bool = True
    reason: str = ""


class _ApplyMissingnessActionsArgs(pydantic.BaseModel):
    """
    Store arguments for deterministic missingness handling.
    """

    model_config = pydantic.ConfigDict(extra="forbid")
    source_path: str
    input_path: str
    time_col: str
    secondary_keys: list[str] | None = None
    winner_formatter: dict[str, Any] | None = None
    actions: list[MissingnessActionSpec]


@ltools.tool(args_schema=_ApplyMissingnessActionsArgs)
def apply_missingness_actions(
    source_path: str,
    input_path: str,
    time_col: str,
    secondary_keys: list[str] | None = None,
    winner_formatter: dict[str, Any] | None = None,
    actions: list[MissingnessActionSpec] | None = None,
) -> dict:
    """
    Apply one bounded missingness strategy per selected column.

    Theory:
    The policy choice for each column may be ambiguous, but the mechanics of
    applying a chosen action should be deterministic and reproducible. By
    sorting within entity/time order, optionally adding missingness flags, and
    then applying simple bounded transforms, the stage can record exactly what
    changed without allowing the LLM to mutate data directly.

    :param source_path: original dataset path used for artifact naming
    :param input_path: dataset path to transform
    :param time_col: selected time column
    :param secondary_keys: optional entity key columns
    :param winner_formatter: optional datetime parsing kwargs
    :param actions: bounded per-column action plan
    :return: transformation report with output dataset path
    """
    dataset = load_dataset(pathlib.Path(input_path))
    working = _ordered_dataset(
        dataset,
        time_col=time_col,
        secondary_keys=secondary_keys,
        winner_formatter=winner_formatter,
    )
    valid_secondary_keys = [
        key
        for key in (secondary_keys or [])
        if key in working.columns and key != time_col
    ]
    action_items = [item.model_dump() if isinstance(item, pydantic.BaseModel) else item for item in (actions or [])]
    drop_mask = pd.Series(False, index=working.index)
    applied_actions: list[dict[str, Any]] = []
    for action in action_items:
        col = str(action["col"])
        strategy = str(action["strategy"])
        create_missingness_flag = bool(action.get("create_missingness_flag", True))
        reason = str(action.get("reason") or "")
        if col not in working.columns:
            applied_actions.append(
                {
                    "col": col,
                    "strategy": strategy,
                    "status": "skipped_missing_column",
                    "reason": reason,
                }
            )
            continue
        before_mask = working[col].isna()
        n_missing_before = int(before_mask.sum())
        if create_missingness_flag and n_missing_before > 0:
            flag_col = f"{col}__was_missing"
            if flag_col not in working.columns:
                working[flag_col] = before_mask.astype(int)
        status = "applied"
        if strategy == "leave_as_nan":
            pass
        elif strategy == "drop_rows":
            drop_mask = drop_mask | before_mask
        elif strategy == "forward_fill":
            if valid_secondary_keys:
                working[col] = working.groupby(valid_secondary_keys, dropna=False)[col].ffill()
            else:
                working[col] = working[col].ffill()
        elif strategy == "interpolate":
            numeric = pd.to_numeric(working[col], errors="coerce")
            if valid_secondary_keys:
                working[col] = working.groupby(valid_secondary_keys, dropna=False)[numeric.name].transform(
                    lambda series: pd.to_numeric(series, errors="coerce").interpolate(
                        limit_area="inside"
                    )
                )
            else:
                working[col] = numeric.interpolate(limit_area="inside")
        elif strategy == "zero_fill":
            numeric = pd.to_numeric(working[col], errors="coerce")
            working[col] = numeric.fillna(0.0)
        else:
            status = "skipped_unsupported_strategy"
        n_missing_after = int(working[col].isna().sum()) if col in working.columns else None
        applied_actions.append(
            {
                "col": col,
                "strategy": strategy,
                "status": status,
                "reason": reason,
                "create_missingness_flag": create_missingness_flag,
                "n_missing_before": n_missing_before,
                "n_missing_after": n_missing_after,
                "n_values_filled": None if n_missing_after is None else max(0, n_missing_before - n_missing_after),
                "n_rows_marked_for_drop": int(before_mask.sum()) if strategy == "drop_rows" else 0,
            }
        )
    n_rows_before = int(working.shape[0])
    if bool(drop_mask.any()):
        working = working.loc[~drop_mask].copy()
    n_rows_after = int(working.shape[0])
    n_rows_dropped = max(0, n_rows_before - n_rows_after)
    remaining_missing_by_column = {
        str(col): int(working[col].isna().sum())
        for col in working.columns
        if not str(col).startswith("_")
    }
    output_dataset = working.drop(columns=["_ts", "_row_order"], errors="ignore")
    output_path = write_stage_dataset(source_path, "handle_missingness", output_dataset)
    return {
        "input_path": input_path,
        "output_path": output_path,
        "n_rows_before": n_rows_before,
        "n_rows_after": n_rows_after,
        "n_rows_dropped": n_rows_dropped,
        "actions_applied": applied_actions,
        "remaining_missing_by_column": remaining_missing_by_column,
        "sorted_by": valid_secondary_keys + (["_ts"] if "_ts" in working.columns else []),
    }


class _ScaleProfileArgs(pydantic.BaseModel):
    """
    Store arguments for deterministic scale profiling.
    """

    model_config = pydantic.ConfigDict(extra="forbid")
    path: str
    numeric_continuous_cols: list[str] | None = None
    numeric_count_cols: list[str] | None = None
    binary_flag_cols: list[str] | None = None


@ltools.tool(args_schema=_ScaleProfileArgs)
def profile_standardization_candidates(
    path: str,
    numeric_continuous_cols: list[str] | None = None,
    numeric_count_cols: list[str] | None = None,
    binary_flag_cols: list[str] | None = None,
) -> dict:
    """
    Profile scale and tail behavior for numeric features.

    Theory:
    Standardization is only justified when the observed numeric scales or tail
    behaviors would otherwise distort comparisons or downstream models. Robust
    scaling depends on median/IQR support, while `log1p` depends on nonnegative
    support and heavy right tails. These properties can be measured
    deterministically before the LLM decides whether the optional transform is
    worth applying.

    :param path: dataset path
    :param numeric_continuous_cols: inferred continuous numeric columns
    :param numeric_count_cols: inferred count-like numeric columns
    :param binary_flag_cols: inferred binary columns to exclude
    :return: per-column scale profile
    """
    dataset = load_dataset(pathlib.Path(path))
    continuous = [col for col in (numeric_continuous_cols or []) if col in dataset.columns]
    counts = [col for col in (numeric_count_cols or []) if col in dataset.columns]
    excluded = {col for col in (binary_flag_cols or []) if col in dataset.columns}
    candidate_cols = [col for col in continuous + counts if col not in excluded]
    candidate_cols = list(dict.fromkeys(candidate_cols))
    per_column: list[dict[str, Any]] = []
    iqr_values: list[float] = []
    for col in candidate_cols:
        numeric = pd.to_numeric(dataset[col], errors="coerce").dropna()
        if numeric.empty:
            continue
        median = numeric.median()
        q1 = numeric.quantile(0.25)
        q3 = numeric.quantile(0.75)
        iqr = q3 - q1
        p01 = numeric.quantile(0.01)
        p50 = numeric.quantile(0.50)
        p99 = numeric.quantile(0.99)
        positive_fraction = float((numeric >= 0).mean())
        zero_fraction = float((numeric == 0).mean())
        abs_median = abs(float(median)) if not pd.isna(median) else 0.0
        tail_ratio = None
        if p50 > 0:
            tail_ratio = float(p99 / p50)
        if float(iqr) > 0.0:
            iqr_values.append(float(iqr))
        feature_bucket = "numeric_continuous" if col in continuous else "numeric_count"
        eligible_actions = ["none"]
        if float(iqr) > 0.0:
            eligible_actions.append("robust_scale")
        if float(numeric.min()) >= 0.0:
            eligible_actions.append("log1p")
        if "robust_scale" in eligible_actions and "log1p" in eligible_actions:
            eligible_actions.append("log1p_then_robust_scale")
        per_column.append(
            {
                "col": col,
                "feature_bucket": feature_bucket,
                "n_non_null": int(numeric.shape[0]),
                "min": _safe_float(numeric.min()),
                "max": _safe_float(numeric.max()),
                "mean": _safe_float(numeric.mean()),
                "std": _safe_float(numeric.std()),
                "median": _safe_float(median),
                "iqr": _safe_float(iqr),
                "p01": _safe_float(p01),
                "p50": _safe_float(p50),
                "p99": _safe_float(p99),
                "zero_fraction": zero_fraction,
                "positive_fraction": positive_fraction,
                "skew": _safe_float(numeric.skew()),
                "tail_ratio_p99_p50": None if tail_ratio is None else tail_ratio,
                "scale_span": _safe_float(numeric.max() - numeric.min()),
                "relative_iqr_to_median": None if abs_median <= 0.0 else float(iqr / abs_median),
                "eligible_actions": eligible_actions,
            }
        )
    positive_iqrs = [value for value in iqr_values if value > 0.0]
    return {
        "path": path,
        "candidate_cols": [item["col"] for item in per_column],
        "n_candidate_cols": len(per_column),
        "scale_summary": {
            "max_iqr": None if not positive_iqrs else float(max(positive_iqrs)),
            "min_positive_iqr": None if not positive_iqrs else float(min(positive_iqrs)),
            "iqr_ratio_max_to_min": (
                None
                if len(positive_iqrs) < 2 or min(positive_iqrs) <= 0.0
                else float(max(positive_iqrs) / min(positive_iqrs))
            ),
            "n_nontrivial_log_candidates": int(
                sum(
                    (
                        item["min"] is not None
                        and item["min"] >= 0.0
                        and item["tail_ratio_p99_p50"] is not None
                        and item["tail_ratio_p99_p50"] >= 5.0
                    )
                    for item in per_column
                )
            ),
        },
        "per_column": per_column,
    }


class StandardizationActionSpec(pydantic.BaseModel):
    """
    Store one bounded standardization action.
    """

    model_config = pydantic.ConfigDict(extra="forbid")
    col: str
    action: str
    reason: str = ""


class _ApplyStandardizationArgs(pydantic.BaseModel):
    """
    Store arguments for deterministic standardization.
    """

    model_config = pydantic.ConfigDict(extra="forbid")
    source_path: str
    input_path: str
    actions: list[StandardizationActionSpec]


@ltools.tool(args_schema=_ApplyStandardizationArgs)
def apply_standardization_actions(
    source_path: str,
    input_path: str,
    actions: list[StandardizationActionSpec] | None = None,
) -> dict:
    """
    Apply bounded numeric transforms deterministically.

    Theory:
    Whether a transform is desirable is an interpretive decision, but the
    transform itself should be a pure function of the observed column values and
    recorded parameters. Persisting medians, IQRs, and log usage makes the
    optional stage reproducible and auditable.

    :param source_path: original dataset path used for artifact naming
    :param input_path: dataset path to transform
    :param actions: bounded per-column transformation plan
    :return: transformation report with output dataset path
    """
    dataset = load_dataset(pathlib.Path(input_path)).copy()
    action_items = [item.model_dump() if isinstance(item, pydantic.BaseModel) else item for item in (actions or [])]
    applied_actions: list[dict[str, Any]] = []
    for action in action_items:
        col = str(action["col"])
        transform = str(action["action"])
        reason = str(action.get("reason") or "")
        if col not in dataset.columns:
            applied_actions.append(
                {
                    "col": col,
                    "action": transform,
                    "status": "skipped_missing_column",
                    "reason": reason,
                }
            )
            continue
        numeric = pd.to_numeric(dataset[col], errors="coerce")
        valid = numeric.dropna()
        if valid.empty:
            applied_actions.append(
                {
                    "col": col,
                    "action": transform,
                    "status": "skipped_no_numeric_values",
                    "reason": reason,
                }
            )
            continue
        params: dict[str, Any] = {}
        transformed = numeric.copy()
        status = "applied"
        if transform == "none":
            pass
        elif transform == "robust_scale":
            median = valid.median()
            q1 = valid.quantile(0.25)
            q3 = valid.quantile(0.75)
            iqr = q3 - q1
            if float(iqr) <= 0.0:
                status = "skipped_zero_iqr"
            else:
                transformed = (numeric - median) / iqr
                params = {"median": float(median), "iqr": float(iqr)}
        elif transform == "log1p":
            if float(valid.min()) < 0.0:
                status = "skipped_negative_values"
            else:
                transformed = pd.Series(np.log1p(numeric), index=numeric.index)
                params = {"log1p": True}
        elif transform == "log1p_then_robust_scale":
            if float(valid.min()) < 0.0:
                status = "skipped_negative_values"
            else:
                logged = pd.Series(np.log1p(numeric), index=numeric.index)
                logged_valid = logged.dropna()
                median = logged_valid.median()
                q1 = logged_valid.quantile(0.25)
                q3 = logged_valid.quantile(0.75)
                iqr = q3 - q1
                if float(iqr) <= 0.0:
                    status = "skipped_zero_iqr_after_log1p"
                else:
                    transformed = (logged - median) / iqr
                    params = {
                        "log1p": True,
                        "median_after_log1p": float(median),
                        "iqr_after_log1p": float(iqr),
                    }
        else:
            status = "skipped_unsupported_action"
        if status == "applied":
            dataset[col] = transformed
        applied_actions.append(
            {
                "col": col,
                "action": transform,
                "status": status,
                "reason": reason,
                "params": params,
            }
        )
    output_path = write_stage_dataset(source_path, "standardize", dataset)
    return {
        "input_path": input_path,
        "output_path": output_path,
        "actions_applied": applied_actions,
    }


class _UnivariateAnalysisArgs(pydantic.BaseModel):
    """
    Store arguments for deterministic univariate analysis.
    """

    model_config = pydantic.ConfigDict(extra="forbid")
    source_path: str
    input_path: str
    time_col: str
    secondary_keys: list[str] | None = None
    numeric_continuous_cols: list[str] | None = None
    numeric_count_cols: list[str] | None = None
    binary_flag_cols: list[str] | None = None


@ltools.tool(args_schema=_UnivariateAnalysisArgs)
def compute_univariate_metrics_and_plots(
    source_path: str,
    input_path: str,
    time_col: str,
    secondary_keys: list[str] | None = None,
    numeric_continuous_cols: list[str] | None = None,
    numeric_count_cols: list[str] | None = None,
    binary_flag_cols: list[str] | None = None,
) -> dict:
    """
    Compute deterministic univariate metrics and produce per-column plots.

    Theory:
    Univariate EDA starts by measuring one feature at a time. Summary metrics
    expose support, spread, skew, missingness, and tail behavior, while
    histogram/ECDF/KDE plots show what "normal values" look like. For panel
    data, per-entity summaries are also useful because a few odd entities can
    hide inside an otherwise normal aggregate distribution.

    :param source_path: original dataset path used for artifact naming
    :param input_path: dataset path to analyze
    :param time_col: selected time column
    :param secondary_keys: optional entity key columns
    :param numeric_continuous_cols: inferred continuous numeric columns
    :param numeric_count_cols: inferred count columns
    :param binary_flag_cols: inferred binary columns
    :return: summary report and plot manifest
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    dataset = load_dataset(pathlib.Path(input_path))
    candidate_cols = _candidate_univariate_numeric_cols(
        dataset,
        time_col=time_col,
        secondary_keys=secondary_keys,
        numeric_continuous_cols=numeric_continuous_cols,
        numeric_count_cols=numeric_count_cols,
        binary_flag_cols=binary_flag_cols,
    )
    overall_feature_summaries: list[dict[str, Any]] = []
    per_entity_feature_summaries: list[dict[str, Any]] = []
    plot_manifest: list[dict[str, Any]] = []
    valid_secondary_keys = [
        key for key in (secondary_keys or []) if key in dataset.columns and key != time_col
    ]
    for col in candidate_cols:
        summary = _univariate_summary(dataset[col])
        summary["col"] = col
        summary["feature_bucket"] = (
            "numeric_continuous"
            if col in (numeric_continuous_cols or [])
            else "numeric_count"
            if col in (numeric_count_cols or [])
            else "binary_flag"
            if col in (binary_flag_cols or [])
            else "numeric"
        )
        overall_feature_summaries.append(summary)

        numeric = pd.to_numeric(dataset[col], errors="coerce").dropna()
        fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
        if numeric.empty:
            axes[0].text(0.5, 0.5, "No numeric observations", ha="center", va="center")
            axes[0].set_axis_off()
            axes[1].text(0.5, 0.5, "No numeric observations", ha="center", va="center")
            axes[1].set_axis_off()
            kde_plotted = False
        else:
            n_bins = int(min(50, max(10, np.sqrt(numeric.shape[0]))))
            axes[0].hist(numeric, bins=n_bins, color="#4472C4", alpha=0.75, density=True)
            kde_curve = _gaussian_kde_curve(numeric)
            kde_plotted = kde_curve is not None
            if kde_curve is not None:
                x_grid, density = kde_curve
                axes[0].plot(x_grid, density, color="#D62728", linewidth=1.5)
            sorted_vals = np.sort(numeric.to_numpy(dtype=float))
            y_ecdf = np.arange(1, sorted_vals.size + 1) / float(sorted_vals.size)
            axes[1].step(sorted_vals, y_ecdf, where="post", color="#2CA02C", linewidth=1.5)
            axes[1].set_ylim(0.0, 1.0)
        axes[0].set_title(f"{col} histogram")
        axes[1].set_title(f"{col} ECDF")
        fig.suptitle(
            f"{col} | skew={summary['skew']} | tail_ratio={summary['tail_ratio_p99_p50']}",
            fontsize=10,
        )
        plot_path = write_stage_plot(source_path, "univariate_metrics_plotting", f"{col}.distribution", fig)
        plt.close(fig)
        plot_manifest.append(
            {
                "col": col,
                "plot_path": plot_path,
                "kde_plotted": kde_plotted,
            }
        )

        if valid_secondary_keys:
            grouped = dataset.groupby(valid_secondary_keys, dropna=False, sort=False)
            for raw_key, frame in grouped:
                key_tuple = raw_key if isinstance(raw_key, tuple) else (raw_key,)
                entity = _series_identifier(valid_secondary_keys, key_tuple)
                entity_summary = _univariate_summary(frame[col])
                entity_summary["col"] = col
                entity_summary["entity"] = entity
                per_entity_feature_summaries.append(entity_summary)

    overall_feature_summaries.sort(
        key=lambda item: (
            item["missing_pct"] if item["missing_pct"] is not None else -1.0,
            abs(item["skew"]) if item["skew"] is not None else -1.0,
            item["tail_ratio_p99_p50"] if item["tail_ratio_p99_p50"] is not None else -1.0,
        ),
        reverse=True,
    )
    return {
        "input_path": input_path,
        "analysis_numeric_cols": candidate_cols,
        "overall_feature_summaries": overall_feature_summaries,
        "per_entity_feature_summaries": per_entity_feature_summaries,
        "plot_manifest": plot_manifest,
    }


class _TransformTestArgs(pydantic.BaseModel):
    """
    Store arguments for deterministic transform testing.
    """

    model_config = pydantic.ConfigDict(extra="forbid")
    source_path: str
    input_path: str
    time_col: str
    secondary_keys: list[str] | None = None
    numeric_continuous_cols: list[str] | None = None
    numeric_count_cols: list[str] | None = None
    binary_flag_cols: list[str] | None = None


@ltools.tool(args_schema=_TransformTestArgs)
def test_univariate_transforms(
    source_path: str,
    input_path: str,
    time_col: str,
    secondary_keys: list[str] | None = None,
    numeric_continuous_cols: list[str] | None = None,
    numeric_count_cols: list[str] | None = None,
    binary_flag_cols: list[str] | None = None,
) -> dict:
    """
    Deterministically compare candidate transforms for skewed or heavy-tailed
    numeric features.

    Theory:
    Transform testing should only run when there is enough empirical evidence
    that raw values may violate practical modeling assumptions or obscure
    univariate structure. The decision can be made deterministically from
    summary shape metrics such as skewness and tail ratios. Candidate transforms
    are then compared by how much they reduce those distortions.

    :param source_path: original dataset path used for trace naming
    :param input_path: dataset path to analyze
    :param time_col: selected time column
    :param secondary_keys: optional entity key columns
    :param numeric_continuous_cols: inferred continuous numeric columns
    :param numeric_count_cols: inferred count columns
    :param binary_flag_cols: inferred binary columns
    :return: transform test report
    """
    dataset = load_dataset(pathlib.Path(input_path))
    candidate_cols = _candidate_univariate_numeric_cols(
        dataset,
        time_col=time_col,
        secondary_keys=secondary_keys,
        numeric_continuous_cols=numeric_continuous_cols,
        numeric_count_cols=numeric_count_cols,
        binary_flag_cols=binary_flag_cols,
    )
    tested_columns: list[dict[str, Any]] = []
    skipped_columns: list[dict[str, Any]] = []
    for col in candidate_cols:
        numeric = pd.to_numeric(dataset[col], errors="coerce")
        base_summary = _univariate_summary(numeric)
        n_non_null = int(base_summary["n_non_null"])
        abs_skew = abs(float(base_summary["skew"])) if base_summary["skew"] is not None else 0.0
        tail_ratio = float(base_summary["tail_ratio_p99_p50"]) if base_summary["tail_ratio_p99_p50"] is not None else 0.0
        should_test = bool(
            n_non_null >= 30
            and (
                abs_skew >= 1.0
                or tail_ratio >= 4.0
            )
        )
        if not should_test:
            skipped_columns.append(
                {
                    "col": col,
                    "reason": (
                        "Insufficient deterministic evidence for transform testing. "
                        f"n_non_null={n_non_null}, abs_skew={abs_skew:.3f}, tail_ratio={tail_ratio:.3f}"
                    ),
                    "base_summary": base_summary,
                }
            )
            continue
        candidate_scores: list[dict[str, Any]] = []
        for name, transformed in _transform_candidates(numeric).items():
            score_payload = _transform_score(transformed)
            candidate_scores.append(
                {
                    "transform": name,
                    "score": score_payload["score"],
                    "summary": score_payload["summary"],
                }
            )
        valid_scores = [item for item in candidate_scores if item["score"] is not None]
        valid_scores.sort(key=lambda item: float(item["score"]))
        best = valid_scores[0]
        baseline = next(item for item in valid_scores if item["transform"] == "none")
        improvement = float(baseline["score"] - best["score"])
        if best["transform"] == "none" or improvement < 0.25:
            recommendation = "none"
            reason = (
                "Candidate transforms did not materially improve deterministic shape metrics "
                f"(best_improvement={improvement:.3f})."
            )
        else:
            recommendation = best["transform"]
            reason = (
                f"{best['transform']} best reduced deterministic shape distortion "
                f"(baseline_score={baseline['score']:.3f}, best_score={best['score']:.3f})."
            )
        tested_columns.append(
            {
                "col": col,
                "base_summary": base_summary,
                "candidate_scores": valid_scores,
                "recommended_transform": recommendation,
                "improvement_over_none": improvement,
                "reason": reason,
            }
        )
    payload = {
        "input_path": input_path,
        "n_candidate_cols": len(candidate_cols),
        "n_tested_cols": len(tested_columns),
        "n_skipped_cols": len(skipped_columns),
        "tested_columns": tested_columns,
        "skipped_columns": skipped_columns,
    }
    write_stage_trace(source_path, "test_transforms", payload)
    return payload


def analyze_header(state: dict) -> dict:
    """
    Validate dataset headers.

    :param state: graph state containing dataset path
    :return: updated state fields with header status
    """
    path = pathlib.Path(str(state["path"]))
    dataset = load_dataset(path)
    cols = list(dataset.columns)
    has_header = True
    error = ""
    if (
        all(isinstance(col, int) for col in cols)
        and cols == list(range(len(cols)))
    ):
        has_header = False
        error = "No column names."
    else:
        for col in cols:
            if col is None:
                has_header = False
                error = "One or more column names missing."
                break
            col_name = str(col).strip()
            if col_name == "":
                has_header = False
                error = "One or more column names missing."
                break
            if (
                col_name[0].isdigit()
                or not _VALID_HEADER_START_RE.match(col_name)
            ):
                has_header = False
                error = (
                    "One or more column names start with invalid characters."
                )
                break
    if has_header:
        result = {"has_header": has_header, "dataset": dataset}
    else:
        result = {"has_header": has_header, "error": error}
    return result


@ltools.tool
def extract_metadata(path: str) -> dict:
    """
    Return minimal dataset metadata.

    :param path: dataset path
    :return: metadata with shape and per-column cardinality
    """
    dataset_path = pathlib.Path(path)
    dataset = load_dataset(dataset_path)
    n_rows, n_cols = dataset.shape
    n_unique = dataset.nunique(dropna=True)
    n_unique_map = {str(col): int(n_unique[col]) for col in n_unique.index}
    metadata = {
        "n_rows": int(n_rows),
        "n_cols": int(n_cols),
        "n_unique": n_unique_map,
    }
    return metadata


@ltools.tool
def extract_column_profiles(path: str) -> dict:
    """
    Profile each column using value-level statistics rather than relying on
    names alone.

    Theory:
    Semantic feature inference becomes more robust when it is grounded in
    empirical column behavior. Binary flags tend to have two states, counts
    tend to be nonnegative integers, continuous measurements usually have many
    distinct real-valued observations, and identifiers often repeat but are not
    numeric measurements. These profile statistics give later stages stable
    evidence even when column names are unhelpful.

    :param path: dataset path
    :return: per-column profile map
    """
    dataset_path = pathlib.Path(path)
    dataset = load_dataset(dataset_path)
    profiles = _build_column_profiles(dataset)
    return {"column_profiles": profiles}


class _EntityCandidateArgs(pydantic.BaseModel):
    """
    Store arguments for deterministic entity-key scoring.
    """

    model_config = pydantic.ConfigDict(extra="forbid")
    path: str
    time_col: str
    candidate_cols: list[str] | None = None
    max_combo_size: int = 2


@ltools.tool(args_schema=_EntityCandidateArgs)
def score_entity_candidates(
    path: str,
    time_col: str,
    candidate_cols: list[str] | None = None,
    max_combo_size: int = 2,
) -> dict:
    """
    Score candidate entity keys by how well they partition repeated time-series
    observations into stable per-entity trajectories.

    Theory:
    A useful entity key in panel data should do three things. First, entities
    should reappear across multiple rows, otherwise the key behaves like a
    row-level identifier rather than a series identifier. Second, the pair
    `(entity_key, time_col)` should be close to unique, because that pair is
    the natural coordinate system of a panel time series. Third, a good entity
    key should explain repeated timestamps by reducing collisions once the
    entity dimension is included. These criteria are deterministic and more
    reliable than name-based guessing.

    :param path: dataset path
    :param time_col: selected time column
    :param candidate_cols: optional candidate entity columns
    :param max_combo_size: max size of composite key combinations to evaluate
    :return: scored candidate report with recommended secondary keys
    """
    dataset_path = pathlib.Path(path)
    dataset = load_dataset(dataset_path)
    if time_col not in dataset.columns:
        raise KeyError(f"time_col '{time_col}' not found in dataset")
    timestamp = pd.to_datetime(dataset[time_col], errors="coerce")
    profiles = _build_column_profiles(dataset)
    available_cols = [str(col) for col in dataset.columns if str(col) != time_col]
    if candidate_cols is None:
        selected = []
        for col in available_cols:
            profile = profiles[col]
            if profile["n_unique"] <= 1:
                continue
            if profile["unique_ratio"] >= 1.0:
                continue
            selected.append(col)
        candidate_cols = selected
    else:
        candidate_cols = [
            col for col in candidate_cols if col in dataset.columns and col != time_col
        ]
    candidate_cols = sorted(dict.fromkeys(candidate_cols))
    max_combo_size = max(1, min(int(max_combo_size), 2))
    duplicate_timestamps = int(timestamp.dropna().duplicated().sum())
    candidates: list[dict[str, Any]] = []
    for combo_size in range(1, max_combo_size + 1):
        for combo in itertools.combinations(candidate_cols, combo_size):
            subset = dataset[list(combo)].copy()
            subset["_ts"] = timestamp
            valid = subset.dropna(subset=[*combo, "_ts"])
            if valid.empty:
                continue
            group_sizes = valid.groupby(list(combo), dropna=True).size()
            if group_sizes.empty:
                continue
            n_entities = int(group_sizes.shape[0])
            mean_obs_per_entity = float(group_sizes.mean())
            entity_reuse_fraction = float((group_sizes > 1).mean())
            duplicate_pairs = int(
                valid.duplicated(subset=[*combo, "_ts"]).sum()
            )
            pair_uniqueness = float(
                1.0 - (duplicate_pairs / max(1, int(valid.shape[0])))
            )
            if duplicate_timestamps > 0:
                collision_reduction = float(
                    1.0 - (duplicate_pairs / max(1, duplicate_timestamps))
                )
            else:
                collision_reduction = 1.0 if mean_obs_per_entity > 1.0 else 0.0
            repeatability_score = float(min(max((mean_obs_per_entity - 1.0) / 4.0, 0.0), 1.0))
            score = float(
                0.35 * pair_uniqueness
                + 0.35 * repeatability_score
                + 0.20 * entity_reuse_fraction
                + 0.10 * max(0.0, min(collision_reduction, 1.0))
            )
            candidates.append(
                {
                    "secondary_keys": list(combo),
                    "n_entities": n_entities,
                    "mean_obs_per_entity": mean_obs_per_entity,
                    "entity_reuse_fraction": entity_reuse_fraction,
                    "duplicate_entity_timestamp_pairs": duplicate_pairs,
                    "pair_uniqueness": pair_uniqueness,
                    "collision_reduction": collision_reduction,
                    "score": score,
                }
            )
    candidates.sort(
        key=lambda item: (
            item["score"],
            item["entity_reuse_fraction"],
            item["mean_obs_per_entity"],
            -len(item["secondary_keys"]),
        ),
        reverse=True,
    )
    top_candidate = candidates[0] if candidates else None
    if (
        top_candidate is not None
        and top_candidate["score"] >= 0.60
        and top_candidate["n_entities"] >= 2
        and top_candidate["mean_obs_per_entity"] >= 2.0
    ):
        recommended_secondary_keys = top_candidate["secondary_keys"]
    else:
        recommended_secondary_keys = []
    return {
        "time_col": time_col,
        "duplicate_timestamps": duplicate_timestamps,
        "candidate_cols": candidate_cols,
        "candidates": candidates[:10],
        "recommended_secondary_keys": recommended_secondary_keys,
    }


class _FeatureBucketsArgs(pydantic.BaseModel):
    """
    Store arguments for deterministic semantic feature typing.
    """

    model_config = pydantic.ConfigDict(extra="forbid")
    path: str
    time_col: str
    secondary_keys: list[str] | None = None


@ltools.tool(args_schema=_FeatureBucketsArgs)
def infer_feature_buckets(
    path: str,
    time_col: str,
    secondary_keys: list[str] | None = None,
) -> dict:
    """
    Deterministically type features from their observed value behavior.

    Theory:
    The semantic distinction between counts, binary flags, continuous measures,
    and categoricals can often be established directly from the support of the
    observed values. Binary flags exhibit two states, counts live on the
    nonnegative integers, continuous measures take broader real-valued ranges,
    and categorical features are residual non-key columns that do not behave
    like numeric measurements. Weakly inferred classes such as targets or
    exogenous drivers are intentionally left empty because their meaning depends
    more on task context than on value support alone.

    :param path: dataset path
    :param time_col: selected time column
    :param secondary_keys: optional entity key columns to exclude
    :return: semantic feature buckets
    """
    dataset_path = pathlib.Path(path)
    dataset = load_dataset(dataset_path)
    profiles = _build_column_profiles(dataset)
    excluded = {time_col, *(secondary_keys or [])}
    numeric_continuous_cols: list[str] = []
    numeric_count_cols: list[str] = []
    binary_flag_cols: list[str] = []
    categorical_feature_cols: list[str] = []
    for col in [str(value) for value in dataset.columns]:
        if col in excluded:
            continue
        profile = profiles[col]
        if profile["is_binary_like"]:
            binary_flag_cols.append(col)
        elif (
            profile["is_numeric_like"]
            and profile["is_integer_like"]
            and profile["is_nonnegative_like"]
            and profile["n_unique"] > 2
        ):
            numeric_count_cols.append(col)
        elif profile["is_numeric_like"]:
            numeric_continuous_cols.append(col)
        else:
            categorical_feature_cols.append(col)
    covariate_cols = (
        numeric_continuous_cols
        + numeric_count_cols
        + binary_flag_cols
        + categorical_feature_cols
    )
    return {
        "numeric_continuous_cols": numeric_continuous_cols,
        "numeric_count_cols": numeric_count_cols,
        "binary_flag_cols": binary_flag_cols,
        "categorical_feature_cols": categorical_feature_cols,
        "known_exogenous_cols": [],
        "target_cols": [],
        "covariate_cols": covariate_cols,
        "column_profiles": profiles,
    }


@ltools.tool
def extract_head(path: str, *, n: int = 5) -> dict:
    """
    Return the first rows from a dataset.

    :param path: dataset path
    :param n: number of rows to return
    :return: head rows serialized as JSON-compatible payload
    """
    dataset_path = pathlib.Path(path)
    dataset = load_dataset(dataset_path)
    n_rows = int(n)
    if n_rows <= 0:
        n_rows = 5
    n_rows = min(n_rows, 50)
    head = dataset.head(n_rows)
    rows = json.loads(head.to_json(orient="records", date_format="iso"))
    payload = {
        "n": n_rows,
        "columns": [str(col) for col in head.columns.tolist()],
        "rows": rows,
    }
    return payload
