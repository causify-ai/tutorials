from __future__ import annotations

from langchain_core.messages import HumanMessage
from langchain.agents import create_agent

from config import get_chat_model
from tools.agent_tools import mean
from middleware.log_middleware import log_before_agent

def main():
    agent = create_agent(
        model=get_chat_model(),
        tools=[mean],
        middleware=[log_before_agent],
        system_prompt="Use tools for computation.",
    )

    out = agent.invoke({"messages": [HumanMessage(content="mean([1, 5, 9]) please")]})

    print("audit:", out.get("audit"))
    print("final answer:", out["messages"][-1].content)
    print(out)

if __name__ == "__main__":
    main()
