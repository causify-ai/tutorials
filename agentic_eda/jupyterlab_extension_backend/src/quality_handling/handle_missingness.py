"""
Import as:

import src.quality_handling.handle_missingness as shandlemiss
"""

from __future__ import annotations

import argparse
import logging
from typing import Literal
from typing import TypedDict

import langchain.agents as lagents
import langchain_core.messages as lmessages
import langgraph.graph as lgraph
import pydantic

import src.config.config as cconf
import src.quality_handling.audit_missingness as sauditmiss
import src.tools.input_tools as tinptool

_LOG = logging.getLogger(__name__)


def _build_missingness_plan_summary(actions: list[dict], *, defaulted_cols: int) -> str:
    """
    Build a summary from the normalized missingness actions.

    :param actions: normalized action list
    :param defaulted_cols: number of columns defaulted during normalization
    :return: summary text aligned with the final plan
    """
    if not actions:
        return "No non-time columns required missingness handling."
    counts: dict[str, int] = {}
    for action in actions:
        strategy = str(action["strategy"])
        counts[strategy] = counts.get(strategy, 0) + 1
    ordered_counts = ", ".join(
        f"{strategy}={counts[strategy]}"
        for strategy in sorted(counts)
    )
    summary = (
        f"Normalized missingness plan for {len(actions)} columns: {ordered_counts}. "
        "Actions reflect the final bounded plan after validation against eligible strategies."
    )
    if defaulted_cols > 0:
        summary += f" {defaulted_cols} columns were defaulted conservatively during normalization."
    return summary


class MissingnessDecision(pydantic.BaseModel):
    """
    Store one bounded missingness decision.
    """

    col: str
    strategy: Literal[
        "leave_as_nan",
        "forward_fill",
        "interpolate",
        "zero_fill",
        "drop_rows",
    ]
    create_missingness_flag: bool = True
    reason: str


class MissingnessPlanOutput(pydantic.BaseModel):
    """
    Store LLM-produced missingness plan.
    """

    summary: str
    actions: list[MissingnessDecision]


class CompositeState(TypedDict):
    """
    Store graph state for missingness handling.
    """

    path: str
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
    metadata: dict
    time_col: str
    candidates: list[dict]
    winner_formatter: dict
    entity_col: str | None
    numeric_cols: list[str]
    nonnegative_cols: list[str]
    jump_mult: float
    report: dict
    summary: str
    flag: str
    type: str
    primary_key: str
    secondary_keys: list[str]
    numeric_continuous_cols: list[str]
    numeric_count_cols: list[str]
    binary_flag_cols: list[str]
    categorical_feature_cols: list[str]
    known_exogenous_cols: list[str]
    target_cols: list[str]
    covariate_cols: list[str]
    n_nat_time: int
    min_time: str | None
    max_time: str | None
    typical_delta_mode: str | None
    typical_delta_median: str | None
    expected_frequency: str | None
    dominant_frequency_fraction: float
    is_irregular_sampling: bool
    resampling_decision: str
    coverage_summary: dict
    coverage_per_entity: list[dict]
    missingness_report: dict
    missingness_plan: dict
    missingness_handling_report: dict
    quality_dataset_path: str


def call_audit_missingness(state: CompositeState) -> dict:
    """
    Run the sequential pipeline up to missingness auditing.

    :param state: graph state
    :return: composite payload from audit_missingness
    """
    payload = sauditmiss.run_audit_missingness(state["path"])
    return payload


def _normalize_missingness_plan(state: CompositeState, raw_plan: dict) -> dict:
    """
    Ensure every missing column has one supported action.

    :param state: graph state
    :param raw_plan: LLM-produced plan
    :return: normalized deterministic plan
    """
    audit_report = state["missingness_report"]
    missing_cols = [
        item
        for item in audit_report["value_missingness_by_column"]
        if item["n_missing"] > 0 and item["col"] != state["primary_key"]
    ]
    eligible_by_col = {
        item["col"]: set(item["eligible_strategies"])
        for item in missing_cols
    }
    plan_by_col = {}
    defaulted_cols = 0
    for item in raw_plan.get("actions") or []:
        col = str(item.get("col") or "")
        if col not in eligible_by_col:
            continue
        strategy = str(item.get("strategy") or "leave_as_nan")
        if strategy not in eligible_by_col[col]:
            strategy = "leave_as_nan"
        plan_by_col[col] = {
            "col": col,
            "strategy": strategy,
            "create_missingness_flag": bool(item.get("create_missingness_flag", True)),
            "reason": str(item.get("reason") or ""),
        }
    normalized_actions = []
    for item in missing_cols:
        col = item["col"]
        action = plan_by_col.get(
            col,
            {
                "col": col,
                "strategy": "leave_as_nan",
                "create_missingness_flag": True,
                "reason": "Defaulted conservatively because no valid explicit plan was provided.",
            },
        )
        normalized_actions.append(action)
        if col not in plan_by_col:
            defaulted_cols += 1
    return {
        "summary": _build_missingness_plan_summary(
            normalized_actions,
            defaulted_cols=defaulted_cols,
        ),
        "actions": normalized_actions,
    }


