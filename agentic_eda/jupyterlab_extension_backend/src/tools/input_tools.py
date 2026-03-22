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
import pandas as pd
import pydantic

_VALID_HEADER_START_RE = re.compile(r"^[A-Za-z_]")


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
    trace_root = pathlib.Path(__file__).resolve().parents[1] / "traces"
    trace_root.mkdir(parents=True, exist_ok=True)
    filename = f"{dataset_path.stem}.{stage}.json"
    trace_path = trace_root / filename
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
