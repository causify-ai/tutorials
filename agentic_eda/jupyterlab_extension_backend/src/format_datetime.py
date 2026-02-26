"""
Import as:

import src.format_datetime as sfordat
"""

import logging
import pathlib
from typing import TypedDict

import langchain.agents as lagents
import langchain.tools as ltools
import langchain_core.messages as lmessages
import langgraph.graph as lgraph
import numpy as np
import pandas as pd
import pydantic

import config.config as cconf
import src.handle_inputs as shainp
import tools.input_tools as tinptool

_LOG = logging.getLogger(__name__)


def _score_parse(dt: pd.Series) -> float:
    """
    Score datetime parse quality.

    :param dt: candidate datetime series
    :return: score where larger means better
    """
    datetime_series = pd.to_datetime(dt, errors="coerce", utc=True)
    if datetime_series.isna().all():
        score = -1.0
        return score
    parsed_fraction = float(datetime_series.notna().mean())
    min_timestamp = datetime_series.min()
    max_timestamp = datetime_series.max()
    range_score = 1.0
    min_bound = pd.Timestamp("1990-01-01", tz="UTC")
    max_bound = pd.Timestamp("2035-01-01", tz="UTC")
    if min_timestamp < min_bound or max_timestamp > max_bound:
        range_score = 0.7
    datetime_no_na = datetime_series.dropna()
    monotonic_score = 0.0
    if len(datetime_no_na) >= 3:
        deltas = datetime_no_na.diff()
        inversions = float((deltas < pd.Timedelta(0)).mean())
        monotonic_score = 1.0 - inversions
    score = (
        parsed_fraction * 0.65 + range_score * 0.15 + monotonic_score * 0.20
    )
    return float(score)


class _Candidate(pydantic.BaseModel):
    """
    Store one datetime parse candidate.
    """

    model_config = pydantic.ConfigDict(extra="forbid")
    format: str | None
    dayfirst: bool | None
    yearfirst: bool | None
    utc: bool


class _ParseWithCandidatesArgs(pydantic.BaseModel):
    """
    Store tool arguments for candidate parsing.
    """

    model_config = pydantic.ConfigDict(extra="forbid")
    path: str
    col_name: str
    candidates: list[_Candidate]


@ltools.tool(args_schema=_ParseWithCandidatesArgs)
def _parse_with_candidates(
    path: str,
    col_name: str,
    candidates: list[_Candidate],
) -> dict:
    """
    Parse one column with multiple datetime candidates and pick the best.

    :param path: dataset path
    :param col_name: target column name
    :param candidates: parse candidates
    :return: best candidate summary
    """
    dataset_path = pathlib.Path(path)
    dataset = tinptool.load_dataset(dataset_path)
    col = dataset[col_name]
    best_score = -1.0
    best_candidate = None
    best_parsed_fraction = 0.0
    series = col.astype(str).str.strip().replace(
        {
            "": np.nan,
            "nan": np.nan,
            "NaT": np.nan,
        }
    )
    for candidate in candidates:
        candidate_dict = candidate.model_dump()
        format_val = candidate_dict["format"]
        dayfirst_val = candidate_dict["dayfirst"]
        yearfirst_val = candidate_dict["yearfirst"]
        utc_val = candidate_dict["utc"]
        kwargs = {
            key: val
            for key, val in {
                "format": format_val,
                "dayfirst": dayfirst_val,
                "yearfirst": yearfirst_val,
                "utc": utc_val,
            }.items()
            if val is not None
        }
        try:
            datetime_series = pd.to_datetime(
                series,
                errors="coerce",
                **kwargs,
            )
        except Exception:
            continue
        score = _score_parse(datetime_series)
        if score > best_score:
            best_score = score
            best_candidate = candidate_dict
            best_parsed_fraction = float(datetime_series.notna().mean())
    payload = {
        "best_candidate": best_candidate,
        "best_score": float(best_score),
        "parsed_fraction": float(best_parsed_fraction),
    }
    return payload


class DateFormatterState(TypedDict):
    """
    Store graph state for datetime formatting.
    """

    path: str
    time_col: str
    candidates: list[dict]
    winner_formatter: dict


class DateFormatterOutput(pydantic.BaseModel):
    """
    Store structured formatter output.
    """

    model_config = pydantic.ConfigDict(extra="forbid")
    candidates: list[_Candidate]
    winner_formatter: _Candidate


def run_formatting_agent(state: DateFormatterState) -> dict:
    """
    Run LLM tool-calling to find the best datetime parser.

    :param state: formatter graph state
    :return: candidate list and winner formatter
    """
    system_prompt = (
        "Use tools to convert the provided time column into a correct datetime "
        "format.\n"
        "1. Use extract_head to inspect the temporal column and propose parse "
        "candidates.\n"
        "2. Call _parse_with_candidates with those candidates.\n"
        "3. Return all candidates and the winning formatter."
    )
    llm = cconf.get_chat_model(model="gpt-4.1")
    agent = lagents.create_agent(
        model=llm,
        tools=[_parse_with_candidates, tinptool.extract_head],
        system_prompt=system_prompt,
        response_format=DateFormatterOutput,
    )
    out = agent.invoke(
        {
            "messages": [
                lmessages.HumanMessage(
                    content=(
                        f"The dataset path is {state['path']} and the time "
                        f"column name is {state['time_col']}"
                    )
                )
            ]
        }
    )
    structured_response = out["structured_response"].model_dump()
    payload = {
        "candidates": structured_response["candidates"],
        "winner_formatter": structured_response["winner_formatter"],
    }
    return payload


def call_input_handler(state: DateFormatterState) -> dict:
    """
    Run input handler and pick the first temporal column.

    :param state: formatter graph state
    :return: selected temporal column
    """
    out = shainp.run_input_handler(state["path"])
    temporal_cols = out.get("temporal_cols") or []
    if not temporal_cols:
        raise ValueError("No temporal columns found by input handler.")
    payload = {"time_col": temporal_cols[0]}
    return payload


date_formatter = lgraph.StateGraph(DateFormatterState)
date_formatter.add_node("input_handler", call_input_handler)
date_formatter.add_node("run_formatting_agent", run_formatting_agent)
date_formatter.add_edge(lgraph.START, "input_handler")
date_formatter.add_edge("input_handler", "run_formatting_agent")
date_formatter.add_edge("run_formatting_agent", lgraph.END)
graph = date_formatter.compile()


def run_date_formatter(path: str) -> dict:
    """
    Execute datetime formatter graph and parse the selected time column.

    :param path: dataset path
    :return: output including selected formatter and parsed dtype
    """
    graph_in = {"path": path}
    out: DateFormatterState = graph.invoke(graph_in)  # type: ignore[assignment]
    dataset_path = pathlib.Path(path)
    dataset = tinptool.load_dataset(dataset_path)
    raw_args = out["winner_formatter"]
    format_args = {key: val for key, val in raw_args.items() if val is not None}
    parsed_time = pd.to_datetime(dataset[out["time_col"]], **format_args)
    payload = {
        "time_col": out["time_col"],
        "winner_formatter": out["winner_formatter"],
        "parsed_dtype": str(parsed_time.dtype),
    }
    _LOG.info("Date formatter output: %s", payload)
    return payload
