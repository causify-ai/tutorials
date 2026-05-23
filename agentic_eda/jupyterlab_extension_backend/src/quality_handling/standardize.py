"""
Import as:

import src.quality_handling.standardize as sstandard
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
import src.quality_handling.handle_missingness as shandlemiss
import src.tools.input_tools as tinptool

_LOG = logging.getLogger(__name__)


def _build_standardization_plan_summary(actions: list[dict], *, defaulted_cols: int) -> str:
    """
    Build a summary from the normalized standardization actions.

    :param actions: normalized action list
    :param defaulted_cols: number of columns defaulted during normalization
    :return: summary text aligned with the final plan
    """
    if not actions:
        return "No numeric candidate columns were selected for optional standardization."
    counts: dict[str, int] = {}
    for action in actions:
        transform = str(action["action"])
        counts[transform] = counts.get(transform, 0) + 1
    ordered_counts = ", ".join(
        f"{transform}={counts[transform]}"
        for transform in sorted(counts)
    )
    summary = (
        f"Normalized standardization plan for {len(actions)} columns: {ordered_counts}. "
        "This summary reflects the final validated transform choices, not the raw LLM prose."
    )
    if defaulted_cols > 0:
        summary += f" {defaulted_cols} columns defaulted conservatively to `none`."
    return summary


class StandardizationDecision(pydantic.BaseModel):
    """
    Store one bounded standardization decision.
    """

    col: str
    action: Literal["none", "robust_scale", "log1p", "log1p_then_robust_scale"]
    reason: str


class StandardizationPlanOutput(pydantic.BaseModel):
    """
    Store LLM-produced standardization plan.
    """

    summary: str
    actions: list[StandardizationDecision]


class StandardizationGateOutput(pydantic.BaseModel):
    """
    Store the dataset-level standardization gate decision.
    """

    should_standardize: bool
    reason: str


class CompositeState(TypedDict):
    """
    Store graph state for optional standardization.
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
    standardization_profile: dict
    standardization_gate: dict
    standardization_plan: dict
    standardization_report: dict
    standardized_dataset_path: str


def call_handle_missingness(state: CompositeState) -> dict:
    """
    Run the sequential pipeline up to missingness handling.

    :param state: graph state
    :return: composite payload from handle_missingness
    """
    payload = shandlemiss.run_handle_missingness(state["path"])
    return payload


def profile_standardization(state: CompositeState) -> dict:
    """
    Profile numeric feature scale and tail behavior deterministically.

    :param state: graph state
    :return: scale profile report
    """
    input_path = state["quality_dataset_path"] or state["path"]
    profile = tinptool.profile_standardization_candidates.invoke(
        {
            "path": input_path,
            "numeric_continuous_cols": state["numeric_continuous_cols"],
            "numeric_count_cols": state["numeric_count_cols"],
            "binary_flag_cols": state["binary_flag_cols"],
        }
    )
    payload = {"standardization_profile": profile}
    return payload


def choose_standardization_gate(state: CompositeState) -> dict:
    """
    Decide whether optional standardization should run at all.

    :param state: graph state
    :return: dataset-level gate decision
    """
    per_column = state["standardization_profile"].get("per_column") or []
    if not per_column:
        return {
            "standardization_gate": {
                "should_standardize": False,
                "reason": "No numeric candidate columns were available for optional standardization.",
            }
        }
    llm = cconf.get_chat_model(model="gpt-4.1")
    agent = lagents.create_agent(
        model=llm,
        tools=[],
        system_prompt=(
            "You are the gatekeeper for point 9 in a time-series EDA backend. "
            "Decide whether optional standardization should run at all for this dataset. "
            "Favor should_standardize=false unless there is strong evidence that rescaling "
            "or log-scaling is genuinely useful. Favor false for raw exploratory analysis, "
            "for SCADA or sensor-style datasets where physical units matter, and for cases "
            "where leaving values untouched preserves interpretability. Favor true only when "
            "scale disparities or heavy tails are severe enough that not transforming would "
            "materially hinder comparison or downstream modeling."
        ),
        response_format=StandardizationGateOutput,
    )
    evidence = {
        "series_type": state["type"],
        "numeric_continuous_cols": state["numeric_continuous_cols"],
        "numeric_count_cols": state["numeric_count_cols"],
        "binary_flag_cols": state["binary_flag_cols"],
        "scale_summary": state["standardization_profile"].get("scale_summary"),
        "sample_profiles": per_column[:20],
    }
    out = agent.invoke(
        {
            "messages": [
                lmessages.HumanMessage(
                    content=f"Decide whether optional standardization should run from this evidence: {evidence}"
                )
            ]
        }
    )
    gate = out["structured_response"].model_dump()
    return {"standardization_gate": gate}


def _normalize_standardization_plan(state: CompositeState, raw_plan: dict) -> dict:
    """
    Ensure every candidate column gets a supported transform decision.

    :param state: graph state
    :param raw_plan: LLM-produced plan
    :return: normalized plan
    """
    per_column = state["standardization_profile"].get("per_column") or []
    eligible_by_col = {
        item["col"]: set(item["eligible_actions"])
        for item in per_column
    }
    plan_by_col = {}
    defaulted_cols = 0
    for item in raw_plan.get("actions") or []:
        col = str(item.get("col") or "")
        if col not in eligible_by_col:
            continue
        action = str(item.get("action") or "none")
        if action not in eligible_by_col[col]:
            action = "none"
        plan_by_col[col] = {
            "col": col,
            "action": action,
            "reason": str(item.get("reason") or ""),
        }
    normalized_actions = []
    for item in per_column:
        col = item["col"]
        if col not in plan_by_col:
            defaulted_cols += 1
        normalized_actions.append(
            plan_by_col.get(
                col,
                {
                    "col": col,
                    "action": "none",
                    "reason": "Defaulted conservatively because no valid transform was selected.",
                },
            )
        )
    return {
        "summary": _build_standardization_plan_summary(
            normalized_actions,
            defaulted_cols=defaulted_cols,
        ),
        "actions": normalized_actions,
    }


