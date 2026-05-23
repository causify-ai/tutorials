"""
Import as:

import src.ingest.handle_inputs as shainp
"""

from __future__ import annotations

import argparse
import logging
import pathlib
from typing import Any
from typing import Literal
from typing import TypedDict

import langchain.agents as lagents
import langchain_core.messages as lmessages
import langgraph.graph as lgraph
import pandas as pd
import pydantic

import src.config.config as cconf
import src.tools.input_tools as tinptool

_LOG = logging.getLogger(__name__)


class InputState(TypedDict):
    """
    Store graph state for input checks.
    """

    path: str | pathlib.Path
    done: list[str]
    has_header: bool
    has_missing_values: bool
    error: str
    info: str
    cols: list[str]
    temporal_cols: list[str]
    numeric_val_cols: list[str]
    categorical_val_cols: list[str]
    bad_rows: list[dict]


class LLMOutput(pydantic.BaseModel):
    """
    Store structured output from the header classifier.
    """

    temporal_cols: list[str]
    numeric_val_cols: list[str]
    categorical_val_cols: list[str]


class SeriesStructureFallbackOutput(pydantic.BaseModel):
    """
    Store structured fallback output for ambiguous series-structure cases.
    """

    model_config = pydantic.ConfigDict(extra="forbid")
    secondary_keys: list[str]


class BadRowDescriptor(pydantic.BaseModel):
    """
    Store one fuzzy descriptor for a bad row.
    """

    model_config = pydantic.ConfigDict(extra="forbid")
    row_index: int
    fuzzy_descriptor: str


class BadRowDescriptorOutput(pydantic.BaseModel):
    """
    Store structured fuzzy descriptors for detected bad rows.
    """

    model_config = pydantic.ConfigDict(extra="forbid")
    descriptors: list[BadRowDescriptor]


class SeriesStructureAssessment(TypedDict):
    """
    Store deterministic and fallback evidence for series-structure inference.
    """

    duplicate_timestamps: int
    duplicate_timestamp_fraction: float
    timestamps_mostly_unique: bool
    candidate_entity_cols: list[str]
    entity_candidate_report: dict
    secondary_keys: list[str]
    confidence: Literal["high", "medium", "low"]
    method: Literal["deterministic", "deterministic_no_panel", "fuzzy"]


def _json_safe_value(value: Any) -> Any:
    """
    Convert dataframe cell values into JSON-safe Python values.

    :param value: raw cell value
    :return: JSON-safe value
    """
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            return str(value)
    return value


def _row_to_record(row: pd.Series) -> dict[str, Any]:
    """
    Convert one dataframe row into a JSON-safe mapping.

    :param row: dataframe row
    :return: serialized row mapping
    """
    return {
        str(col): _json_safe_value(value)
        for col, value in row.to_dict().items()
    }


