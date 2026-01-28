from __future__ import annotations

from langchain_core.messages import HumanMessage
from langchain.agents import create_agent

from config import get_chat_model
from tools.agent_tools import utc_now, mean, sqrt

def main():
    llm = get_chat_model()
    agent = create_agent(
        model=llm,
        tools=[utc_now, mean, sqrt],
        system_prompt="Be concise. Use tools for math/time. End with a final answer.",
    )

    inputs = {
        "messages": [HumanMessage(content="What is sqrt(81) and the mean of [2,2,8]?")]
    }

    final_state = agent.invoke(inputs)  # type: ignore

    # The reference states the agent returns the full list of messages. :contentReference[oaicite:5]{index=5}
    print("\n=== Final state keys ===")
    print(list(final_state.keys()))

    print("\n=== Messages ===")
    for i, m in enumerate(final_state["messages"]):
        # HumanMessage / AIMessage / ToolMessage, etc.
        name = type(m).__name__
        extra = ""
        if hasattr(m, "tool_calls") and m.tool_calls:
            extra = f" tool_calls={m.tool_calls}"
        if hasattr(m, "name") and m.name:
            extra += f" name={m.name}"
        print(f"[{i}] {name}:{extra}\n{m.content}\n")

if __name__ == "__main__":
    main()
