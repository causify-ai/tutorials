"""
Docstring for src.handle_inputs

Input dataset checks to run:
- Does it have headers? If not throw error [Header Gate]
- What are the temporal, numeric value, and categorical headers?

"""

from __future__ import annotations
import argparse
from typing import TypedDict
from langgraph.graph import START, END, StateGraph
from pathlib import Path
from tools.input_tools import extract_head, extract_metadata, headerAnalysis
from config.config import get_chat_model
from pydantic import BaseModel
from langchain.agents import create_agent
import pandas as pd
from langchain_core.messages import HumanMessage

class InputState(TypedDict):
    path: str | Path
    done: list
    has_header: bool
    has_missing_values: bool
    error: str
    info: str
    cols: list
    temporal_cols: list[str]
    numeric_val_cols: list[str]
    categorical_val_cols: list[str]

class LLMOutput(BaseModel):
    temporal_cols: list[str]
    numeric_val_cols: list[str]
    categorical_val_cols: list[str]


def header_classification_agent(
        state: InputState
) -> dict:
    
    llm = get_chat_model(model="gpt-4.1")
    agent = create_agent(
        model = llm,
        tools = [extract_head, extract_metadata],
        system_prompt="""You are a header classifier agent. Use any of the tools at your disposal to ultimately convey which columns are temporal, and of the remaining value columns which ones are purely numeric and which ones are categorical. The final output has all lists of columns.
        OUTPUT FORMAT: {"temporal_cols":["..."],"numeric_val_cols": ["..."],"categorical_val_cols":[]}
        """,
        response_format=LLMOutput,
    )

    out = agent.invoke(
        {"messages": [HumanMessage(content=f"The dataset is in {state['path']}")]}
    )

    return out["structured_response"].model_dump()

def error_node(
        state: InputState
):
    
    print(state['error'])

def hasHeader(state) -> bool:
    return state['has_header']

def run_input_handler(path: str | Path):
    g = StateGraph(InputState)

    g.add_node("headerAnalysis", headerAnalysis)
    g.add_node("header_classification_agent", header_classification_agent)
    g.add_node("error", error_node)

    g.add_edge(START, "headerAnalysis")
    # g.add_edge("hasHeader", "header_classification_agent")
    g.add_conditional_edges("headerAnalysis", hasHeader, {True: "header_classification_agent", False: "error"})
    g.add_edge("error", END)
    g.add_edge("header_classification_agent", END)

    graph = g.compile()

    init: InputState = { #type: ignore
        "path": path,

    }

    out = graph.invoke(init)

    print(out)

    return out

if __name__ == "__main__":
    run_input_handler('datasets/T1_slice.csv')
