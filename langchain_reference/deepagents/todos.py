from __future__ import annotations

import json
from deepagents import create_deep_agent
from src.config import get_chat_model


def main():
    model = get_chat_model()
    agent = create_deep_agent(model=model)

    prompt = (
        "Before doing anything else, call write_todos with 5 EDA tasks for a multivariate time series. "
        "Then mark the first task as in_progress and briefly explain why you chose that ordering."
    )

    out_state = agent.invoke({"messages": [{"role": "user", "content": prompt}]})

    print("\n=== FINAL ANSWER ===\n")
    print(out_state["messages"][-1].content)

    print("\n=== TODOS (raw) ===")
    todos = out_state.get("todos", None)
    # 'todos' is a state channel used by the TodoListMiddleware / write_todos tool. 
    print(todos)

    # If it's JSON-ish, show it nicely:
    try:
        print("\n=== TODOS (pretty) ===")
        print(json.dumps(todos, indent=2))
    except Exception:
        pass


if __name__ == "__main__":
    main()