def choose_missingness_plan(state: CompositeState) -> dict:
    """
    Choose bounded missingness actions using deterministic evidence.

    :param state: graph state
    :return: normalized missingness plan
    """
    missing_cols = [
        item
        for item in state["missingness_report"]["value_missingness_by_column"]
        if item["n_missing"] > 0 and item["col"] != state["primary_key"]
    ]
    if not missing_cols:
        payload = {
            "missingness_plan": {
                "summary": "No non-time columns contain missing values requiring handling.",
                "actions": [],
            }
        }
        return payload
    llm = cconf.get_chat_model(model="gpt-4.1")
    agent = lagents.create_agent(
        model=llm,
        tools=[],
        system_prompt=(
            "You are a missingness planner for a time-series EDA backend. "
            "Choose exactly one bounded strategy per column with missing values. "
            "Allowed strategies are leave_as_nan, forward_fill, interpolate, "
            "zero_fill, and drop_rows. Prefer conservative choices when the "
            "evidence is weak. Use zero_fill only for true count-like variables "
            "where structural zeros are plausible. Use interpolate only for "
            "numeric columns. Use forward_fill for stateful or slowly varying "
            "features when continuity is plausible. Missing timestamps are a "
            "separate issue from missing cell values; do not pretend that a cell "
            "imputation solves timestamp holes."
        ),
        response_format=MissingnessPlanOutput,
    )
    evidence = {
        "series_type": state["type"],
        "expected_frequency": state["expected_frequency"],
        "is_irregular_sampling": state["is_irregular_sampling"],
        "timestamp_missingness_summary": state["missingness_report"]["timestamp_missingness_summary"],
        "columns_with_missing_values": missing_cols,
        "numeric_continuous_cols": state["numeric_continuous_cols"],
        "numeric_count_cols": state["numeric_count_cols"],
        "binary_flag_cols": state["binary_flag_cols"],
        "categorical_feature_cols": state["categorical_feature_cols"],
    }
    out = agent.invoke(
        {
            "messages": [
                lmessages.HumanMessage(
                    content=f"Plan missingness handling from this evidence: {evidence}"
                )
            ]
        }
    )
    raw_plan = out["structured_response"].model_dump()
    normalized_plan = _normalize_missingness_plan(state, raw_plan)
    payload = {"missingness_plan": normalized_plan}
    return payload


def apply_missingness_plan(state: CompositeState) -> dict:
    """
    Apply the chosen missingness plan deterministically.

    :param state: graph state
    :return: handling report and output dataset path
    """
    handling_report = tinptool.apply_missingness_actions.invoke(
        {
            "source_path": state["path"],
            "input_path": state["path"],
            "time_col": state["primary_key"],
            "secondary_keys": state["secondary_keys"],
            "winner_formatter": state["winner_formatter"],
            "actions": state["missingness_plan"]["actions"],
        }
    )
    trace_payload = {
        "missingness_plan": state["missingness_plan"],
        "missingness_handling_report": handling_report,
    }
    tinptool.write_stage_trace(state["path"], "handle_missingness", trace_payload)
    payload = {
        "missingness_handling_report": handling_report,
        "quality_dataset_path": handling_report["output_path"],
    }
    return payload


missingness_handling = lgraph.StateGraph(CompositeState)
missingness_handling.add_node("audit_missingness_pipeline", call_audit_missingness)
missingness_handling.add_node("choose_missingness_plan", choose_missingness_plan)
missingness_handling.add_node("apply_missingness_plan", apply_missingness_plan)
missingness_handling.add_edge(lgraph.START, "audit_missingness_pipeline")
missingness_handling.add_edge("audit_missingness_pipeline", "choose_missingness_plan")
missingness_handling.add_edge("choose_missingness_plan", "apply_missingness_plan")
missingness_handling.add_edge("apply_missingness_plan", lgraph.END)
graph = missingness_handling.compile()


def run_handle_missingness(path: str) -> dict:
    """
    Execute missingness handling end to end.

    :param path: dataset path
    :return: full composite graph payload
    """
    init_state: CompositeState = {
        "path": path,
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
        "metadata": {},
        "time_col": "",
        "candidates": [],
        "winner_formatter": {},
        "entity_col": None,
        "numeric_cols": [],
        "nonnegative_cols": [],
        "jump_mult": 20.0,
        "report": {},
        "summary": "",
        "flag": "",
        "type": "",
        "primary_key": "",
        "secondary_keys": [],
        "numeric_continuous_cols": [],
        "numeric_count_cols": [],
        "binary_flag_cols": [],
        "categorical_feature_cols": [],
        "known_exogenous_cols": [],
        "target_cols": [],
        "covariate_cols": [],
        "n_nat_time": 0,
        "min_time": None,
        "max_time": None,
        "typical_delta_mode": None,
        "typical_delta_median": None,
        "expected_frequency": None,
        "dominant_frequency_fraction": 0.0,
        "is_irregular_sampling": False,
        "resampling_decision": "",
        "coverage_summary": {},
        "coverage_per_entity": [],
        "missingness_report": {},
        "missingness_plan": {},
        "missingness_handling_report": {},
        "quality_dataset_path": "",
    }
    out = graph.invoke(init_state)
    payload: CompositeState = out
    _LOG.info("Missingness handling output: %s", payload)
    return payload


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
    run_handle_missingness(args.path)
