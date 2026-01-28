from __future__ import annotations

import argparse
from typing import TypedDict

from langgraph.graph import START, END, StateGraph

class State(TypedDict):
    flag: str
    out: str

def do_a(state: State) -> dict:
    return {"out": "took path A"}

def do_b(state: State) -> dict:
    return {"out": "took path B"}

def route(state: State) -> str:
    # Return the NEXT NODE NAME
    return "do_a" if state["flag"] == "a" else "do_b"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-f","--flag", choices=["a", "b"], required=True)
    args = ap.parse_args()

    g = StateGraph(State)
    g.add_node("do_a", do_a)
    g.add_node("do_b", do_b)

    g.add_conditional_edges(START, route)  # START -> do_a or do_b
    g.add_edge("do_a", END)
    g.add_edge("do_b", END)

    graph = g.compile()

    out = graph.invoke({"flag": args.flag, "out": ""})
    print(out)

if __name__ == "__main__":
    main()
