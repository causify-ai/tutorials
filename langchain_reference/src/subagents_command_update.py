from __future__ import annotations

import json
from typing import TypedDict, Annotated

from langchain.agents import create_agent, AgentState
from langchain.tools import tool
from langchain.messages import ToolMessage  # if this import fails: from langchain_core.messages import ToolMessage
from langgraph.types import Command
from langchain.tools import InjectedToolCallId  # injected tool call id

from config import get_chat_model


class CustomState(AgentState):
    facts: list[str]


def _last_text(result: dict) -> str:
    msg = result["messages"][-1]
    return getattr(msg, "content", None) or getattr(msg, "text", None) or str(msg)


def main():
    model = get_chat_model()

    # Worker: extract facts as JSON
    FACT_WORKER_PROMPT = (
        "Extract 3-5 key facts from the input.\n"
        "Return ONLY valid JSON: {\"facts\": [\"...\", \"...\", ...]}\n"
    )
    fact_worker = create_agent(model, tools=[], system_prompt=FACT_WORKER_PROMPT)

    @tool("extract_facts", description="Extract key facts from text and store them into supervisor state.")
    def extract_facts(
        text: str,
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        result = fact_worker.invoke({"messages": [{"role": "user", "content": text}]})
        raw = _last_text(result)

        # Parse JSON; if it fails, degrade gracefully.
        facts: list[str]
        try:
            obj = json.loads(raw)
            facts = list(obj.get("facts", []))
        except Exception:
            facts = [raw]

        # Important: return ToolMessage with tool_call_id + update supervisor state
        return Command(
            update={
                "facts": facts,
                "messages": [
                    ToolMessage(
                        content=f"Stored {len(facts)} facts.",
                        tool_call_id=tool_call_id,
                    )
                ],
            }
        )

    SUPERVISOR_PROMPT = (
        "You are a supervisor.\n"
        "1) Call extract_facts on the user's passage.\n"
        "2) Then answer the user using those facts (paraphrase).\n"
        "If facts exist in state, rely on them.\n"
    )
    supervisor = create_agent(model, tools=[extract_facts], system_prompt=SUPERVISOR_PROMPT, state_schema=CustomState)

    passage = (
        "LangGraph lets you build stateful agent workflows as graphs. "
        "It supports persistence and interrupts, and can coordinate multiple agents."
    )

    out = supervisor.invoke(
        {"messages": [{"role": "user", "content": f"Read this and explain it:\n\n{passage}"}], #type:ignore
         "facts": []}
    )

    print("\n[DEBUG] Updated facts in final state:")
    print(out.get("facts"))

    print("\n[DEBUG] Final assistant answer:")
    print(out["messages"][-1].content)


if __name__ == "__main__":
    main()