def detect_bad_rows(state: InputState) -> dict:
    """
    Detect rows that do not behave like observations because their temporal
    fields are missing or unparseable.

    Theory:
    In time-series ingestion, observation rows should participate in the time
    axis. Rows whose temporal fields cannot be parsed are often metadata,
    annotation, footer, or malformed rows. Capturing them explicitly preserves
    evidence for downstream handling without silently dropping information at
    ingestion time.

    :param state: input graph state
    :return: detected bad-row payload
    """
    temporal_cols = state.get("temporal_cols") or []
    if not temporal_cols:
        return {"bad_rows": []}

    dataset_path = pathlib.Path(str(state["path"]))
    dataset = tinptool.load_dataset(dataset_path)
    valid_temporal_cols = [col for col in temporal_cols if col in dataset.columns]
    if not valid_temporal_cols:
        return {"bad_rows": []}

    parse_matrix: dict[str, pd.Series] = {}
    normalized_matrix: dict[str, pd.Series] = {}
    for col in valid_temporal_cols:
        raw_series = dataset[col]
        normalized = raw_series.astype(str).str.strip().replace(
            {"": pd.NA, "nan": pd.NA, "NaT": pd.NA}
        )
        normalized_matrix[col] = normalized
        parse_matrix[col] = pd.to_datetime(normalized, errors="coerce")

    bad_rows: list[dict[str, Any]] = []
    for row_idx in range(int(dataset.shape[0])):
        reasons: list[str] = []
        temporal_values: dict[str, Any] = {}
        has_temporal_signal = False
        has_parseable_temporal = False
        for col in valid_temporal_cols:
            raw_value = normalized_matrix[col].iloc[row_idx]
            parsed_value = parse_matrix[col].iloc[row_idx]
            temporal_values[col] = _json_safe_value(raw_value)
            if not pd.isna(raw_value):
                has_temporal_signal = True
            if not pd.isna(parsed_value):
                has_parseable_temporal = True
                continue
            if pd.isna(raw_value):
                reasons.append(f"missing_temporal_value:{col}")
            else:
                raw_text = str(raw_value).strip()
                reasons.append(f"unparseable_temporal_value:{col}")
                if raw_text.endswith(":"):
                    reasons.append(f"annotation_like_temporal_value:{col}")
        if has_parseable_temporal:
            continue
        if not has_temporal_signal and not reasons:
            continue
        row = dataset.iloc[row_idx]
        bad_rows.append(
            {
                "row_index": int(row_idx),
                "csv_row_number": int(row_idx) + 2,
                "temporal_values": temporal_values,
                "reasons": sorted(dict.fromkeys(reasons)),
                "raw_row": _row_to_record(row),
                "fuzzy_descriptor": "",
            }
        )
    return {"bad_rows": bad_rows}


def describe_bad_rows(state: InputState) -> dict:
    """
    Attach short fuzzy descriptors to already-detected bad rows.

    Theory:
    Deterministic rules can reliably tell us that a row does not behave like a
    data observation, but they are less expressive about the row's likely role.
    A constrained model can add a short human-readable descriptor such as
    metadata row, blank footer row, or malformed timestamp row without being
    allowed to invent new row IDs or alter the deterministic evidence.

    :param state: input graph state
    :return: bad rows with fuzzy descriptors
    """
    bad_rows = [dict(row) for row in (state.get("bad_rows") or [])]
    if not bad_rows:
        return {"bad_rows": []}

    llm = cconf.get_chat_model(model="gpt-4.1")
    agent = lagents.create_agent(
        model=llm,
        tools=[],
        system_prompt=(
            "You are labeling already-detected bad rows in a dataset. "
            "For each row_index, return a short fuzzy descriptor such as "
            "'metadata/control row', 'blank/incomplete row', "
            "'annotation row', or 'malformed timestamp row'. "
            "Do not change row_index values and do not add rows."
        ),
        response_format=BadRowDescriptorOutput,
    )
    out = agent.invoke(
        {
            "messages": [
                lmessages.HumanMessage(
                    content=f"Detected bad rows: {bad_rows}"
                )
            ]
        }
    )
    descriptors = out["structured_response"].model_dump().get("descriptors") or []
    descriptor_map = {
        int(item["row_index"]): str(item["fuzzy_descriptor"]).strip()
        for item in descriptors
    }
    for row in bad_rows:
        row["fuzzy_descriptor"] = descriptor_map.get(
            int(row["row_index"]),
            "bad/non-data row",
        )
    return {"bad_rows": bad_rows}


def _parse_time_series(
    path: str | pathlib.Path,
    time_col: str,
    winner_formatter: dict | None = None,
) -> pd.Series:
    """
    Parse a proposed time column to measure whether it behaves like a real time
    axis.

    Theory:
    Handle-input classification identifies candidate temporal columns, but it
    does not establish whether the observed values actually parse into a stable
    datetime axis. Parseability is the empirical question: can the values be
    converted into usable timestamps with only a small failure rate? That check
    is important because schema inference should rely on observed value
    behavior, not just column labels or LLM guesses.

    :param path: dataset path
    :param time_col: selected time column
    :param winner_formatter: optional datetime parsing kwargs
    :return: parsed timestamp series
    """
    dataset = tinptool.load_dataset(pathlib.Path(str(path)))
    format_args = winner_formatter or {}
    format_args = {key: val for key, val in format_args.items() if val is not None}
    try:
        return pd.to_datetime(dataset[time_col], errors="coerce", **format_args)
    except Exception:
        return pd.to_datetime(dataset[time_col], errors="coerce")


