"""
Import as:

import src.univariate_analysis.univariate_metrics_plotting as sunivar
"""

from __future__ import annotations

import argparse
import logging
from typing import TypedDict

import langgraph.graph as lgraph

import src.quality_handling.standardize as sstandard
import src.tools.input_tools as tinptool

_LOG = logging.getLogger(__name__)


class CompositeState(TypedDict):
    """
    Store graph state for univariate metrics and plotting.
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
    univariate_report: dict


def call_standardize(state: CompositeState) -> dict:
    """
    Run the sequential pipeline up to optional standardization.

    :param state: graph state
    :return: composite payload from standardize
    """
    payload = sstandard.run_standardize(state["path"])
    return payload


def compute_univariate_metrics_and_plots(state: CompositeState) -> dict:
    """
    Compute univariate summaries and write per-feature distribution plots.

    :param state: graph state
    :return: univariate report
    """
    analysis_path = state.get("quality_dataset_path") or state["path"]
    report = tinptool.compute_univariate_metrics_and_plots.invoke(
        {
            "source_path": state["path"],
            "input_path": analysis_path,
            "time_col": state["primary_key"],
            "secondary_keys": state["secondary_keys"],
            "numeric_continuous_cols": state["numeric_continuous_cols"],
            "numeric_count_cols": state["numeric_count_cols"],
            "binary_flag_cols": state["binary_flag_cols"],
        }
    )
    trace_payload = {
        "analysis_path": analysis_path,
        "univariate_report": report,
    }
    tinptool.write_stage_trace(state["path"], "univariate_metrics_plotting", trace_payload)
    return {"univariate_report": report}


univariate_analysis = lgraph.StateGraph(CompositeState)
univariate_analysis.add_node("standardize_pipeline", call_standardize)
univariate_analysis.add_node("compute_univariate_metrics_and_plots", compute_univariate_metrics_and_plots)
univariate_analysis.add_edge(lgraph.START, "standardize_pipeline")
univariate_analysis.add_edge("standardize_pipeline", "compute_univariate_metrics_and_plots")
univariate_analysis.add_edge("compute_univariate_metrics_and_plots", lgraph.END)
graph = univariate_analysis.compile()


def run_univariate_metrics_plotting(path: str) -> dict:
    """
    Execute univariate summaries and plotting end to end.

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
        "univariate_report": {},
    }
    out = graph.invoke(init_state)
    payload: CompositeState = out
    _LOG.info("Univariate analysis output: %s", payload)
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
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    args = _parse_args()
    run_univariate_metrics_plotting(args.path)
