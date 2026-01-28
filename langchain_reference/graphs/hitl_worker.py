from __future__ import annotations

from typing import TypedDict, Literal
from pathlib import Path

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from langgraph.types import interrupt


class State(TypedDict):
    target_path: str
    decision: Literal["approve", "reject", ""]


def propose_delete(state: State) -> dict:
    # Ask for human approval
    payload = {
        "action": "delete_file",
        "target_path": state["target_path"],
        "message": "Approve deletion?",
    }
    decision = interrupt(payload)  # pauses here until resumed
    return {"decision": decision}


def do_delete(state: State) -> dict:
    if state["decision"] != "approve":
        return {"target_path": state["target_path"]}  # no-op

    p = Path(state["target_path"])
    # toy safety: only delete if exists and is a file
    if p.exists() and p.is_file():
        p.unlink()
    return {"target_path": state["target_path"]}


builder = StateGraph(State)
builder.add_node("propose", propose_delete)
builder.add_node("delete", do_delete)
builder.add_edge(START, "propose")
builder.add_edge("propose", "delete")
builder.add_edge("delete", END)

ckpt = MemorySaver()
graph = builder.compile(checkpointer=ckpt)


def main():
    # create a toy file
    Path("tmp").mkdir(exist_ok=True)
    victim = Path("tmp/victim.txt")
    victim.write_text("delete me")
    print("Created:", victim, "exists?", victim.exists())

    thread_id = "HITL_DEMO"

    # Start run (will interrupt)
    print("\n=== RUN 1: expect interrupt ===")
    out = graph.invoke(
        {"target_path": str(victim), "decision": ""},
        config={"configurable": {"thread_id": thread_id}},
    )
    # If it interrupted, you won't reach a normal final here in many setups.

    resume = input(f"{out['__interrupt__'][0].value['message']}\n")

    # can be conditional using `if "__interrupt__" in out:`

    print(f"\n=== RESUME: {resume} ===")
    out2 = graph.invoke(
        Command(resume=resume),
        config={"configurable": {"thread_id": thread_id}},
    )
    print("After resume, exists?", victim.exists())


if __name__ == "__main__":
    main()
