from __future__ import annotations

from deepagents import create_deep_agent
from src.config import get_chat_model


def main():
    # Deep agents require a tool-calling-capable model. :contentReference[oaicite:6]{index=6}
    model = get_chat_model()

    agent = create_deep_agent(model=model)

    prompt = (
        "You are given a multivariate time-series dataset (unknown schema). "
        "Make a 5-step plan for doing EDA, then summarize what insights you'd try to extract."
    )

    out_state = agent.invoke(
        {"messages": [{"role": "user", "content": prompt}]}
    )

    # out_state is LangGraph state; messages are in out_state["messages"] :contentReference[oaicite:7]{index=7}
    final_msg = out_state["messages"][-1]
    print("\n=== FINAL ===\n")
    print(getattr(final_msg, "content", str(final_msg)))

    # Optional: show which channels exist
    print("\n=== STATE KEYS ===")
    print(list(out_state.keys()))


if __name__ == "__main__":
    main()
