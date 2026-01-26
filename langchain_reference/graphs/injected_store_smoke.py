from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.store.memory import InMemoryStore

from tools.pref_injectedstore_tools import save_pref, load_pref

class State(TypedDict):
    messages: Annotated[list, add_messages]

def make_graph():
    store = InMemoryStore()
    tool_node = ToolNode([save_pref, load_pref])

    g = StateGraph(State)
    g.add_node("tools", tool_node)
    g.add_edge(START, "tools")
    g.add_edge("tools", END)

    graph = g.compile(store=store)  # store gets injected into InjectedStore tools :contentReference[oaicite:6]{index=6}
    return graph

def run_once(graph, tool_calls):
    return graph.invoke({"messages": [AIMessage(content="", tool_calls=tool_calls)]})

def main():
    graph = make_graph()

    # First run: save
    out1 = run_once(graph, [
        {"name": "save_pref", "args": {"user_id": "u1", "key": "freq_hint", "value": "1min"}, "id": "t1", "type": "tool_call"}
    ])
    print("Run1 last message:", out1["messages"][-1].content)

    # Second run: load (later)
    out2 = run_once(graph, [
        {"name": "load_pref", "args": {"user_id": "u1", "key": "freq_hint"}, "id": "t2", "type": "tool_call"}
    ])
    print("Run2 last message:", out2["messages"][-1].content)

if __name__ == "__main__":
    main()
