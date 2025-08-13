# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Build an LLM Agent with LangGraph

# %% [markdown]
# ## Description
#
# This notebook shows how to build a minimal EDA-focused LLM agent with LangGraph and OpenAI. It demonstrates an agent that takes a prompt and autonomously selects and runs available EDA tools to complete the analysis.

# %% [markdown]
# ## Imports

# %%
import os
import logging
from typing import Annotated, TypedDict

import pandas as pd
import numpy as np

import helpers.hdbg as hdbg
import matplotlib.pyplot as plt
import langchain_core.tools as lc_tools
import langchain_core.messages as lc_messages
import langchain_openai as lc_openai
import langgraph.graph as lg_graph
import langgraph.graph.message as lg_msg
import langgraph.prebuilt as lg_prebuilt


# %% [markdown]
# ## Config

# %%
# Avoid messages from OpenAI REST interface.
hdbg.init_logger(verbosity=logging.CRITICAL)
_LOG = logging.getLogger(__name__)

# %%
# Add OpenAPI to environment variable.
# os.environ["OPENAI_API_KEY"] = ""
# Initiate OpenAI model.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY is not set. Set it in your environment before running the agent.")

# %% [markdown]
# ## Generate data

# %%
demo_csv_path = "demo_sales.csv"
demo_df = pd.DataFrame(
    {
        "region": ["Northeast", "Midwest", "South", "West"] * 5,
        "month": list(range(1, 21)),
        "units_sold": np.random.randint(10, 500, size=20),
        "price": np.random.uniform(5.0, 30.0, size=20).round(2),
    }
)
demo_df.to_csv(demo_csv_path, index=False)
demo_df.head()


# %% [markdown]
# ## Define EDA tools
#
# These tools are the agent’s abilities. We’ll expose a few for EDA:
# - `read_head(path, n)`: preview top rows
# - `describe_columns(path)`: numeric summary
# - `groupby_agg(path, by, metric, agg)`: quick groupby summaries

# %%
@lc_tools.tool
def read_head(path: str, n: int = 5) -> str:
    """
    Preview the top rows of a CSV.

    :param path: path to the CSV file
    :param n: number of rows to show
    :return: table preview
    """
    df = pd.read_csv(path)
    return df.head(n).to_markdown(index=False)


@lc_tools.tool
def plot_histogram(path: str, column: str) -> str:
    """
    Display a histogram for a numeric column from a CSV.

    :param path: path to the CSV file
    :param column: column to plot
    :param bins: number of bins to use
    :return: confirmation message after rendering
    """
    df = pd.read_csv(path)
    values = pd.to_numeric(df[column], errors="coerce").dropna()
    plt.figure()
    plt.hist(values, bins=20)
    plt.xlabel(column)
    plt.ylabel("Count")
    plt.title(f"Histogram of {column}")
    plt.tight_layout()
    plt.show()
    return "Displayed histogram."


@lc_tools.tool
def groupby_agg(path: str, by: str, metric: str) -> str:
    """
    Compute the mean of a numeric column grouped by a categorical column.

    :param path: path to the CSV file
    :param by: categorical column to group by
    :param metric: numeric column to aggregate (mean)
    :return: grouped table summary
    """
    df = pd.read_csv(path)
    grouped = df.groupby(by)[metric].mean().reset_index()
    return grouped.to_markdown(index=False)

EDA_TOOLS = [read_head, plot_histogram, groupby_agg]


# %% [markdown]
# ## Define agent state and nodes

# %%
class AgentState(TypedDict):
    """
    Accumulate chat messages.
    """
    messages: Annotated[list[lc_messages.AnyMessage], lg_msg.add_messages]

# Model with tools bound.
llm = lc_openai.ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(EDA_TOOLS)

def assistant_node(state: AgentState) -> dict:
    """
    Tell me to produce the next AI message given the conversation.
    """
    ai_msg = llm.invoke(state["messages"])
    return {"messages": [ai_msg]}


# %%

# Tool node executes tools when the model requests them.
tools_node = lg_prebuilt.ToolNode(EDA_TOOLS)
# Build the graph.
graph = lg_graph.StateGraph(AgentState)
graph.add_node("assistant", assistant_node)
graph.add_node("tools", tools_node)
# Assistant decides either: call tools -> go to tools; or respond -> END.
graph.add_conditional_edges("assistant", lg_prebuilt.tools_condition)
graph.add_edge("tools", "assistant")
graph.set_entry_point("assistant")
app = graph.compile()
print("Graph compiled.")


# %% [markdown]
# ## Agent Demo

# %%
# Define system behavior and user input.
sys_msg = lc_messages.SystemMessage(
    content=(
        "You have EDA tools for previewing rows, plotting histograms, and grouped aggregations. "
        "When a user asks for EDA, choose and call the most relevant tool. "
    )
)

def run_turn(user_text: str):
    state = {"messages": [sys_msg, lc_messages.HumanMessage(content=user_text)]}
    final = None
    for event in app.stream(state, stream_mode="values"):
        final = event["messages"][-1]
    return final


# %%
# Example 1: preview head.
final_1 = run_turn(f"Show the first 3 rows of {demo_csv_path}.")
print(final_1.content)

# %%
# Example 2: plot histogram.
final_2 = run_turn(f"Plot a histogram of the 'units_sold' column from {demo_csv_path} with 10 bins.")
print(final_2.content)

# %%
# Example 3: groupby aggregation.
final_3 = run_turn(f"What is the average of 'units_sold' by 'region' in {demo_csv_path}?")
print(final_3.content)
