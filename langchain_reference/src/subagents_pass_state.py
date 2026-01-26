from __future__ import annotations

import argparse
from typing import TypedDict, Annotated

from langchain.agents import create_agent, AgentState
from langchain.tools import tool, ToolRuntime  # ToolRuntime injected automatically
from config import get_chat_model


class CustomState(AgentState):
    # AgentState already includes "messages"
    user_prefs: dict


def _last_text(result: dict) -> str:
    msg = result["messages"][-1]
    return getattr(msg, "content", None) or getattr(msg, "text", None) or str(msg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tone", default="neutral", choices=["neutral", "friendly", "formal"])
    args = ap.parse_args()

    model = get_chat_model()

    # Worker agent: can do general rewriting, but obeys the extra instruction we inject.
    WORKER_PROMPT = (
        "You are a rewriting assistant. Return only the rewritten text.\n"
        "Keep it short.\n"
    )
    worker = create_agent(model, tools=[], system_prompt=WORKER_PROMPT)

    @tool(
        "rewrite_with_prefs",
        description="Rewrite the user's text following preferences from supervisor state (tone, style).",
    )
    def rewrite_with_prefs(
        text: str,
        runtime: ToolRuntime[None, CustomState],
    ) -> str:
        # Pull preferences from the supervisor's state
        # print("[DEBUG]: Tool: Runtime:", runtime)
        prefs = runtime.state.get("user_prefs", {})
        print("[DEBUG]: Tool: Pref:", prefs)
        tone = prefs.get("tone", "neutral")

        # Inject "just enough" state into the worker's messages:
        worker_msgs = [
            {"role": "system", "content": f"Rewrite tone must be: {tone}. And verbose."},
            {"role": "user", "content": text},
        ]
        result = worker.invoke({"messages": worker_msgs}) #type: ignore
        return _last_text(result)

    SUPERVISOR_PROMPT = (
        "You are a supervisor.\n"
        "Always call rewrite_with_prefs for rewriting requests.\n"
        "Return the tool result as the final answer.\n"
    )
    supervisor = create_agent(model, tools=[rewrite_with_prefs], system_prompt=SUPERVISOR_PROMPT, state_schema=CustomState)

    # Supervisor state carries user_prefs.
    state = {
        "messages": [{"role": "user", "content": "Rewrite: please send me the report by tonight."}],
        "user_prefs": {"tone": args.tone},
    }

    print(f"\n[DEBUG] user_prefs = {state['user_prefs']}\n")

    # Stream so you can see tool-calling behavior
    for step in supervisor.stream(state): #type: ignore
        for update in step.values():
            for m in update.get("messages", []):
                m.pretty_print()


if __name__ == "__main__":
    main()