def _select_entity_candidate_cols(
    *,
    cols: list[str],
    time_col: str,
    numeric_val_cols: list[str],
    categorical_val_cols: list[str],
    column_profiles: dict,
) -> list[str]:
    """
    Select plausible entity-key candidates using value-level heuristics.

    Theory:
    Entity keys should behave like identifiers that partition repeated
    timestamps into coherent per-entity series. Measurement columns usually do
    not do that, even if they repeat. The candidate filter therefore keeps
    likely identifier-like categoricals and only a narrow class of integer-like
    numeric columns, while excluding continuous measurements, binary flags, and
    near-row-unique columns.

    :param cols: all dataset columns
    :param time_col: selected time column
    :param numeric_val_cols: numeric value columns
    :param categorical_val_cols: categorical value columns
    :param column_profiles: per-column deterministic profiles
    :return: filtered candidate entity columns
    """
    candidates: list[str] = []
    numeric_set = set(numeric_val_cols)
    categorical_set = set(categorical_val_cols)
    for col in cols:
        if col == time_col:
            continue
        profile = column_profiles.get(col) or {}
        n_unique = int(profile.get("n_unique", 0))
        unique_ratio = float(profile.get("unique_ratio", 1.0))
        if n_unique <= 1 or unique_ratio >= 0.95:
            continue
        if col in categorical_set:
            candidates.append(col)
            continue
        if col in numeric_set:
            if bool(profile.get("is_binary_like")):
                continue
            if not bool(profile.get("is_integer_like")):
                continue
            if not bool(profile.get("is_nonnegative_like")):
                continue
            if n_unique > 200:
                continue
            if unique_ratio > 0.50:
                continue
            candidates.append(col)
    return candidates


def _fuzzy_secondary_key_agent(
    *,
    path: str,
    time_col: str,
    candidate_entity_cols: list[str],
    entity_candidate_report: dict,
    column_profiles: dict,
) -> list[str]:
    """
    Resolve ambiguous panel-vs-multivariate cases with a constrained LLM tie
    breaker.

    Theory:
    Deterministic heuristics are strongest when the data exhibits clean
    identifier behavior. Ambiguous cases remain, especially when columns are
    poorly named or identifier-like columns are partially numeric. In those
    cases, a model can act as a constrained judge over a narrow candidate set,
    using deterministic evidence rather than inventing columns freely. This
    keeps fuzzy reasoning explainable and bounded.

    :param path: dataset path
    :param time_col: selected time column
    :param candidate_entity_cols: filtered entity-key candidates
    :param entity_candidate_report: deterministic scoring report
    :param column_profiles: per-column profiles
    :return: chosen secondary keys, possibly empty
    """
    if not candidate_entity_cols:
        return []
    llm = cconf.get_chat_model(model="gpt-4.1")
    agent = lagents.create_agent(
        model=llm,
        tools=[tinptool.extract_head, tinptool.extract_metadata],
        system_prompt=(
            "You are resolving an ambiguous series-structure classification. "
            "Choose secondary keys only from the provided candidate_entity_cols. "
            "Return [] if the dataset still looks like a single or wide "
            "multivariate time series rather than panel data. Prefer the "
            "deterministic evidence report over column names."
        ),
        response_format=SeriesStructureFallbackOutput,
    )
    profile_subset = {
        col: column_profiles.get(col, {})
        for col in candidate_entity_cols
    }
    out = agent.invoke(
        {
            "messages": [
                lmessages.HumanMessage(
                    content=(
                        f"Dataset path: {path}\n"
                        f"time_col: {time_col}\n"
                        f"candidate_entity_cols: {candidate_entity_cols}\n"
                        f"entity_candidate_report: {entity_candidate_report}\n"
                        f"column_profiles: {profile_subset}"
                    )
                )
            ]
        }
    )
    structured = out["structured_response"].model_dump()
    secondary_keys: list[str] = []
    seen: set[str] = set()
    allowed = set(candidate_entity_cols)
    for col in structured.get("secondary_keys") or []:
        col_name = str(col)
        if col_name not in allowed or col_name in seen:
            continue
        seen.add(col_name)
        secondary_keys.append(col_name)
    return secondary_keys


