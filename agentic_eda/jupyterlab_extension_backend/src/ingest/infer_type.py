"""
Import as:

import src.ingest.infer_type as sinfert
"""

from __future__ import annotations

import argparse
import logging
import pathlib
from typing import Literal
from typing import TypedDict

import langgraph.graph as lgraph

import src.ingest.format_datetime as sfordat
import src.ingest.handle_inputs as shainp
import src.tools.input_tools as tinptool

_LOG = logging.getLogger(__name__)


class SeriesTypeState(TypedDict):
    """
    Store the inferred series structure.
    """

    type: Literal["single", "multiple", "multivariate"]
    primary_key: str
    secondary_keys: list[str]


class CompositeState(TypedDict):
    """
    Store graph state for series-structure inference.
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
    type: Literal["single", "multiple", "multivariate"]
    primary_key: str
    secondary_keys: list[str]


def call_input_handler(state: CompositeState) -> dict:
    """
    Run input handler and collect column metadata.

    :param state: graph state
    :return: column classification payload
    """
    dataset_path = pathlib.Path(state["path"])
    dataset = tinptool.load_dataset(dataset_path)
    out = shainp.run_input_handler(state["path"])
    metadata = tinptool.extract_metadata.invoke({"path": state["path"]})
    payload = {
        "done": out.get("done") or [],
        "has_header": bool(out.get("has_header", True)),
        "has_missing_values": bool(out.get("has_missing_values", False)),
        "error": str(out.get("error") or ""),
        "info": str(out.get("info") or ""),
        "cols": [str(col) for col in dataset.columns.tolist()],
        "temporal_cols": out.get("temporal_cols") or [],
        "numeric_val_cols": out.get("numeric_val_cols") or [],
        "categorical_val_cols": out.get("categorical_val_cols") or [],
        "bad_rows": out.get("bad_rows") or [],
        "numeric_cols": out.get("numeric_val_cols") or [],
        "metadata": metadata,
    }
    return payload


def call_date_formatter(state: CompositeState) -> dict:
    """
    Run the datetime formatter graph.

    :param state: graph state
    :return: selected time column
    """
    out: sfordat.DateFormatterState = sfordat.graph.invoke(  # type: ignore
        {"path": state["path"]}
    )
    payload = {
        "time_col": out["time_col"],
        "candidates": out.get("candidates") or [],
        "winner_formatter": out.get("winner_formatter") or {},
    }
    return payload


def infer_type(state: CompositeState) -> dict:
    """
    Infer whether the dataset is single-series, panel, or multivariate using
    deterministic value-level evidence.

    :param state: graph state
    :return: inferred series structure
    """
    structure_assessment = shainp.assess_series_structure(
        path=state["path"],
        cols=state["cols"],
        time_col=state["time_col"],
        numeric_val_cols=state["numeric_val_cols"],
        categorical_val_cols=state["categorical_val_cols"],
        winner_formatter=state["winner_formatter"],
    )
    primary_key = state["time_col"]
    secondary_keys = structure_assessment.get("secondary_keys") or []
    if secondary_keys:
        inferred_type: Literal["single", "multiple", "multivariate"] = "multiple"
    elif len(state["numeric_val_cols"]) > 1:
        inferred_type = "multivariate"
    else:
        inferred_type = "single"
    trace_payload = {
        "time_col": primary_key,
        "structure_assessment": structure_assessment,
        "inferred_type": inferred_type,
        "secondary_keys": secondary_keys,
    }
    tinptool.write_stage_trace(state["path"], "infer_type", trace_payload)
    payload = {
        "type": inferred_type,
        "primary_key": primary_key,
        "secondary_keys": secondary_keys,
        "entity_col": secondary_keys[0] if secondary_keys else None,
    }
    return payload


series_type = lgraph.StateGraph(CompositeState)
series_type.add_node("input_handler", call_input_handler)
series_type.add_node("date_formatter", call_date_formatter)
series_type.add_node("infer_type", infer_type)
series_type.add_edge(lgraph.START, "input_handler")
series_type.add_edge("input_handler", "date_formatter")
series_type.add_edge("date_formatter", "infer_type")
series_type.add_edge("infer_type", lgraph.END)
graph = series_type.compile()


def run_infer_type(path: str) -> dict:
    """
    Execute series-structure inference end to end.

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
        "type": "single",
        "primary_key": "",
        "secondary_keys": [],
    }
    out = graph.invoke(init_state)
    payload: CompositeState = out
    _LOG.info("Series type output: %s", payload)
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
    run_infer_type(args.path)
