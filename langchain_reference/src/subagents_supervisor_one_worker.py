from __future__ import annotations
from langchain.agents import create_agent
from langchain.tools import tool

from config import get_chat_model

def _last_text(result: dict) -> str:
    """
    Return last text from agent result dictionary
    """
    msg = result['messages'][-1]
    # Different LC message classes expose text differently.
    return getattr(msg, "text", None) or getattr(msg, "content", None) or str(msg)

def main():
    model = get_chat_model()
    # 1) Worker agent
    WORKER_PROMPT = (
        "You are a summarization specialist. \n"
         "Given text, produce:\n"
        "- 1 sentence summary\n"
        "- 3 bullet key points\n"
        "Keep it concise.\n"
    )

    worker_agent = create_agent(model, tools=[], system_prompt=WORKER_PROMPT)

    # Wrap worker agent in tool scaffolding
    @tool("summarize_text", description="Summarize long text into a short summary + 3 bullet points.")
    def summarize_text(text: str) -> str:
        result = worker_agent.invoke({"messages": [{"role": "user", "content": text}]})
        return _last_text(result)  # supervisor sees ONLY this final text
    
    # 3) Supervisor agent orchestrates tools (here, only one tool)
    SUPERVISOR_PROMPT = (
        "You are a helpful assistant.\n"
        "If the user asks to summarize something (or provides a long passage), call summarize_text.\n"
        "Otherwise answer normally.\n"
        "When you call summarize_text, pass the user's passage as-is.\n"
    )
    supervisor = create_agent(model, tools=[summarize_text], system_prompt=SUPERVISOR_PROMPT)

    # 4) Demo query
    query = (
        "Summarize this:\n\n"
        "LangChain and LangGraph are frameworks for building LLM applications and agents. "
        "LangChain provides core abstractions like models, tools, and prompts. "
        "LangGraph helps you build stateful agent workflows as graphs, enabling persistence, "
        "interrupts, and multi-agent coordination."
    )

    print("\n=== Supervisor streaming ===")
    for step in supervisor.stream({"messages": [{"role": "user", "content": query}]}):
        for update in step.values():
            for message in update.get("messages", []):
                message.pretty_print()

    # Or if you prefer non-streaming:
    # out = supervisor.invoke({"messages": [{"role": "user", "content": query}]})
    # print("\n=== Final ===\n", _last_text(out))


if __name__ == "__main__":
    main()