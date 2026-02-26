"""
Import as:

import src.handle_inputs as shainp
"""

from __future__ import annotations

import argparse
import logging
import pathlib
from typing import TypedDict

import langchain.agents as lagents
import langchain_core.messages as lmessages
import langgraph.graph as lgraph
import pydantic

import config.config as cconf
import tools.input_tools as tinptool

_LOG = logging.getLogger(__name__)


class InputState(TypedDict):
    """
    Store graph state for input checks.
    """

    path: str | pathlib.Path
    done: list[str]
    has_header: bool
    has_missing_values: bool
    error: str
    info: str
    cols: list[str]
    temporal_cols: list[str]
    numeric_val_cols: list[str]
    categorical_val_cols: list[str]


class LLMOutput(pydantic.BaseModel):
    """
    Store structured output from the header classifier.
    """

    temporal_cols: list[str]
    numeric_val_cols: list[str]
    categorical_val_cols: list[str]


def header_classification_agent(state: InputState) -> dict:
    """
    Classify temporal, numeric, and categorical columns.

    :param state: input graph state
    :return: column classification payload
    """
    llm = cconf.get_chat_model(model="gpt-4.1")
    agent = lagents.create_agent(
        model=llm,
        tools=[tinptool.extract_head, tinptool.extract_metadata],
        system_prompt=(
            "You are a header classifier agent. Use tools to identify temporal "
            "columns and classify the remaining value columns as numeric or "
            "categorical. Output JSON with keys temporal_cols, "
            "numeric_val_cols, and categorical_val_cols."
        ),
        response_format=LLMOutput,
    )
    out = agent.invoke(
        {
            "messages": [
                lmessages.HumanMessage(
                    content=f"The dataset is in {state['path']}"
                )
            ]
        }
    )
    result = out["structured_response"].model_dump()
    return result


def error_node(state: InputState) -> dict:
    """
    Log an error node transition.

    :param state: input graph state
    :return: empty update
    """
    _LOG.error("Input handler failed: %s", state["error"])
    return {}


def has_header(state: InputState) -> bool:
    """
    Check if header validation passed.

    :param state: input graph state
    :return: true when headers are valid
    """
    has_header_flag = state["has_header"]
    return has_header_flag


def run_input_handler(path: str | pathlib.Path) -> dict:
    """
    Run dataset header and column classification checks.

    :param path: path to dataset
    :return: final graph output
    """
    graph_builder = lgraph.StateGraph(InputState)
    graph_builder.add_node("header_analysis", tinptool.analyze_header)
    graph_builder.add_node(
        "header_classification_agent",
        header_classification_agent,
    )
    graph_builder.add_node("error", error_node)
    graph_builder.add_edge(lgraph.START, "header_analysis")
    graph_builder.add_conditional_edges(
        "header_analysis",
        has_header,
        {
            True: "header_classification_agent",
            False: "error",
        },
    )
    graph_builder.add_edge("error", lgraph.END)
    graph_builder.add_edge("header_classification_agent", lgraph.END)
    graph = graph_builder.compile()
    init_state: InputState = {
        "path": str(path),
        "done": [],
        "has_header": True,
        "has_missing_values": False,
        "error": "",
        "info": "",
        "cols": [],
        "temporal_cols": [],
        "numeric_val_cols": [],
        "categorical_val_cols": [],
    }
    out = graph.invoke(init_state)
    _LOG.info("Input handler output: %s", out)
    return out


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
    run_input_handler(args.path)
