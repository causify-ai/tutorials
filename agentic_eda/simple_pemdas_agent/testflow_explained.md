# Understanding `testflow.py`: Minimal BEDMAS LangGraph Loop

`agentic_eda/simple_pemdas_agent/testflow.py` is the smallest possible LangGraph agent for solving math expressions with BEDMAS discipline. It deliberately avoids fancy routing nodes so you can see every moving part of a self-looping agent that keeps calling a single function until it declares the task finished.

---

## Core Ideas

1. **State-first design**
   ```python
   class MathState(TypedDict):
       expression: str
       scratchpad: Annotated[list[str], operator.add]
       status: Literal["ongoing", "done"]
       result: float | None
   ```
   - `expression` is the string the agent is currently simplifying.
   - `scratchpad` accumulates short, human-readable notes (thanks to `operator.add`, LangGraph appends instead of overwriting).
   - `status` gates the routing function `should_continue` so the graph knows when to stop.
   - `result` mirrors the final expression once the agent reaches `"done"`.

2. **Manual tool bridge**
   - Each arithmetic helper (`add.py`, `sub.py`, etc.) exposes a `run(a, b)` function.
   - `testflow.py` wraps them inside plain Python functions (`call_addition`, `call_division`, …) and stores them in a `TOOLS` dict keyed by the LLM’s tool names.
   - When the LLM returns `tool_name`, `a`, `b`, and a simplified expression, the script immediately calls `TOOLS[tool_name](a, b)` and logs the result to the scratchpad.
   - This manual bridge is the key difference from `testflow2.py`, which lets LangGraph’s `ToolNode` dispatch tool calls automatically.

3. **Structured LLM output**
   - The `llm_agent` node requests a `MathOperation` Pydantic object (`tool_name`, `a`, `b`, `simplified`, `status`) via `model.with_structured_output`.
   - `status` comes directly from the LLM. When it says `"done"`, the node writes the numeric `simplified` value into `result`, enabling the router to terminate.
   - Because there is no `ToolNode`, the LLM must always propose the next expression itself; the script prints every step for easy tracing.

4. **Graph wiring**
   ```python
   builder = StateGraph(MathState)
   builder.add_node("llm_agent", llm_agent)
   builder.add_edge(START, "llm_agent")
   builder.add_conditional_edges("llm_agent", should_continue, ["llm_agent", END])
   graph = builder.compile()
   ```
   - Only one node exists (`llm_agent`). After each turn, `should_continue` inspects `status`: keep looping or exit.
   - The entire agent therefore fits into ~30 lines of graph code, making it ideal for debugging LangGraph state transitions.

5. **Running it**
   ```bash
   export OPENAI_API_KEY=...
   python agentic_eda/simple_pemdas_agent/testflow.py
   ```
   - The script seeds `expression = "(5^2) + (3-4) * (6 * 2) / (3 + 20)"`.
   - The loop continues until the LLM emits `status="done"` and `simplified="1.0869565"`.

---

## When to Use `testflow.py`

- You want the most transparent view of how a LangGraph agent can orchestrate tools without any LangGraph-provided helper nodes.
- You need to customize how tool outputs are recorded (e.g., logging, custom telemetry) before updating state.
- You are teaching LangGraph basics and want an example that fits on one screen yet demonstrates BEDMAS reasoning, structured outputs, and routing.

For richer telemetry, auto tool dispatch, and streaming traces, look at `testflow2_explained.md`, which documents the upgraded ToolNode-based variant.
