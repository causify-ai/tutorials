from __future__ import annotations

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver


# -------------------------
# Subgraph: increments a counter
# -------------------------

class SubState(TypedDict):
    n: int

def bump(state: SubState) -> dict:
    return {"n": state.get("n", 0) + 1}

sub_builder = StateGraph(SubState)
sub_builder.add_node("bump", bump)
sub_builder.add_edge(START, "bump")
sub_builder.add_edge("bump", END)

# We'll compile two versions:
# A) shared (no checkpointer here)
sub_shared = sub_builder.compile()

# B) private (subgraph has its own checkpointer)
sub_private_ckpt = MemorySaver()
sub_private = sub_builder.compile(checkpointer=sub_private_ckpt)


# -------------------------
# Parent graph: calls subgraph twice across turns
# -------------------------

class ParentState(TypedDict):
    mode: str   # "shared" or "private"
    sub_n: int  # last seen counter

def call_sub(state: ParentState) -> dict:
    mode = state["mode"]
    if mode == "shared":
        out = sub_shared.invoke({"n": state.get("sub_n", 0)})
        # Here "memory" is basically parent-managed, because we're passing state manually.
        return {"sub_n": out["n"]}
    else:
        # subgraph persists via its own checkpointer thread_id
        out = sub_private.invoke(
            {"n": 0},  # initial input
            config={"configurable": {"thread_id": "SUBGRAPH_THREAD"}}
        )
        return {"sub_n": out["n"]}

parent_builder = StateGraph(ParentState)
parent_builder.add_node("call_sub", call_sub)
parent_builder.add_edge(START, "call_sub")
parent_builder.add_edge("call_sub", END)

parent_ckpt = MemorySaver()
parent = parent_builder.compile(checkpointer=parent_ckpt)


def run_twice(mode: str):
    print(f"\n=== MODE: {mode} ===")

    # Turn 1
    out1 = parent.invoke(
        {"mode": mode, "sub_n": 0},
        config={"configurable": {"thread_id": f"PARENT_{mode}"}}
    )
    print("Turn1 sub_n:", out1["sub_n"])

    # Turn 2 (same thread_id => parent memory persists)
    out2 = parent.invoke(
        {"mode": mode, "sub_n": out1["sub_n"]},
        config={"configurable": {"thread_id": f"PARENT_{mode}"}}
    )
    print("Turn2 sub_n:", out2["sub_n"])


def main():
    run_twice("shared")
    run_twice("private")


if __name__ == "__main__":
    main()
