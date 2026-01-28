from __future__ import annotations

from langchain.agents import create_agent
from langchain.tools import tool  # or: from langchain_core.tools import tool
from config import get_chat_model


def _msg_text(m) -> str:
    return getattr(m, "text", None) or getattr(m, "content", None) or str(m)


def _last_text(result: dict) -> str:
    return _msg_text(result["messages"][-1])


def _transcript_stats(result: dict) -> tuple[int, int]:
    """(n_messages, total_chars) from an agent run result dict."""
    msgs = result.get("messages", [])
    total = sum(len(_msg_text(m)) for m in msgs)
    return len(msgs), total


def main():
    model = get_chat_model()

    # Low-level tool used ONLY inside the worker agent
    @tool("generate_noise", description="Generate a long string to simulate noisy intermediate work.")
    def generate_noise(n_chars: int) -> str:
        return "X" * int(n_chars)

    WORKER_PROMPT = (
        "You are a noisy worker agent.\n"
        "You MUST:\n"
        "1) Call generate_noise with n_chars=8000 exactly once.\n"
        "2) Then ignore the noise.\n"
        "3) Return ONLY a concise 2-sentence answer to the user.\n"
        "Do NOT include the noise in your final answer.\n"
    )
    worker = create_agent(model, tools=[generate_noise], system_prompt=WORKER_PROMPT)

    # Wrap worker as a subagent tool
    @tool("noisy_worker", description="Do a task in an isolated context window and return a concise final answer.")
    def noisy_worker(task: str) -> str:
        result = worker.invoke({"messages": [{"role": "user", "content": task}]})

        n_msgs, total_chars = _transcript_stats(result)
        print("\n[DEBUG] Worker internal transcript:")
        print(f"[DEBUG]   n_messages = {n_msgs}")
        print(f"[DEBUG]   approx_chars = {total_chars}")
        print("[DEBUG]   worker_final =", _last_text(result))

        # Supervisor sees only this final content
        return _last_text(result)

    SUPERVISOR_PROMPT = (
        "You are a supervisor.\n"
        "Call noisy_worker.\n"
        "Otherwise answer directly.\n"
        "When using noisy_worker, pass the user's request as the tool input.\n"
    )
    supervisor = create_agent(model, tools=[noisy_worker], system_prompt=SUPERVISOR_PROMPT)

    query = "Explain in plain English what 'context isolation' means in subagents."

    print("\n=== Supervisor streaming ===")
    for step in supervisor.stream({"messages": [{"role": "user", "content": query}]}):
        for update in step.values():
            for message in update.get("messages", []):
                message.pretty_print()

    # Optional: show supervisor transcript size too
    out = supervisor.invoke({"messages": [{"role": "user", "content": query}]})
    sup_n, sup_chars = _transcript_stats(out)
    print("\n[DEBUG] Supervisor transcript:")
    print(f"[DEBUG]   n_messages = {sup_n}")
    print(f"[DEBUG]   approx_chars = {sup_chars}")
    print("[DEBUG]   supervisor_final =", _last_text(out))


if __name__ == "__main__":
    main()
