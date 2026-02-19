import src.handle_inputs as handle_inputs
import pandas as pd
import numpy as np
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from pathlib import Path
from config.config import get_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from tools.input_tools import load_dataset, extract_head
from pydantic import BaseModel, ConfigDict

def _score_parse(dt: pd.Series) -> float:
    # Force dtype to datetime (safe even if already datetime)
    dt = pd.to_datetime(dt, errors="coerce")

    if dt.isna().all():
        return -1.0

    parsed = dt.notna().mean()

    dmin, dmax = dt.min(), dt.max()
    sane_range = 1.0
    if dmin < pd.Timestamp("1990-01-01") or dmax > pd.Timestamp("2035-01-01"):
        sane_range = 0.7

    dt2 = dt.dropna()
    mono = 0.0
    if len(dt2) >= 3:
        deltas = dt2.diff()  # this is Timedelta series now
        inversions = (deltas < pd.Timedelta(0)).mean()
        mono = 1.0 - float(inversions)

    return float(parsed) * 0.65 + sane_range * 0.15 + mono * 0.20

class _Candidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Keep all keys REQUIRED but nullable, to satisfy strict tool-schema validators.
    format: str | None
    dayfirst: bool | None
    yearfirst: bool | None
    utc: bool


class _ParseWithCandidatesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    col_name: str
    candidates: list[_Candidate]


@tool(args_schema=_ParseWithCandidatesArgs)
def _parse_with_candidates(path: str, col_name: str, candidates: list[_Candidate]):
    """
  Try multiple datetime parsing “candidates” for a single column and pick the best one.

  This helper normalizes the input series to strings, then iterates
  over a list of candidate parse configurations (format/dayfirst/yearfirst/utc), parses the column
  with `pandas.to_datetime`, and selects the candidate with the highest score as computed by `_score_parse`.

  Scoring (via `_score_parse`) favors:
  - high parse success rate (fraction of non-NaT values),
  - a “sane” min/max timestamp range (1990-01-01 through 2035-01-01),
  - monotonicity / low rate of backwards time jumps (for columns that look like time).

  Parameters
  ----------
  col:
      A pandas Series containing the raw values for a single candidate
  time column.
      Values are coerced to `str`, stripped, and empty strings as well
  as the literal
      strings `"nan"` and `"NaT"` are treated as missing.
  candidates:
      A list of dicts, each describing one parsing attempt. Supported keys:
      - "format": `str | None`
          Passed to `pd.to_datetime(..., format=...)`. Common values:
          - a strptime format (e.g. "%Y-%m-%d %H:%M:%S")
          - "ISO8601" (pandas special value)
          - "mixed" (pandas special value for per-element inference)
          - None (let pandas infer)
      - "dayfirst": `bool` (default False)
      - "yearfirst": `bool` (default False)
      - "utc": `bool` (default False)

    eg,
      {"format": "%d %m %Y %H:%M", "dayfirst": None, "yearfirst": None, "utc": False}
      {"format": "mixed", "dayfirst": True, "yearfirst": False, "utc": False}
      {"format": "ISO8601", "dayfirst": None, "yearfirst": None, "utc": True}

  Returns
  -------
  dict:
      JSON-serializable summary of the best candidate:
      - best_candidate: {format, dayfirst, yearfirst, utc}
      - best_score: float
      - parsed_fraction: float in [0, 1]
    """
    _path = Path(path)
    data = load_dataset(_path)
    col: pd.Series = data[col_name]
    best_score = -1.0
    best_meta = None
    best_parsed_fraction = 0.0

    s = col.astype(str).str.strip().replace({"": np.nan, "nan": np.nan, "NaT": np.nan})

    for c in candidates:
        c_dict = c if isinstance(c, dict) else c.model_dump()
        fmt = c_dict.get("format", None)
        dayfirst = c_dict.get("dayfirst", None)
        yearfirst = c_dict.get("yearfirst", None)
        utc = c_dict.get("utc", None)

        kwargs = {k: v for k, v in {"format": fmt, "dayfirst": dayfirst, "yearfirst": yearfirst, "utc": utc}.items() if v is not None}

        try:
            dt = pd.to_datetime(
                s,
                errors="coerce",
                **kwargs,
            )
        except Exception:
            continue

        sc = _score_parse(dt)
        if sc > best_score:
            best_score = sc
            best_meta = c_dict
            best_parsed_fraction = float(dt.notna().mean())

    return {
        "best_candidate": best_meta,
        "best_score": float(best_score),
        "parsed_fraction": float(best_parsed_fraction),
    }


class DateFormatterState(TypedDict):
    path: str
    time_col: str
    candidates: list[dict]
    winner_formatter: dict

class DateFormatterOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidates: list[_Candidate]
    winner_formatter: _Candidate

def run_formatting_agent(
        state: DateFormatterState
):
    system_prompt: str = """Use the tools at your disposal to convert the time column provided into a correct datetime format. The docstring for the function
    has information on how to pass the arguments. To get an idea of formatting strings, use the extract_head tool as needed. 

    Steps:
    1. Use extract_head to get an idea of what the temporal column looks like and create a list of dict candidates looking like:
    [{"format": "%d %m %Y %H:%M", "dayfirst": None, "yearfirst": None, "utc": False}, 
    {"format": "mixed", "dayfirst": True, "yearfirst": False, "utc": False},
    ...
    ]

    2. Pass all the information needed by _parse_with_candidates and find out the winning format. e.g. {"format": "%d %m %Y %H:%M", "dayfirst": None, "yearfirst": None, "utc": False}
    
"""
    llm = get_chat_model(model="gpt-4.1")
    agent = create_agent(
        model = llm,
        tools = [_parse_with_candidates, extract_head],
        system_prompt=system_prompt,
        response_format=DateFormatterOutput,
    )

    out = agent.invoke(
        {"messages": [HumanMessage(content=f"The dataset path is {state['path']} and the time column name is {state['time_col']}")]}
    )

    sr = out["structured_response"].model_dump()
    return {"candidates": sr["candidates"], "winner_formatter": sr["winner_formatter"]}

def call_input_handler(state: DateFormatterState) -> dict:
    # Call compiled subgraph like a function
    out = handle_inputs.run_input_handler(state["path"])
    temporal_cols = out.get("temporal_cols") or []
    if not temporal_cols:
        raise ValueError("No temporal columns found by input handler.")
    return {"time_col": temporal_cols[0]}

date_formatter = StateGraph(DateFormatterState)
date_formatter.add_node("input_handler", call_input_handler)
date_formatter.add_node("run_formatting_agent", run_formatting_agent)
date_formatter.add_edge(START, "input_handler")
date_formatter.add_edge("input_handler", "run_formatting_agent")
date_formatter.add_edge("run_formatting_agent", END)
graph = date_formatter.compile()


def run_date_formatter(path: str):

    inp = {
        "path": path,

    }
    out: DateFormatterState = graph.invoke(inp) #type: ignore
    print(out["winner_formatter"])

    _path = Path(path)
    data = load_dataset(_path) 
    raw_args: dict = out["winner_formatter"]
    format_args = {k: v for k, v in raw_args.items() if v is not None}
    print(type(pd.to_datetime(data[out["time_col"]], **format_args))) # type: ignore


if __name__ == "__main__":
    run_date_formatter("datasets/T1_slice.csv")

