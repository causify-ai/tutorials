from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from tools.math_tools import mean, zscore

class State(TypedDict):
    messages: Annotated[list, add_messages]

def main():
    tool_node = ToolNode([mean, zscore])

    g = StateGraph(State)
    g.add_node("tools", tool_node)
    g.add_edge(START, "tools")
    g.add_edge("tools", END)
    graph = g.compile()

    # ToolNode supports "Direct Tool Calls" input format:
    # [{"name": "...", "args": {...}, "id": "...", "type": "tool_call"}] :contentReference[oaicite:6]{index=6}
    tool_calls = [
        {"name": "mean", "args": {"xs": [1, 2, 3, 4]}, "id": "t1", "type": "tool_call"},
        {"name": "zscore", "args": {"xs": [9, 10, 10], "x": 10}, "id": "t2", "type": "tool_call"},  # will error (std=0)
    ]

    out = graph.invoke({"messages": [AIMessage(content="", tool_calls=tool_calls)]})

    print("Final messages:")
    for m in out["messages"]:
        print("-", type(m).__name__, "=>", getattr(m, "content", None))

if __name__ == "__main__":
    main()
