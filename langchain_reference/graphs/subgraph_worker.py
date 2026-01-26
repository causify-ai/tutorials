from __future__ import annotations

from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# -------------------------
# Subgraph: parse -> format
# -------------------------

class SubState(TypedDict):
    raw: str
    parsed: dict
    formatted: str

def parse_node(state: SubState) -> dict:
    # toy parsing: split "key: value" lines into dict
    raw = state["raw"]
    parsed = {}
    for line in raw.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            parsed[k.strip()] = v.strip()
    return {"parsed": parsed}

def format_node(state: SubState) -> dict:
    parsed = state.get("parsed", {})
    # toy formatting: render as bullet list
    lines = [f"- {k}: {v}" for k, v in parsed.items()]
    return {"formatted": "Parsed fields:\n" + "\n".join(lines)}

sub_builder = StateGraph(SubState)
sub_builder.add_node("parse", parse_node)
sub_builder.add_node("format", format_node)
sub_builder.add_edge(START, "parse")
sub_builder.add_edge("parse", "format")
sub_builder.add_edge("format", END)
subgraph = sub_builder.compile()


# -------------------------
# Parent graph: calls subgraph
# -------------------------

class ParentState(TypedDict):
    user_text: str
    result: str

def call_subgraph(state: ParentState) -> dict:
    # Call compiled subgraph like a function
    out = subgraph.invoke({"raw": state["user_text"]}) #type: ignore
    return {"result": out["formatted"]}

parent_builder = StateGraph(ParentState)
parent_builder.add_node("worker", call_subgraph)
parent_builder.add_edge(START, "worker")
parent_builder.add_edge("worker", END)
parent = parent_builder.compile()


def main():
    inp = {
        "user_text": "name: Indro\nrole: ML engineer\nlocation: Kolkata"
    }

    print("\n=== STREAM (subgraphs=True) ===\n")
    for event in parent.stream(inp, subgraphs=True): #type: ignore
        # events are dicts; printing raw is easiest for first time
        print(event)

    out = parent.invoke(inp) #type: ignore
    print(out)
    print("\n=== FINAL ===")
    print(out["result"])


if __name__ == "__main__":
    main()
