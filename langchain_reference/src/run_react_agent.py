from __future__ import annotations

from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
import sys
from typing import cast
from config import get_chat_model
from tools.agent_tools import utc_now, mean, sqrt
from langchain.agents import AgentState

def main():
    llm = get_chat_model()
    tools = [utc_now, mean, sqrt]

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are a careful assistant. Use tools when computation or time is required. "
            "When you call a tool, use its output in your final answer."
        ),
    )

    # This question *forces* tool use (time + math).
    inputs = {
        "messages": [
            HumanMessage(content="Compute mean([1,2,3,4,10]) and sqrt(49). Also tell me the current UTC time.")
        ]
    }

    print("=== Streaming updates ===")
    for chunk in agent.stream(inputs, stream_mode="updates"): # type: ignore[arg-type]
        print(chunk)

if __name__ == "__main__":
    main()
