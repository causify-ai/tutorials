from __future__ import annotations

from langchain.agents import create_agent
from langchain.tools import tool
from config import get_chat_model


def _last_text(result: dict) -> str:
    msg = result["messages"][-1]
    return getattr(msg, "content", None) or getattr(msg, "text", None) or str(msg)


def main():
    model = get_chat_model()

    # Three workers (as subagents)
    sum_agent = create_agent(model, tools=[], system_prompt="Summarize in 2 sentences. Return only the summary.")
    act_agent = create_agent(model, tools=[], system_prompt="Extract action items as bullets. Return only bullets.")
    reply_agent = create_agent(model, tools=[], system_prompt="Draft a short reply email. Return only the email body.")

    @tool("sub_summarize", description="Summarize the text in 2 sentences.")
    def sub_summarize(text: str) -> str:
        return _last_text(sum_agent.invoke({"messages": [{"role": "user", "content": text}]}))

    @tool("sub_action_items", description="Extract action items as bullet points.")
    def sub_action_items(text: str) -> str:
        return _last_text(act_agent.invoke({"messages": [{"role": "user", "content": text}]}))

    @tool("sub_draft_reply", description="Draft a short email reply addressing the content.")
    def sub_draft_reply(text: str) -> str:
        return _last_text(reply_agent.invoke({"messages": [{"role": "user", "content": text}]}))

    SUPERVISOR_PROMPT = (
        "You are a supervisor.\n"
        "For the user's message, call ALL THREE tools in a single turn:\n"
        "1) sub_summarize\n"
        "2) sub_action_items\n"
        "3) sub_draft_reply\n"
        "Then produce a final response with sections Summary / Action Items / Draft Reply.\n"
        "Do not skip tools.\n"
    )

    supervisor = create_agent(
        model,
        tools=[sub_summarize, sub_action_items, sub_draft_reply],
        system_prompt=SUPERVISOR_PROMPT,
    )

    email_thread = (
        "Hi team,\n"
        "We need to ship the notebook execution feature by Friday. "
        "Please confirm if papermill is working in your env. "
        "Also document where artifacts land after execution.\n"
        "Thanks!"
    )

    print("\n=== Streaming: look for ONE AI message with 3 tool calls ===\n")
    for step in supervisor.stream({"messages": [{"role": "user", "content": email_thread}]}):
        for update in step.values():
            for m in update.get("messages", []):
                m.pretty_print()


if __name__ == "__main__":
    main()
