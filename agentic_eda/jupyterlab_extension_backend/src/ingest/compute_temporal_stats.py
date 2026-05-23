"""
Import as:

import src.ingest.compute_temporal_stats as sctstats
"""

from __future__ import annotations

import argparse
import logging
from typing import TypedDict

import langgraph.graph as lgraph

import src.ingest.infer_structure as sinferstruct
import src.tools.input_tools as tinptool

_LOG = logging.getLogger(__name__)


class TemporalStatsState(TypedDict):
    """
    Store deterministic temporal statistics.
    """

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


class CompositeState(TypedDict):
    """
    Store graph state for temporal statistics.
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


def call_infer_structure(state: CompositeState) -> dict:
    """
    Run the sequential pipeline up to feature-structure inference.

    :param state: graph state
    :return: composite payload from infer_structure
    """
    payload = sinferstruct.run_infer_structure(state["path"])
    return payload


def compute_temporal_stats(state: CompositeState) -> dict:
    """
    Compute deterministic temporal range, coverage, and frequency statistics.

    :param state: graph state
    :return: temporal statistics payload
    """
    temporal_report = tinptool.compute_temporal_stats.invoke(
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
        "temporal_report": temporal_report,
    }
    tinptool.write_stage_trace(state["path"], "compute_temporal_stats", trace_payload)
    payload = {
        "n_nat_time": temporal_report["n_nat_time"],
        "min_time": temporal_report["min_time"],
        "max_time": temporal_report["max_time"],
        "typical_delta_mode": temporal_report["typical_delta_mode"],
        "typical_delta_median": temporal_report["typical_delta_median"],
        "expected_frequency": temporal_report["expected_frequency"],
        "dominant_frequency_fraction": temporal_report["dominant_frequency_fraction"],
        "is_irregular_sampling": temporal_report["is_irregular_sampling"],
        "resampling_decision": temporal_report["resampling_decision"],
        "coverage_summary": temporal_report["coverage_summary"],
        "coverage_per_entity": temporal_report["coverage_per_entity"],
    }
    return payload


temporal_stats = lgraph.StateGraph(CompositeState)
temporal_stats.add_node("infer_structure_pipeline", call_infer_structure)
temporal_stats.add_node("compute_temporal_stats", compute_temporal_stats)
temporal_stats.add_edge(lgraph.START, "infer_structure_pipeline")
temporal_stats.add_edge("infer_structure_pipeline", "compute_temporal_stats")
temporal_stats.add_edge("compute_temporal_stats", lgraph.END)
graph = temporal_stats.compile()


def run_compute_temporal_stats(path: str) -> dict:
    """
    Execute temporal statistics end to end.

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
    }
    out = graph.invoke(init_state)
    payload: CompositeState = out
    _LOG.info("Temporal stats output: %s", payload)
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
    run_compute_temporal_stats(args.path)
