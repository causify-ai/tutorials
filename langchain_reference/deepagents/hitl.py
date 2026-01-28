from __future__ import annotations

from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from src.config import get_chat_model
from langchain.agents.middleware.human_in_the_loop import InterruptOnConfig


def main():
    model = get_chat_model()
    ckpt = MemorySaver()
    thread_id = "DA7_CLI_HITL"

    agent = create_deep_agent(
        model=model,
        checkpointer=ckpt,
        interrupt_on={"edit_file":InterruptOnConfig(allowed_decisions=["approve", "reject"])},  # gate edits 
    )

    prompt = (
        "1) write_file /workspace/notes.md with 'line1\\nline2\\n'\n"
        "2) edit_file to replace 'line2' with 'LINE2_EDITED'\n"
        "3) read_file and print the contents\n"
    )

    print("\n=== RUN (expect interrupt) ===")
   
    out=agent.invoke(
        {"messages": [{"role": "user", "content": prompt}]},
        config={"configurable": {"thread_id": thread_id}},
        )
    if "__interrupt__" in out:
      intr = out["__interrupt__"][0]          # Interrupt(...)
      hitl_request = intr.value               # what needs approval
      print("INTERRUPT:", hitl_request)

    # ---- HITL ----
    decision = input("\nApprove the pending operation? (approve/reject): ").strip().lower()
    if decision not in ("approve", "reject"):
        decision = "reject"

    print("\n=== RESUME ===")
    out = agent.invoke(
        Command(resume={"decisions": [{"type": decision}]}),
        config={"configurable": {"thread_id": thread_id}},
    )
    print("\n=== FINAL ===\n")
    print(out["messages"][-1].content)


if __name__ == "__main__":
    main()
