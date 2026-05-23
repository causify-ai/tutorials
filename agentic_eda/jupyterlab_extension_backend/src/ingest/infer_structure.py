"""
Import as:

import src.ingest.infer_structure as sinferstruct
"""

from __future__ import annotations

import argparse
import logging
from typing import TypedDict

import langgraph.graph as lgraph

import src.ingest.infer_type as sinfert
import src.tools.input_tools as tinptool

_LOG = logging.getLogger(__name__)


class FeatureStructureState(TypedDict):
    """
    Store inferred semantic feature groupings.
    """

    numeric_continuous_cols: list[str]
    numeric_count_cols: list[str]
    binary_flag_cols: list[str]
    categorical_feature_cols: list[str]
    known_exogenous_cols: list[str]
    target_cols: list[str]
    covariate_cols: list[str]


class CompositeState(TypedDict):
    """
    Store graph state for feature-structure inference.
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


def call_infer_type(state: CompositeState) -> dict:
    """
    Run the sequential pipeline up to series-type inference.

    :param state: graph state
    :return: composite payload from infer_type
    """
    payload = sinfert.run_infer_type(state["path"])
    return payload


def infer_structure(state: CompositeState) -> dict:
    """
    Infer semantic feature roles for EDA deterministically from observed column
    behavior.

    :param state: graph state
    :return: inferred feature groupings
    """
    feature_bucket_report = tinptool.infer_feature_buckets.invoke(
        {
            "path": state["path"],
            "time_col": state["primary_key"],
            "secondary_keys": state["secondary_keys"],
        }
    )
    trace_payload = {
        "primary_key": state["primary_key"],
        "secondary_keys": state["secondary_keys"],
        "series_type": state["type"],
        "feature_bucket_report": feature_bucket_report,
    }
    tinptool.write_stage_trace(state["path"], "infer_structure", trace_payload)
    payload = {
        "numeric_continuous_cols": feature_bucket_report["numeric_continuous_cols"],
        "numeric_count_cols": feature_bucket_report["numeric_count_cols"],
        "binary_flag_cols": feature_bucket_report["binary_flag_cols"],
        "categorical_feature_cols": feature_bucket_report["categorical_feature_cols"],
        "known_exogenous_cols": feature_bucket_report["known_exogenous_cols"],
        "target_cols": feature_bucket_report["target_cols"],
        "covariate_cols": feature_bucket_report["covariate_cols"],
    }
    return payload


feature_structure = lgraph.StateGraph(CompositeState)
feature_structure.add_node("infer_type_pipeline", call_infer_type)
feature_structure.add_node("infer_structure", infer_structure)
feature_structure.add_edge(lgraph.START, "infer_type_pipeline")
feature_structure.add_edge("infer_type_pipeline", "infer_structure")
feature_structure.add_edge("infer_structure", lgraph.END)
graph = feature_structure.compile()


def run_infer_structure(path: str) -> dict:
    """
    Execute feature-structure inference end to end.

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
    }
    out = graph.invoke(init_state)
    payload: CompositeState = out
    _LOG.info("Feature structure output: %s", payload)
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
    run_infer_structure(args.path)
