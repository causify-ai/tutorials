"""
Import as:

import src.ingest.integrity as sinteg
"""

import logging
import pathlib
from typing import Literal
from typing import TypedDict

import langchain.agents as lagents
import langchain_core.messages as lmessages
import langgraph.graph as lgraph
import pandas as pd
import pydantic

import src.config.config as cconf
import src.ingest.format_datetime as sfordat
import src.ingest.handle_inputs as shainp
import src.ingest.infer_type as sinfert
import src.tools.input_tools as tinptool

_LOG = logging.getLogger(__name__)


class IntegrityState(TypedDict):
    """
    Store graph state for integrity checks.
    """

    path: str
    time_col: str | None
    winner_formatter: dict
    cols: list[str]
    temporal_cols: list[str]
    bad_rows: list[dict]
    entity_col: str | None
    numeric_cols: list[str]
    categorical_val_cols: list[str]
    metadata: dict
    secondary_keys: list[str]
    nonnegative_cols: list[str]
    jump_mult: float
    report: dict
    summary: str
    flag: str


class IntegrityJudgeOutput(pydantic.BaseModel):
    """
    Store structured LLM judgment.
    """

    summary: str
    flag: Literal["yes", "no"]


def call_date_formatter(state: IntegrityState) -> dict:
    """
    Run the datetime formatter graph.

    :param state: integrity graph state
    :return: selected time column and formatter
    """
    out: sfordat.DateFormatterState = sfordat.graph.invoke(  # type: ignore
        {"path": state["path"]}
    )
    payload = {
        "time_col": out["time_col"],
        "winner_formatter": out["winner_formatter"],
    }
    return payload


def _maybe_infer_columns(state: IntegrityState) -> dict:
    """
    Collect schema context needed by downstream integrity checks.

    :param state: integrity graph state
    :return: schema-related state updates
    """
    if (
        state.get("cols")
        and state.get("temporal_cols")
        and state.get("numeric_cols")
        and state.get("metadata")
    ):
        payload = {}
    else:
        dataset_path = pathlib.Path(state["path"])
        dataset = tinptool.load_dataset(dataset_path)
        out = shainp.run_input_handler(state["path"])
        metadata = tinptool.extract_metadata.invoke({"path": state["path"]})
        payload = {
            "cols": [str(col) for col in dataset.columns.tolist()],
            "temporal_cols": out.get("temporal_cols") or [],
            "bad_rows": out.get("bad_rows") or [],
            "numeric_cols": out.get("numeric_val_cols") or [],
            "categorical_val_cols": out.get("categorical_val_cols") or [],
            "metadata": metadata,
        }
    return payload


def call_infer_type(state: IntegrityState) -> dict:
    """
    Infer the series structure and derive the temporary entity key.

    :param state: integrity graph state
    :return: inferred secondary keys and first entity key
    """
    infer_state: sinfert.CompositeState = {
        "path": state["path"],
        "cols": state.get("cols") or [],
        "temporal_cols": state.get("temporal_cols") or [],
        "numeric_val_cols": state.get("numeric_cols") or [],
        "categorical_val_cols": state.get("categorical_val_cols") or [],
        "bad_rows": state.get("bad_rows") or [],
        "metadata": state.get("metadata") or {},
        "time_col": state["time_col"] or "",
        "done": [],
        "has_header": True,
        "has_missing_values": False,
        "error": "",
        "info": "",
        "candidates": [],
        "winner_formatter": state.get("winner_formatter") or {},
        "entity_col": None,
        "numeric_cols": state.get("numeric_cols") or [],
        "nonnegative_cols": [],
        "jump_mult": 20.0,
        "report": {},
        "summary": "",
        "flag": "",
        "type": "single",
        "primary_key": "",
        "secondary_keys": [],
    }
    out = sinfert.infer_type(infer_state)
    secondary_keys = out.get("secondary_keys") or []
    entity_col = secondary_keys[0] if secondary_keys else None
    payload = {
        "secondary_keys": secondary_keys,
        "entity_col": entity_col,
    }
    return payload