def assess_series_structure(
    *,
    path: str | pathlib.Path,
    cols: list[str],
    time_col: str,
    numeric_val_cols: list[str],
    categorical_val_cols: list[str],
    winner_formatter: dict | None = None,
) -> SeriesStructureAssessment:
    """
    Assess whether the dataset behaves like a single series, panel, or wide
    multivariate time series.

    Theory:
    The decisive signal for panel structure is not the column name but the time
    axis itself. If timestamps are already mostly unique, there is no need to
    search for entity keys: the data is behaving like one wide time-indexed
    table. Only when timestamps repeat meaningfully should we look for
    identifier columns that make `(entity, time)` close to unique. This staging
    avoids promoting ordinary measurement columns into fake entity IDs.

    :param path: dataset path
    :param cols: all dataset columns
    :param time_col: selected time column
    :param numeric_val_cols: numeric value columns
    :param categorical_val_cols: categorical value columns
    :param winner_formatter: optional datetime parsing kwargs
    :return: series-structure assessment
    """
    string_path = str(path)
    timestamp = _parse_time_series(string_path, time_col, winner_formatter)
    valid_ts = timestamp.dropna()
    duplicate_timestamps = int(valid_ts.duplicated().sum())
    duplicate_fraction = (
        0.0 if valid_ts.empty else float(duplicate_timestamps / max(1, int(valid_ts.shape[0])))
    )
    timestamps_mostly_unique = duplicate_timestamps == 0 or duplicate_fraction < 0.01
    profiles_out = tinptool.extract_column_profiles.invoke({"path": string_path})
    column_profiles = profiles_out.get("column_profiles") or {}
    candidate_entity_cols = _select_entity_candidate_cols(
        cols=cols,
        time_col=time_col,
        numeric_val_cols=numeric_val_cols,
        categorical_val_cols=categorical_val_cols,
        column_profiles=column_profiles,
    )
    if timestamps_mostly_unique:
        return {
            "duplicate_timestamps": duplicate_timestamps,
            "duplicate_timestamp_fraction": duplicate_fraction,
            "timestamps_mostly_unique": True,
            "candidate_entity_cols": [],
            "entity_candidate_report": {
                "time_col": time_col,
                "candidate_cols": [],
                "candidates": [],
                "recommended_secondary_keys": [],
            },
            "secondary_keys": [],
            "confidence": "high",
            "method": "deterministic_no_panel",
        }
    entity_candidate_report = tinptool.score_entity_candidates.invoke(
        {
            "path": string_path,
            "time_col": time_col,
            "candidate_cols": candidate_entity_cols,
            "max_combo_size": 2,
        }
    )
    recommended_secondary_keys = (
        entity_candidate_report.get("recommended_secondary_keys") or []
    )
    candidates = entity_candidate_report.get("candidates") or []
    top_score = 0.0 if not candidates else float(candidates[0].get("score", 0.0))
    if recommended_secondary_keys:
        confidence: Literal["high", "medium", "low"] = (
            "high" if top_score >= 0.75 else "medium"
        )
        return {
            "duplicate_timestamps": duplicate_timestamps,
            "duplicate_timestamp_fraction": duplicate_fraction,
            "timestamps_mostly_unique": False,
            "candidate_entity_cols": candidate_entity_cols,
            "entity_candidate_report": entity_candidate_report,
            "secondary_keys": recommended_secondary_keys,
            "confidence": confidence,
            "method": "deterministic",
        }
    fuzzy_secondary_keys = _fuzzy_secondary_key_agent(
        path=string_path,
        time_col=time_col,
        candidate_entity_cols=candidate_entity_cols,
        entity_candidate_report=entity_candidate_report,
        column_profiles=column_profiles,
    )
    return {
        "duplicate_timestamps": duplicate_timestamps,
        "duplicate_timestamp_fraction": duplicate_fraction,
        "timestamps_mostly_unique": False,
        "candidate_entity_cols": candidate_entity_cols,
        "entity_candidate_report": entity_candidate_report,
        "secondary_keys": fuzzy_secondary_keys,
        "confidence": "low" if fuzzy_secondary_keys else "medium",
        "method": "fuzzy",
    }


