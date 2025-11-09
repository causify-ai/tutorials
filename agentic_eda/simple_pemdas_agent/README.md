# Simple PEMDAS Agent

A tiny workspace for experimenting with self-looping LangGraph agents that enforce BEDMAS/PEMDAS order of operations. The goal is to keep everything transparent: each tool call is explicit, the state is tiny, and the agent loops until it decides the expression is fully solved.

## Contents
- `testflow.py` – minimal agent with a single `llm_agent` node that *manually* calls helper scripts via a Python dict.
- `testflow2.py` – a slightly more advanced agent that leans on LangGraph’s `ToolNode` and message passing.
- `add.py`, `sub.py`, `mult.py`, `div.py`, `exp.py` – deterministic helper modules providing `run(a, b)` primitives.
- `testflow_explained.md` and `testflow2_explained.md` – companion docs detailing each flow.

## Motivation
Large, multi-tool agents in `agentic_eda` can be hard to reason about. This folder isolates the smallest “math-only” scenario so you can verify LangGraph wiring, observe how LLM planning interacts with deterministic tools, and benchmark alternative orchestration styles before promoting ideas back into bigger agents.

## Architectural Contrast

### Tool Dispatch
- `testflow.py`: Custom Python dict that calls each helper directly after the LLM responds.
- `testflow2.py`: LangGraph `ToolNode` executes @tool-decorated wrappers and feeds the output back as `ToolMessage`s.

### State Shape
- `testflow.py`: `MathState` has `expression`, `scratchpad`, `status`, `result` with no internal message history.
- `testflow2.py`: Extends `MathState` with `messages` managed by `langgraph.graph.message.add_messages`, enabling richer context passing.

### Routing
- `testflow.py`: Single node loop `START → llm_agent → (llm_agent or END)` routed by `should_continue`.
- `testflow2.py`: Three-node loop `llm_agent → tools → observe` with conditional edges (`from_llm`, `next_step`).

### Validation
- `testflow.py`: Uses a Pydantic `MathOperation` schema so the LLM must declare the next operation, new expression, and status.
- `testflow2.py`: Allows the LLM to emit either tool calls or final floats; the `observe` node validates output via regex and updates state.

### Observability
- `testflow.py`: Logs each executed tool inline without streaming helpers.
- `testflow2.py`: Provides `pp_update` for LangGraph streaming traces so you can watch decisions live.

Both scripts depend on `OPENAI_API_KEY` and the LangChain/LangGraph stack (`langchain-openai`, `langgraph`, `pydantic`). Choose the flow that matches the level of automation you need: `testflow.py` for ultimate transparency, `testflow2.py` for production-style tool orchestration.