def run_integrity_checks(state: IntegrityState) -> dict:
    """
    Run deterministic integrity checks on a dataset.

    :param state: integrity graph state
    :return: report payload
    """
    dataset_path = pathlib.Path(state["path"])
    dataset = tinptool.load_dataset(dataset_path)
    issues: list[dict] = []
    summary: dict = {
        "n_rows": int(dataset.shape[0]),
        "n_cols": int(dataset.shape[1]),
    }
    if dataset.shape[0] == 0:
        issues.append({"type": "empty_dataset", "msg": "Dataset has 0 rows."})
        report = {"summary": summary, "issues": issues}
        payload = {"report": report}
        return payload
    time_col = state.get("time_col")
    if time_col is None or time_col not in dataset.columns:
        issues.append(
            {
                "type": "missing_time_col",
                "msg": f"time_col missing: {time_col!r}",
            }
        )
        report = {"summary": summary, "issues": issues}
        payload = {"report": report}
        return payload
    format_args = state.get("winner_formatter") or {}
    format_args = {
        key: val
        for key, val in format_args.items()
        if val is not None
    }
    try:
        timestamp = pd.to_datetime(
            dataset[time_col],
            errors="coerce",
            **format_args,
        )
    except Exception:
        timestamp = pd.to_datetime(dataset[time_col], errors="coerce")
    summary["n_nat_time"] = int(timestamp.isna().sum())
    summary["min_time"] = (
        None if timestamp.dropna().empty else str(timestamp.dropna().min())
    )
    summary["max_time"] = (
        None if timestamp.dropna().empty else str(timestamp.dropna().max())
    )
    duplicate_timestamps = int(timestamp.dropna().duplicated().sum())
    summary["duplicate_timestamps"] = duplicate_timestamps
    if duplicate_timestamps > 0:
        issues.append(
            {"type": "duplicate_timestamps", "count": duplicate_timestamps}
        )
    entity_col = state.get("entity_col")
    # TODO: Use all inferred secondary_keys as a composite entity key for
    # integrity checks; for now we temporarily use only the first key.
    if entity_col is not None and entity_col in dataset.columns:
        summary["n_entities"] = int(dataset[entity_col].nunique(dropna=True))
        tmp = dataset[[entity_col]].copy()
        tmp["_ts"] = timestamp
        duplicate_pairs = int(
            tmp.dropna(subset=[entity_col, "_ts"])
            .duplicated(subset=[entity_col, "_ts"])
            .sum()
        )
        summary["duplicate_entity_timestamp_pairs"] = duplicate_pairs
        if duplicate_pairs > 0:
            issues.append(
                {
                    "type": "duplicate_entity_timestamp_pairs",
                    "count": duplicate_pairs,
                }
            )
    else:
        summary["duplicate_entity_timestamp_pairs"] = None
    numeric_cols = [col for col in state.get("numeric_cols") or []]
    numeric_cols = [col for col in numeric_cols if col in dataset.columns]
    nonnegative_cols = [col for col in state.get("nonnegative_cols") or []]
    negative_report: dict = {}
    for col in nonnegative_cols:
        if col not in dataset.columns:
            continue
        series = pd.to_numeric(dataset[col], errors="coerce")
        n_negative = int((series < 0).sum(skipna=True))
        if n_negative > 0:
            negative_report[col] = n_negative
    summary["negatives_in_nonnegative_cols"] = negative_report
    if negative_report:
        issues.append({"type": "negative_values", "details": negative_report})
    jump_mult = float(state.get("jump_mult") or 20.0)
    jumps: dict = {}
    if numeric_cols:
        selected_cols = [time_col]
        if entity_col is not None and entity_col in dataset.columns:
            selected_cols.append(entity_col)
        selected_cols.extend(numeric_cols)
        tmp = dataset[selected_cols].copy()
        tmp["_ts"] = timestamp
        if entity_col is None or entity_col not in tmp.columns:
            sort_cols = ["_ts"]
        else:
            sort_cols = [entity_col, "_ts"]
        tmp = tmp.sort_values(sort_cols)
        for col in numeric_cols:
            tmp[col] = pd.to_numeric(tmp[col], errors="coerce")
            if entity_col is None or entity_col not in tmp.columns:
                diff = tmp[col].diff()
            else:
                diff = tmp.groupby(entity_col)[col].diff()
            diff_abs = diff.abs()
            scale = diff_abs.median()
            if pd.isna(scale) or float(scale) <= 0.0:
                scale = diff_abs.mean()
            if pd.isna(scale) or float(scale) <= 0.0:
                continue
            threshold = float(scale) * jump_mult
            flagged = diff_abs > threshold
            n_flagged = int(flagged.sum(skipna=True))
            if n_flagged <= 0:
                continue
            examples: list[dict] = []
            flagged_idx = tmp.index[flagged.fillna(False)][:5]
            for idx in flagged_idx:
                diff_val = diff.loc[idx]
                curr_val = tmp.loc[idx, col]
                if pd.isna(diff_val) or pd.isna(curr_val):
                    prev_val = None
                else:
                    prev_val = float(curr_val - diff_val)
                example = {
                    "col": col,
                    "entity": (
                        None
                        if entity_col is None or entity_col not in tmp.columns
                        else tmp.loc[idx, entity_col]
                    ),
                    "time": (
                        None
                        if pd.isna(tmp.loc[idx, "_ts"])
                        else str(tmp.loc[idx, "_ts"])
                    ),
                    "prev": prev_val,
                    "curr": None if pd.isna(curr_val) else float(curr_val),
                    "diff": None if pd.isna(diff_val) else float(diff_val),
                    "threshold": float(threshold),
                }
                examples.append(example)
            jumps[col] = {
                "count": n_flagged,
                "threshold": threshold,
                "examples": examples,
            }
            issues.append(
                {
                    "type": "impossible_jumps",
                    "col": col,
                    "count": n_flagged,
                }
            )
    summary["jump_mult"] = jump_mult
    summary["jumps"] = jumps
    report = {"summary": summary, "issues": issues}
    payload = {"report": report}
    return payload


