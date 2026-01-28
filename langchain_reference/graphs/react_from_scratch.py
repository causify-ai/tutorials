# graphs/react_from_scratch.py
from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from src.config import get_chat_model
from tools.agent_tools import utc_now, mean, sqrt  # your tools

class State(TypedDict):
    messages: Annotated[list, add_messages]

def call_model(state: State) -> dict:
    llm = get_chat_model().bind_tools([utc_now, mean, sqrt])
    ai = llm.invoke(state["messages"])
    return {"messages": [ai]}

def needs_tools(state: State) -> str:
    last = state["messages"][-1]
    tool_calls = getattr(last, "tool_calls", None)
    if tool_calls:
        return "tools"
    return "end"

def main():
    tool_node = ToolNode([utc_now, mean, sqrt])

    g = StateGraph(State)
    g.add_node("model", call_model)
    g.add_node("tools", tool_node)

    g.add_edge(START, "model")
    g.add_conditional_edges("model", needs_tools, {"tools": "tools", "end": END})
    g.add_edge("tools", "model")  # loop back

    graph = g.compile()

    init = {
        "messages": [
            HumanMessage(content="Compute mean([1,2,3,4,10]) and sqrt(49). Also tell me the current UTC time.")
        ]
    }

    out = graph.invoke(init) #type:ignore

    print("\n=== Final messages ===")
    for m in out["messages"]:
        t = type(m).__name__
        extra = ""
        if getattr(m, "tool_calls", None):
            extra = f" tool_calls={[tc['name'] for tc in m.tool_calls]}"
        if getattr(m, "name", None):
            extra += f" name={m.name}"
        print(f"{t}{extra}\n{m.content}\n")

if __name__ == "__main__":
    main()