def header_classification_agent(state: InputState) -> dict:
    """
    Classify temporal, numeric, and categorical columns.

    :param state: input graph state
    :return: column classification payload
    """
    llm = cconf.get_chat_model(model="gpt-4.1")
    agent = lagents.create_agent(
        model=llm,
        tools=[tinptool.extract_head, tinptool.extract_metadata],
        system_prompt=(
            "You are a header classifier agent. Use tools to identify temporal "
            "columns and classify the remaining value columns as numeric or "
            "categorical. Output JSON with keys temporal_cols, "
            "numeric_val_cols, and categorical_val_cols."
        ),
        response_format=LLMOutput,
    )
    out = agent.invoke(
        {
            "messages": [
                lmessages.HumanMessage(
                    content=f"The dataset is in {state['path']}"
                )
            ]
        }
    )
    result = out["structured_response"].model_dump()
    return result


def error_node(state: InputState) -> dict:
    """
    Log an error node transition.

    :param state: input graph state
    :return: empty update
    """
    _LOG.error("Input handler failed: %s", state["error"])
    return {}


def has_header(state: InputState) -> bool:
    """
    Check if header validation passed.

    :param state: input graph state
    :return: true when headers are valid
    """
    has_header_flag = state["has_header"]
    return has_header_flag


def run_input_handler(path: str | pathlib.Path) -> dict:
    """
    Run dataset header and column classification checks.

    :param path: path to dataset
    :return: final graph output
    """
    graph_builder = lgraph.StateGraph(InputState)
    graph_builder.add_node("header_analysis", tinptool.analyze_header)
    graph_builder.add_node(
        "header_classification_agent",
        header_classification_agent,
    )
    graph_builder.add_node("detect_bad_rows", detect_bad_rows)
    graph_builder.add_node("describe_bad_rows", describe_bad_rows)
    graph_builder.add_node("error", error_node)
    graph_builder.add_edge(lgraph.START, "header_analysis")
    graph_builder.add_conditional_edges(
        "header_analysis",
        has_header,
        {
            True: "header_classification_agent",
            False: "error",
        },
    )
    graph_builder.add_edge("error", lgraph.END)
    graph_builder.add_edge("header_classification_agent", "detect_bad_rows")
    graph_builder.add_edge("detect_bad_rows", "describe_bad_rows")
    graph_builder.add_edge("describe_bad_rows", lgraph.END)
    graph = graph_builder.compile()
    init_state: InputState = {
        "path": str(path),
        "done": [],
        "has_header": True,
        "has_missing_values": False,
        "error": "",
        "info": "",
        "cols": [],
        "temporal_cols": [],
        "numeric_val_cols": [],
        "categorical_val_cols": [],
        "bad_rows": [],
    }
    out = graph.invoke(init_state)
    _LOG.info("Input handler output: %s", out)
    return out


def _parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    :return: parsed arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        required=True,
        help="Path to dataset file.",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    args = _parse_args()
    run_input_handler(args.path)
