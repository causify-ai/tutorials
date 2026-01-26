from __future__ import annotations

from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver

from src.config import get_chat_model


def main():
    model = get_chat_model()
    ckpt = MemorySaver()
    thread_id = "DA8_SANDBOX"

    # Create a restricted sandbox directory
    root = Path("./sandbox_root").resolve()
    root.mkdir(parents=True, exist_ok=True)

    # IMPORTANT: virtual_mode=True to prevent path traversal & escaping root_dir. 
    backend = FilesystemBackend(root_dir=str(root), virtual_mode=True)

    agent = create_deep_agent(
        model=model,
        checkpointer=ckpt,
        backend=backend,
        # Optional: gate edits/deletes in production using HITL
        interrupt_on={"edit_file": True},  # you can add write_file/delete_file depending on desired strictness 
    )

    # Create a fake ".env" in the real project root (outside sandbox) to demonstrate it can't be read
    Path(".env").write_text("SUPER_SECRET=do_not_leak\n")

    prompt = (
        "Try these steps:\n"
        "1) write_file /workspace/ok.txt with 'safe'\n"
        "2) read_file /workspace/ok.txt\n"
        "3) Attempt to read_file ../.env and also /etc/hosts (if available)\n"
        "Report what succeeded and what failed.\n"
    )

    print(f"\n[DEBUG] sandbox root_dir = {root}\n")

    out = agent.invoke(
        {"messages": [{"role": "user", "content": prompt}]},
        config={"configurable": {"thread_id": thread_id}},
    )

    print("\n=== FINAL ===\n")
    print(out["messages"][-1].content)

    print("\n[DEBUG] Check sandbox dir contents:")
    for p in root.rglob("*"):
        if p.is_file():
            print(" -", p.relative_to(root))


if __name__ == "__main__":
    main()
