from __future__ import annotations

from deepagents import create_deep_agent, CompiledSubAgent
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

from src.config import get_chat_model


def main():
    model = get_chat_model()
    ckpt = MemorySaver()

    # Build a compiled agent graph to use as a subagent runnable 
    specialized_prompt = (
        "You are a strict 'hypothesis generator' for EDA.\n"
        "Input: dataset description.\n"
        "Output:\n"
        "- 2 plausible hypotheses (bullet list)\n"
        "- For each hypothesis: 1 test/plot you would run\n"
        "Be concrete, yet concise.\n"
    )
    compiled_worker_graph = create_agent(model=model, tools=[], system_prompt=specialized_prompt)

    compiled_subagent = CompiledSubAgent(
        name="hypothesis-agent",
        description="Generates plausible hypotheses and concrete tests/plots for EDA.",
        runnable=compiled_worker_graph,
    )

    agent = create_deep_agent(
        model=model,
        checkpointer=ckpt,
        subagents=[compiled_subagent],
        name="main-agent",
    )

    prompt = (
        "Dataset: multivariate time series, minute-level, sensors S1..S4, occasional missingness.\n"
        "Delegate to hypothesis-agent to generate hypotheses + tests.\n"
        "Use task(name='hypothesis-agent', task='...').\n"
        "Then present the results cleanly in not more than 2 sentences."
    )

    out = agent.invoke(
        {"messages": [{"role": "user", "content": prompt}]},
        config={"configurable": {"thread_id": "DA6"}},
    )

    print("\n=== FINAL ===\n")
    print(out["messages"][-1].content)


if __name__ == "__main__":
    main()
