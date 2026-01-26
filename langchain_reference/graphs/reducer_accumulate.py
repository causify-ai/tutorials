# graphs/reducer_accumulate.py
from __future__ import annotations

from typing import Annotated, TypedDict, List

from langgraph.graph import START, END, StateGraph

def add_list(old: List[str], new: List[str]) -> List[str]:
    # reducer: merge old evidence with new evidence
    return old + new

class State(TypedDict):
    evidence: Annotated[List[str], add_list]

def find_missingness(_: State) -> dict:
    return {"evidence": ["missingness: temp has 2% missing"]}

def find_outliers(_: State) -> dict:
    return {"evidence": ["outliers: co2 spikes at t=2024-01-03 12:00"]}

def main():
    g = StateGraph(State)
    g.add_node("missingness", find_missingness) # type:ignore
    g.add_node("outliers", find_outliers) # type:ignore

    g.add_edge(START, "missingness")
    g.add_edge("missingness", "outliers")
    g.add_edge("outliers", END)

    graph = g.compile()

    out = graph.invoke({"evidence": []})
    print("evidence:")
    for item in out["evidence"]:
        print("-", item)

if __name__ == "__main__":
    main()
