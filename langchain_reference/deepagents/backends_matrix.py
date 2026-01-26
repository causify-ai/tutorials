from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Dict, Any

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend, StoreBackend, CompositeBackend, StateBackend
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

from src.config import get_chat_model


NOTE_STATE = "/workspace/notes.md"
NOTE_FS = "/workspace/notes.md"         # will map into local FS root_dir
NOTE_STORE = "/memories/notes.md"       # recommended pattern with CompositeBackend routes


def run(agent, thread_id: str, user_msg: str) -> Dict[str, Any]:
    # create_deep_agent returns a compiled LangGraph graph; pass thread_id via config :contentReference[oaicite:9]{index=9}
    return agent.invoke(
        {"messages": [{"role": "user", "content": user_msg}]},
        config={"configurable": {"thread_id": thread_id}},
    )


def main():
    model = get_chat_model()

    # Checkpointer is what makes "same thread" persist across turns for state backends. :contentReference[oaicite:10]{index=10}
    ckpt = MemorySaver()

    # --------
    # 1) Default StateBackend (ephemeral-by-thread)
    # --------
    agent_state = create_deep_agent(model=model, checkpointer=ckpt)
    # Default backend is StateBackend (ephemeral in state, per thread). 

    # --------
    # 2) Local filesystem backend (persist across threads because it's real disk)
    # --------
    root = Path("./fs_root").resolve()
    root.mkdir(parents=True, exist_ok=True)

    agent_fs = create_deep_agent(
        model=model,
        checkpointer=ckpt,
        backend=FilesystemBackend(root_dir=str(root), virtual_mode=True),  # recommended safety :contentReference[oaicite:12]{index=12}
    )

    # --------
    # 3) Store backend via CompositeBackend:
    #    keep /workspace ephemeral, persist /memories in StoreBackend
    # --------
    store = InMemoryStore()
    composite_backend = lambda rt: CompositeBackend(
        default=StateBackend(rt),
        routes={"/memories/": StoreBackend(rt)},
    )
    agent_store = create_deep_agent(
        model=model,
        checkpointer=ckpt,
        backend=composite_backend,
        store=store,  # required for StoreBackend :contentReference[oaicite:13]{index=13}
    )

    # -------------------------------------------------------------------
    # Test plan:
    # - Thread A writes note
    # - Thread A reads note (should succeed for all three)
    # - Thread B reads note:
    #     * StateBackend: should FAIL (different thread)
    #     * FilesystemBackend: should SUCCEED (disk)
    #     * StoreBackend via /memories/: should SUCCEED (store spans threads)
    # -------------------------------------------------------------------

    print("\n================ DA4: STATE BACKEND ================")
    tA, tB = "STATE_A", "STATE_B"
    run(agent_state, tA, f"Use write_file to write '{NOTE_STATE}' with: 'hello from STATE thread A'. Then say 'wrote'.")
    outA = run(agent_state, tA, f"Use read_file to read '{NOTE_STATE}'. Then print the exact content you read.")
    print("Thread A read:", outA["messages"][-1].content)

    outB = run(agent_state, tB, f"Use read_file to read '{NOTE_STATE}'. If missing, say so.")
    print("Thread B read:", outB["messages"][-1].content)

    print("\n================ DA4: FILESYSTEM BACKEND ================")
    tA, tB = "FS_A", "FS_B"
    run(agent_fs, tA, f"Use write_file to write '{NOTE_FS}' with: 'hello from FS thread A'. Then say 'wrote'.")
    outA = run(agent_fs, tA, f"Use read_file to read '{NOTE_FS}'. Then print the exact content you read.")
    print("Thread A read:", outA["messages"][-1].content)

    outB = run(agent_fs, tB, f"Use read_file to read '{NOTE_FS}'. Then print the exact content you read.")
    print("Thread B read:", outB["messages"][-1].content)
    print(f"[DEBUG] Local root_dir on disk: {root}")

    print("\n================ DA4: STORE BACKEND (Composite /memories) ================")
    tA, tB = "STORE_A", "STORE_B"
    run(agent_store, tA, f"Use write_file to write '{NOTE_STORE}' with: 'hello from STORE thread A'. Then say 'wrote'.")
    outA = run(agent_store, tA, f"Use read_file to read '{NOTE_STORE}'. Then print the exact content you read.")
    print("Thread A read:", outA["messages"][-1].content)

    outB = run(agent_store, tB, f"Use read_file to read '{NOTE_STORE}'. Then print the exact content you read.")
    print("Thread B read:", outB["messages"][-1].content)

    print("\n=== Expected behavior summary ===")
    print("- StateBackend: Thread B should NOT see Thread A's /workspace file (thread-scoped).")
    print("- FilesystemBackend: Thread B SHOULD see the file (disk).")
    print("- StoreBackend (/memories): Thread B SHOULD see the file (store spans threads).")


if __name__ == "__main__":
    main()