def choose_standardization_plan(state: CompositeState) -> dict:
    """
    Choose whether optional standardization is justified.

    :param state: graph state
    :return: normalized standardization plan
    """
    gate = state.get("standardization_gate") or {}
    if not bool(gate.get("should_standardize")):
        payload = {
            "standardization_plan": {
                "summary": (
                    "Dataset-level standardization gate returned `no`. "
                    f"Reason: {str(gate.get('reason') or 'No reason provided.')}"
                ),
                "actions": [],
            }
        }
        return payload
    per_column = state["standardization_profile"].get("per_column") or []
    if not per_column:
        payload = {
            "standardization_plan": {
                "summary": "No numeric candidate columns were available for optional standardization.",
                "actions": [],
            }
        }
        return payload
    llm = cconf.get_chat_model(model="gpt-4.1")
    agent = lagents.create_agent(
        model=llm,
        tools=[],
        system_prompt=(
            "You are an optional standardization planner for a time-series EDA backend. "
            "This stage is optional. Use action none unless there is a concrete reason "
            "to transform a feature. Allowed actions are none, robust_scale, log1p, "
            "and log1p_then_robust_scale. Favor none when evidence is weak. Favor "
            "robust_scale for large cross-feature scale disparities. Favor log1p for "
            "strongly right-skewed nonnegative features. Never invent new actions."
        ),
        response_format=StandardizationPlanOutput,
    )
    evidence = {
        "series_type": state["type"],
        "scale_summary": state["standardization_profile"].get("scale_summary"),
        "per_column": per_column,
    }
    out = agent.invoke(
        {
            "messages": [
                lmessages.HumanMessage(
                    content=f"Choose optional standardization actions from this evidence: {evidence}"
                )
            ]
        }
    )
    raw_plan = out["structured_response"].model_dump()
    normalized_plan = _normalize_standardization_plan(state, raw_plan)
    payload = {"standardization_plan": normalized_plan}
    return payload


def apply_standardization_plan(state: CompositeState) -> dict:
    """
    Apply the chosen standardization plan deterministically.

    :param state: graph state
    :return: transformation report and output path
    """
    input_path = state["quality_dataset_path"] or state["path"]
    if not state["standardization_plan"]["actions"]:
        report = {
            "input_path": input_path,
            "output_path": input_path,
            "skipped": True,
            "reason": state["standardization_plan"]["summary"],
            "actions_applied": [],
        }
        trace_payload = {
            "input_path": input_path,
            "standardization_profile": state["standardization_profile"],
            "standardization_gate": state.get("standardization_gate") or {},
            "standardization_plan": state["standardization_plan"],
            "standardization_report": report,
        }
        tinptool.write_stage_trace(state["path"], "standardize", trace_payload)
        payload = {
            "standardization_report": report,
            "standardized_dataset_path": input_path,
        }
        return payload
    report = tinptool.apply_standardization_actions.invoke(
        {
            "source_path": state["path"],
            "input_path": input_path,
            "actions": state["standardization_plan"]["actions"],
        }
    )
    trace_payload = {
        "input_path": input_path,
        "standardization_profile": state["standardization_profile"],
        "standardization_gate": state.get("standardization_gate") or {},
        "standardization_plan": state["standardization_plan"],
        "standardization_report": report,
    }
    tinptool.write_stage_trace(state["path"], "standardize", trace_payload)
    payload = {
        "standardization_report": report,
        "standardized_dataset_path": report["output_path"],
    }
    return payload


standardization = lgraph.StateGraph(CompositeState)
standardization.add_node("handle_missingness_pipeline", call_handle_missingness)
standardization.add_node("profile_standardization", profile_standardization)
standardization.add_node("choose_standardization_gate", choose_standardization_gate)
standardization.add_node("choose_standardization_plan", choose_standardization_plan)
standardization.add_node("apply_standardization_plan", apply_standardization_plan)
standardization.add_edge(lgraph.START, "handle_missingness_pipeline")
standardization.add_edge("handle_missingness_pipeline", "profile_standardization")
standardization.add_edge("profile_standardization", "choose_standardization_gate")
standardization.add_edge("choose_standardization_gate", "choose_standardization_plan")
standardization.add_edge("choose_standardization_plan", "apply_standardization_plan")
standardization.add_edge("apply_standardization_plan", lgraph.END)
graph = standardization.compile()


def run_standardize(path: str) -> dict:
    """
    Execute optional standardization end to end.

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
        "standardization_profile": {},
        "standardization_gate": {},
        "standardization_plan": {},
        "standardization_report": {},
        "standardized_dataset_path": "",
    }
    out = graph.invoke(init_state)
    payload: CompositeState = out
    _LOG.info("Standardization output: %s", payload)
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
    run_standardize(args.path)