def integrity_llm_summary(state: IntegrityState) -> dict:
    """
    Summarize integrity report and provide go/no-go flag.

    :param state: integrity graph state
    :return: summary and decision flag
    """
    llm = cconf.get_chat_model(model="gpt-4.1")
    agent = lagents.create_agent(
        model=llm,
        tools=[],
        system_prompt=(
            "You are an integrity judge. Decide if the dataset can proceed. "
            "Return JSON with keys summary and flag. Set flag to yes only when "
            "there are no meaningful integrity issues."
        ),
        response_format=IntegrityJudgeOutput,
    )
    out = agent.invoke(
        {
            "messages": [
                lmessages.HumanMessage(
                    content=f"Here is the integrity report: {state['report']}"
                )
            ]
        }
    )
    structured_response = out["structured_response"].model_dump()
    payload = {
        "summary": structured_response["summary"],
        "flag": structured_response["flag"],
    }
    return payload


integrity = lgraph.StateGraph(IntegrityState)
integrity.add_node("date_formatter", call_date_formatter)
integrity.add_node("maybe_infer_columns", _maybe_infer_columns)
integrity.add_node("infer_type", call_infer_type)
integrity.add_node("run_integrity_checks", run_integrity_checks)
integrity.add_node("integrity_llm_summary", integrity_llm_summary)
integrity.add_edge(lgraph.START, "date_formatter")
integrity.add_edge("date_formatter", "maybe_infer_columns")
integrity.add_edge("maybe_infer_columns", "infer_type")
integrity.add_edge("infer_type", "run_integrity_checks")
integrity.add_edge("run_integrity_checks", "integrity_llm_summary")
integrity.add_edge("integrity_llm_summary", lgraph.END)
graph = integrity.compile()


def run_integrity(path: str) -> dict:
    """
    Execute integrity graph end to end.

    :param path: dataset path
    :return: integrity report with summary and flag
    """
    init_state: IntegrityState = {
        "path": path,
        "time_col": None,
        "winner_formatter": {},
        "cols": [],
        "temporal_cols": [],
        "bad_rows": [],
        "entity_col": None,
        "numeric_cols": [],
        "categorical_val_cols": [],
        "metadata": {},
        "secondary_keys": [],
        "nonnegative_cols": [],
        "jump_mult": 20.0,
        "report": {},
        "summary": "",
        "flag": "",
    }
    out = graph.invoke(init_state)
    payload = {
        "report": out["report"],
        "summary": out["summary"],
        "flag": out["flag"],
    }
    _LOG.info("Integrity output: %s", payload)
    return payload
