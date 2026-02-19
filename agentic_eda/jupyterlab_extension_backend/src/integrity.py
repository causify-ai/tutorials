import src.handle_inputs as handle_inputs
import src.format_datetime as format_datetime
import pandas as pd
import numpy as np
from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from pathlib import Path
from tools.input_tools import load_dataset
from config.config import get_chat_model
from pydantic import BaseModel
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage


class IntegrityState(TypedDict):
    path: str
    time_col: str
    winner_formatter: dict
    entity_col: str | None
    numeric_cols: list[str]
    nonnegative_cols: list[str]
    jump_mult: float
    report: dict
    summary: str
    flag: str


class IntegrityJudgeOutput(BaseModel):
    summary: str
    flag: Literal["yes", "no"]


def call_date_formatter(state: IntegrityState) -> dict:
    out: format_datetime.DateFormatterState = format_datetime.graph.invoke(  # type: ignore
        {"path": state["path"]} #type:ignore
    )
    return {"time_col": out["time_col"], "winner_formatter": out["winner_formatter"]}

def _maybe_infer_columns(state: IntegrityState) -> dict:
    if state.get("numeric_cols"):
        return {}
    out = handle_inputs.run_input_handler(state["path"])
    numeric_cols = out.get("numeric_val_cols") or []
    return {"numeric_cols": numeric_cols}


def run_integrity_checks(state: IntegrityState) -> dict:
    path = Path(state["path"])
    df = load_dataset(path)

    issues: list[dict] = []
    summary: dict = {
        "n_rows": int(df.shape[0]),
        "n_cols": int(df.shape[1]),
    }

    if df.shape[0] == 0:
        issues.append({"type": "empty_dataset", "msg": "Dataset has 0 rows"})
        return {"report": {"summary": summary, "issues": issues}}

    time_col = state.get("time_col")
    if not time_col or time_col not in df.columns:
        issues.append({"type": "missing_time_col", "msg": f"time_col missing: {time_col!r}"})
        return {"report": {"summary": summary, "issues": issues}}
    format_args = state.get("winner_formatter") or {}
    format_args = {k: v for k, v in format_args.items() if v is not None}
    try:
        ts = pd.to_datetime(df[time_col], errors="coerce", **format_args)
    except Exception:
        ts = pd.to_datetime(df[time_col], errors="coerce")
    summary["n_nat_time"] = int(ts.isna().sum())
    summary["min_time"] = None if ts.dropna().empty else str(ts.dropna().min())
    summary["max_time"] = None if ts.dropna().empty else str(ts.dropna().max())

    dup_ts = int(ts.dropna().duplicated().sum())
    summary["duplicate_timestamps"] = dup_ts
    if dup_ts > 0:
        issues.append({"type": "duplicate_timestamps", "count": dup_ts})

    entity_col = state.get("entity_col") or None
    if entity_col and entity_col in df.columns:
        summary["n_entities"] = int(df[entity_col].nunique(dropna=True))
        tmp = df[[entity_col]].copy()
        tmp["_ts"] = ts
        dup_pairs = int(tmp.dropna(subset=[entity_col, "_ts"]).duplicated(subset=[entity_col, "_ts"]).sum())
        summary["duplicate_entity_timestamp_pairs"] = dup_pairs
        if dup_pairs > 0:
            issues.append({"type": "duplicate_entity_timestamp_pairs", "count": dup_pairs})
    else:
        summary["duplicate_entity_timestamp_pairs"] = None

    numeric_cols = state.get("numeric_cols") or []
    numeric_cols = [c for c in numeric_cols if c in df.columns]

    nonnegative_cols = state.get("nonnegative_cols") or []
    neg_report: dict = {}
    for c in nonnegative_cols:
        if c not in df.columns:
            continue
        s = pd.to_numeric(df[c], errors="coerce")
        nneg = int((s < 0).sum(skipna=True))
        if nneg > 0:
            neg_report[c] = nneg
    summary["negatives_in_nonnegative_cols"] = neg_report
    if len(neg_report) > 0:
        issues.append({"type": "negative_values", "details": neg_report})

    jump_mult = float(state.get("jump_mult") or 20.0)
    jumps: dict = {}
    if numeric_cols:
        tmp = df[[time_col] + ([entity_col] if entity_col and entity_col in df.columns else []) + numeric_cols].copy()
        tmp["_ts"] = ts
        sort_cols = ["_ts"] if not (entity_col and entity_col in tmp.columns) else [entity_col, "_ts"]
        tmp = tmp.sort_values(sort_cols)

        for c in numeric_cols:
            tmp[c] = pd.to_numeric(tmp[c], errors="coerce")
            if entity_col and entity_col in tmp.columns:
                diff = tmp.groupby(entity_col)[c].diff()
            else:
                diff = tmp[c].diff()
            diff_abs = diff.abs()

            scale = diff_abs.median()
            if pd.isna(scale) or float(scale) <= 0.0:
                scale = diff_abs.mean()
            if pd.isna(scale) or float(scale) <= 0.0:
                continue

            threshold = float(scale) * float(jump_mult)
            flag = diff_abs > threshold
            n_flag = int(flag.sum(skipna=True))
            if n_flag <= 0:
                continue

            examples = []
            for i in tmp.index[flag.fillna(False)][:5]:
                d = diff.loc[i]
                curr = tmp.loc[i, c]
                prev = None if pd.isna(d) or pd.isna(curr) else float(curr - d)
                examples.append(
                    {
                        "col": c,
                        "entity": None if not (entity_col and entity_col in tmp.columns) else tmp.loc[i, entity_col],
                        "time": None if pd.isna(tmp.loc[i, "_ts"]) else str(tmp.loc[i, "_ts"]),
                        "prev": prev,
                        "curr": None if pd.isna(curr) else float(curr), #type:ignore
                        "diff": None if pd.isna(d) else float(d),
                        "threshold": float(threshold),
                    }
                )

            jumps[c] = {"count": n_flag, "threshold": threshold, "examples": examples}
            issues.append({"type": "impossible_jumps", "col": c, "count": n_flag})

    summary["jump_mult"] = float(jump_mult)
    summary["jumps"] = jumps

    return {"report": {"summary": summary, "issues": issues}}

