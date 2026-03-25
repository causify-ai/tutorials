"""
Import as:

import src.quality_handling.audit_missingness as sauditmiss
"""

from __future__ import annotations

import argparse
import logging
from typing import TypedDict

import langgraph.graph as lgraph

import src.ingest.compute_temporal_stats as sctstats
import src.tools.input_tools as tinptool

_LOG = logging.getLogger(__name__)


class MissingnessAuditState(TypedDict):
    """
    Store deterministic missingness audit output.
    """

    missingness_report: dict


class CompositeState(TypedDict):
    """
    Store graph state for missingness auditing.
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


def call_compute_temporal_stats(state: CompositeState) -> dict:
    """
    Run the sequential pipeline up to temporal statistics.

    :param state: graph state
    :return: composite payload from compute_temporal_stats
    """
    payload = sctstats.run_compute_temporal_stats(state["path"])
    return payload


def audit_missingness(state: CompositeState) -> dict:
    """
    Audit value missingness and timestamp missingness deterministically.

    :param state: graph state
    :return: missingness report payload
    """
    missingness_report = tinptool.audit_missingness.invoke(
        {
            "path": state["path"],
            "time_col": state["primary_key"],
            "secondary_keys": state["secondary_keys"],
            "winner_formatter": state["winner_formatter"],
        }
    )
    trace_payload = {
        "primary_key": state["primary_key"],
        "secondary_keys": state["secondary_keys"],
        "missingness_report": missingness_report,
    }
    tinptool.write_stage_trace(state["path"], "audit_missingness", trace_payload)
    payload = {
        "missingness_report": missingness_report,
        "has_missing_values": bool(
            missingness_report["value_missingness_summary"]["total_missing_cells"] > 0
            or missingness_report["timestamp_missingness_summary"]["total_missing_timestamps"] > 0
        ),
    }
    return payload


missingness_audit = lgraph.StateGraph(CompositeState)
missingness_audit.add_node("compute_temporal_stats_pipeline", call_compute_temporal_stats)
missingness_audit.add_node("audit_missingness", audit_missingness)
missingness_audit.add_edge(lgraph.START, "compute_temporal_stats_pipeline")
missingness_audit.add_edge("compute_temporal_stats_pipeline", "audit_missingness")
missingness_audit.add_edge("audit_missingness", lgraph.END)
graph = missingness_audit.compile()


def run_audit_missingness(path: str) -> dict:
    """
    Execute missingness auditing end to end.

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
    }
    out = graph.invoke(init_state)
    payload: CompositeState = out
    _LOG.info("Missingness audit output: %s", payload)
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
    run_audit_missingness(args.path)
