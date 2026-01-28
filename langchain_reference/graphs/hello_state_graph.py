from __future__ import annotations

import argparse
from typing import TypedDict

from langgraph.graph import START, END, StateGraph

class State(TypedDict):
    x: int
    y: int
    note: str

def add_one(state: State) -> dict:
    # Node signature: State -> Partial<State>
    return {"x": state["x"] + 1}

def multiply(state: State) -> dict:
    return {"y": state["x"] * 10, "note": f"computed y from x={state['x']}"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-x","--x", type=int, default=3)
    args = ap.parse_args()

    g = StateGraph(State)
    g.add_node("add_one", add_one)
    g.add_node("multiply", multiply)


    # Play around with these
    g.add_edge(START, "multiply")
    g.add_edge("multiply", "add_one")
    g.add_edge("add_one", END)

    graph = g.compile()

    out = graph.invoke({"x": args.x, "y": 0, "note": ""})
    print("final state:", out)

if __name__ == "__main__":
    main()
