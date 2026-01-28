from __future__ import annotations

from langchain.agents import create_agent
from langchain.tools import tool  # or: from langchain_core.tools import tool
from config import get_chat_model


def _last_text(result: dict) -> str:
    msg = result["messages"][-1]
    return getattr(msg, "text", None) or getattr(msg, "content", None) or str(msg)


def main():
    model = get_chat_model()

    # Worker A: date normalization
    DATE_WORKER_PROMPT = (
        "You normalize date/time expressions.\n"
        "Input: a user sentence that mentions a date/time.\n"
        "Output: ONLY a JSON object with keys:\n"
        '  {"normalized": "<ISO-ish or explicit format>", "notes": "<assumptions>"}\n'
        "If date is ambiguous, make a best guess and explain in notes.\n"
    )
    date_agent = create_agent(model, tools=[], system_prompt=DATE_WORKER_PROMPT)

    @tool(
        "normalize_datetime",
        description=(
            "Convert informal date/time mentions (e.g., 'next Tuesday 2pm', 'tomorrow morning') "
            "into a normalized explicit format. Returns JSON."
        ),
    )
    def normalize_datetime(request: str) -> str:
        return _last_text(date_agent.invoke({"messages": [{"role": "user", "content": request}]}))

    # Worker B: email drafting
    EMAIL_WORKER_PROMPT = (
        "You draft short, professional emails.\n"
        "Input: a request describing who to email and what to say.\n"
        "Output: ONLY the email body (no subject line unless asked).\n"
        "Tone: polite, concise.\n"
    )
    email_agent = create_agent(model, tools=[], system_prompt=EMAIL_WORKER_PROMPT)

    @tool(
        "draft_email_body",
        description=(
            "Draft a concise professional email body for a user request. "
            "Use when the user wants to email/message someone."
        ),
    )
    def draft_email_body(request: str) -> str:
        return _last_text(email_agent.invoke({"messages": [{"role": "user", "content": request}]}))

    # Supervisor
    SUPERVISOR_PROMPT = (
        "You are a supervisor.\n"
        "You have two tools:\n"
        "- normalize_datetime: for date/time normalization\n"
        "- draft_email_body: for writing email bodies\n"
        "Pick the tool that best matches the user's intent.\n"
        "If the request clearly needs both, you may call both tools.\n"
        "Return a clean final answer.\n"
    )

    supervisor = create_agent(model, tools=[normalize_datetime, draft_email_body], system_prompt=SUPERVISOR_PROMPT)

    tests = [
        # "What date is 'next Tuesday at 2pm' in a normalized format?",
        "Write an email to my professor asking for a 2-day extension on the assignment due today (conveyed in a normalized format)",
    #     "Draft a message to my teammate: can we meet tomorrow morning for 30 minutes?",
    #     "Normalize: 'first Monday of next month at noon'.",
    #     "Email: apologize for missing the meeting and ask for notes.",
    #     "Normalize: 'in 90 minutes'.",
    ]

    for i, q in enumerate(tests, 1):
        print(f"\n\n===================== TEST {i} =====================")
        print("USER:", q)
        for step in supervisor.stream({"messages": [{"role": "user", "content": q}]}):
            for update in step.values():
                for message in update.get("messages", []):
                    message.pretty_print()


if __name__ == "__main__":
    main()
