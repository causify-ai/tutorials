from __future__ import annotations

import json
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from tools.state_tools import dataset_brief

class State(TypedDict):
    messages: Annotated[list, add_messages]
    dataset_meta: dict  # system-owned

def main():
    tool_node = ToolNode([dataset_brief])

    g = StateGraph(State)
    g.add_node("tools", tool_node)
    g.add_edge(START, "tools")
    g.add_edge("tools", END)
    graph = g.compile()

    # Pretend an LLM asked to call the tool:
    tool_calls = [
        {
            "name": "dataset_brief",
            "args": {"question": "What columns exist and what is the sampling frequency?"},
            "id": "t1",
            "type": "tool_call",
        }
    ]

    state_in: State = {
        "dataset_meta": {
            "n_rows": 10000,
            "n_cols": 8,
            "columns": ["ts", "temp", "humidity", "co2", "pir", "door", "power", "label"],
            "freq": "1min",
        },
        "messages": [AIMessage(content="", tool_calls=tool_calls)],
    }

    out = graph.invoke(state_in)

    # The ToolMessage content is the JSON string returned by the tool
    # You’ll see it appended to messages.
    print("Messages:")
    for m in out["messages"]:
        print("-", type(m).__name__, getattr(m, "name", None), "=>", getattr(m, "content", None))

    # Extract the ToolMessage content:
    tool_msg = out["messages"][-1]
    print("\nParsed tool output:", json.loads(tool_msg.content))

if __name__ == "__main__":
    main()