def integrity_llm_summary(state: IntegrityState) -> dict:
    llm = get_chat_model(model="gpt-4.1")
    agent = create_agent(
        model=llm,
        tools=[],
        system_prompt="""You are an integrity judge.
You get an integrity report dict from a dataset.
Decide if everything looks normal enough to proceed.

Output format:
{ "summary": "...", "flag": "yes" or "no" }

Rules:
- flag = "yes" only if the report has no meaningful integrity issues.
- flag = "no" if there are clear issues (duplicates, impossible jumps, bad timestamps, etc.).
- Keep summary short and direct.
""",
        response_format=IntegrityJudgeOutput,
    )
    out = agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content=f"Here is the integrity report: {state['report']}"
                )
            ]
        }
    )
    sr = out["structured_response"].model_dump()
    return {"summary": sr["summary"], "flag": sr["flag"]}


integrity = StateGraph(IntegrityState)
integrity.add_node("date_formatter", call_date_formatter)
integrity.add_node("maybe_infer_columns", _maybe_infer_columns)
integrity.add_node("integrity", run_integrity_checks)
integrity.add_node("integrity_llm_summary", integrity_llm_summary)
integrity.add_edge(START, "date_formatter")
integrity.add_edge("date_formatter", "maybe_infer_columns")
integrity.add_edge("maybe_infer_columns", "integrity")
integrity.add_edge("integrity", "integrity_llm_summary")
integrity.add_edge("integrity_llm_summary", END)
graph = integrity.compile()


def run_integrity(path: str, time_col: str | None = None, entity_col: str | None = None):
    init: IntegrityState = {  # type: ignore
        "path": path,
        "time_col": time_col, #type:ignore
        "winner_formatter": {},
        "entity_col": entity_col,
        "numeric_cols": [],
        "nonnegative_cols": [],
        "jump_mult": 20.0,
    }
    out = graph.invoke(init)
    print(out["report"])
    print({"summary": out["summary"], "flag": out["flag"]})
    return {"report": out["report"], "summary": out["summary"], "flag": out["flag"]}


if __name__ == "__main__":
    run_integrity("datasets/T1_slice.csv")
