# Understanding `testflow2.py`: An Agentic Math Solver

This document breaks down the `agentic_eda/simple_pemdas_agent/testflow2.py` script, which implements a robust mathematical expression solver using the LangGraph library. The agent is designed to solve expressions by strictly following the order of operations (BEDMAS/PEMDAS), calling one specific tool for each step.

## Overview

The script defines a stateful graph where a Large Language Model (LLM) acts as the "brain" or agent. Given a mathematical expression, the agent repeatedly decides on the single next operation to perform, calls the appropriate tool (e.g., `addition`, `multiplication`), observes the result, and updates the expression. This loop continues until the expression is fully reduced to a single number.

The key design goals are **correctness** and **observability**. The agent is heavily constrained to prevent it from taking shortcuts or making calculation errors, ensuring each step is a verifiable tool call.

---

## Core Components

The script is built from several key parts that work together within the LangGraph framework.

### 1. State Management (`MathState`)

The entire process is managed through a `MathState` dictionary, which tracks the agent's progress.

```python
class MathState(TypedDict):
    expression: str
    scratchpad: Annotated[list[str], operator.add]
    status: Literal["ongoing", "done"]
    result: float | None
    # internal messages for ToolNode
    messages: Annotated[Sequence, add_messages]
```

- **`expression`**: The current state of the mathematical expression string, which gets simplified at each step.
- **`scratchpad`**: A log that records the operations performed by the agent. The `operator.add` annotation tells LangGraph to append new entries to this list rather than overwriting it.
- **`status`**: Tracks whether the process is `"ongoing"` or `"done"`.
- **`result`**: Stores the final floating-point number once the calculation is complete.
- **`messages`**: An internal list for communication between the LLM, tools, and the graph. This is where the history of prompts, AI responses, and tool outputs is maintained.

### 2. Tools: Wrapping Python Scripts

The basic arithmetic operations are defined in separate Python scripts (`add.py`, `sub.py`, etc.). These are wrapped into LangChain `@tool`-decorated functions.

```python
@tool
def addition(a: float, b: float) -> float:
    """Compute a+b."""
    print("[proof] add tool being called")
    return float(add.run(a, b))

TOOLS = [exponentiation, multiplication, division, addition, subtraction]
```

This is a powerful pattern:
- It keeps the core logic (the math) separate from the agentic orchestration.
- The docstrings of these functions are automatically provided to the LLM, teaching it how and when to use each tool.
- Pydantic type hints (`a: float, b: float`) ensure the LLM provides arguments in the correct format.

### 3. The Model and System Prompt: Guiding the Agent

The script uses a ChatOpenAI model (`gpt-4o`) and binds the tools to it.

```python
# parallel_tool_calls=False ensures exactly one tool call each loop
model = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(
    TOOLS, parallel_tool_calls=False
)

SYSTEM = SystemMessage(content=(
    "You are a strict math executor. Follow BEDMAS (PEMDAS)."
    "\nRules you MUST follow:"
    "\n1) If parentheses exist, reduce an operation **inside the innermost parentheses first**."
    "\n2) Each step you MUST call **exactly one** tool (a, b)."
    "\n3) Do **not** do arithmetic in plain text. Never rewrite the expression except"
    " immediately after a tool call."
    "\n4) After a tool executes, reply with the updated expression string only."
    "\n5) When fully reduced, reply with a single float only."
))
```

This is the most critical part for ensuring correctness:
- **`parallel_tool_calls=False`**: This is a key LangGraph feature that forces the LLM to call only **one tool at a time**. This prevents it from trying to solve multiple parts of the expression at once and makes the process strictly sequential.
- **System Prompt**: The prompt is highly directive, laying out non-negotiable rules. It commands the agent to follow BEDMAS, focus on innermost parentheses, and use tools for all calculations. This prevents the LLM from "cheating" by performing math itself, which is prone to errors.

### 4. Graph Nodes: The Steps of the Loop

The graph consists of three nodes:
1.  **`llm_agent`**: This node is the "brain". It takes the current state (especially the `expression` and `messages` history) and invokes the model. The model's response is either a request to call a tool or, if the work is done, the final numerical answer.
2.  **`tools`**: This is a `ToolNode` that executes the tool call requested by the `llm_agent`. It receives the tool name and arguments, runs the corresponding Python function, and appends the result in a `ToolMessage`.
3.  **`observe`**: This custom node runs after the LLM or a tool. Its job is to inspect the latest message and update the `MathState`. It logs tool outputs to the `scratchpad` and, most importantly, checks if the LLM has returned a final number to terminate the process.

---

## Information and State Flow

The graph defines a clear, cyclical flow of information, managed by the `MathState`.

1.  **START**: The graph begins with the initial state, containing the full expression (e.g., `"(5^2) / (3 + 20)"`).
2.  **`llm_agent`**: The agent receives the expression. It decides the first operation is `5^2` and outputs a message containing a `tool_call` for `exponentiation(a=5, b=2)`.
3.  **Routing (`from_llm`)**: The graph sees the `tool_call` and routes the state to the `tools` node.
4.  **`tools`**: The `ToolNode` executes `exponentiation(5, 2)`, gets `25.0`, and appends a `ToolMessage(content="25.0", name="exponentiation")` to the `messages` list.
5.  **`observe`**: This node sees the new `ToolMessage`. It updates the `scratchpad` with `"exponentiation -> 25.0"`. The state now contains the original expression but also the result of the first step.
6.  **Routing (`next_step`)**: The status is still `"ongoing"`, so the graph routes back to the `llm_agent`.
7.  **`llm_agent` (Loop 2)**: The agent now receives the *updated* message history, which includes the result of the tool call. It is prompted again with the original expression. Its next message is an `AIMessage` containing the *new, simplified expression*: `"25.0 / (3 + 20)"`.
8.  **`observe` (Loop 2)**: This node sees the new `AIMessage` and updates the `expression` in the state to `"25.0 / (3 + 20)"`.
9.  **`llm_agent` (Loop 3)**: The agent sees the new expression, identifies `(3 + 20)` as the next step, and calls `addition(a=3, b=20)`.

This cycle of **LLM -> Tool -> Observe -> LLM** continues until the expression is fully simplified.

---

## Step-by-Step Example: `(5^2) / (3 + 20)`

Here is a trace of how the agent solves the expression, showing the state at each step.

### Step 1 – `llm_agent`
- Action: Sees `(5^2) / (3 + 20)` and plans `exponentiation(a=5, b=2)`.
- Expression: `(5^2) / (3 + 20)`
- Scratchpad: *(no entry yet)*

### Step 2 – `tools`
- Action: Executes `exponentiation(5, 2)` and returns `25.0`.
- Expression: `(5^2) / (3 + 20)`
- Scratchpad: *(no new entry yet)*

### Step 3 – `observe`
- Action: Logs `"exponentiation -> 25.0"` to the scratchpad.
- Expression: `(5^2) / (3 + 20)`
- Scratchpad: `exponentiation -> 25.0`

### Step 4 – `llm_agent`
- Action: Consumes the tool result and replies with a simplified expression.
- Expression: `(5^2) / (3 + 20)`
- Scratchpad: `exponentiation -> 25.0`

### Step 5 – `observe`
- Action: Updates the expression to `25.0 / (3 + 20)`.
- Expression: `25.0 / (3 + 20)`
- Scratchpad: `exponentiation -> 25.0`

### Step 6 – `llm_agent`
- Action: Sees `25.0 / (3 + 20)` and plans `addition(a=3, b=20)`.
- Expression: `25.0 / (3 + 20)`
- Scratchpad: `exponentiation -> 25.0`

### Step 7 – `tools`
- Action: Executes `addition(3, 20)` and returns `23.0`.
- Expression: `25.0 / (3 + 20)`
- Scratchpad: `exponentiation -> 25.0`

### Step 8 – `observe`
- Action: Logs `"addition -> 23.0"` to the scratchpad.
- Expression: `25.0 / (3 + 20)`
- Scratchpad: `addition -> 23.0`

### Step 9 – `llm_agent`
- Action: Uses the tool output to emit the simplified expression `25.0 / (3 + 20)`.
- Expression: `25.0 / (3 + 20)`
- Scratchpad: `addition -> 23.0`

### Step 10 – `observe`
- Action: Updates the expression to `25.0 / 23.0`.
- Expression: `25.0 / 23.0`
- Scratchpad: `addition -> 23.0`

### Step 11 – `llm_agent`
- Action: Identifies division as the final required tool and plans `division(a=25.0, b=23.0)`.
- Expression: `25.0 / 23.0`
- Scratchpad: `addition -> 23.0`

### Step 12 – `tools`
- Action: Executes `division(25.0, 23.0)` and returns `1.09`.
- Expression: `25.0 / 23.0`
- Scratchpad: `addition -> 23.0`

### Step 13 – `observe`
- Action: Logs `"division -> 1.09"` to the scratchpad.
- Expression: `25.0 / 23.0`
- Scratchpad: `division -> 1.09`

### Step 14 – `llm_agent`
- Action: Emits the final numeric answer `1.09`.
- Expression: `25.0 / 23.0`
- Scratchpad: `division -> 1.09`

### Step 15 – `observe`
- Action: Detects the final float, sets `status="done"`, and stores `result=1.09`.
- Expression: `1.09`
- Scratchpad: `division -> 1.09`

### Step 16 – `END`
- Action: Graph terminates because the state is `done`.
- Expression: `1.09`
- Scratchpad: `division -> 1.09`

---

## Key Code Highlights

- **Single Tool Call Enforcement**: The line `model.bind_tools(TOOLS, parallel_tool_calls=False)` is a simple but powerful way to force a step-by-step thought process, which is crucial for both correctness and debugging.
- **Stateful Message Management**: The `llm_agent` intelligently reconstructs its message history at each step, providing the `SYSTEM` prompt for guidance, the current `expression` as the immediate task, and the recent `ToolMessage` history as context. This gives the agent memory of its last action.
- **Decoupled Observation**: The `observe` node cleanly separates the "thinking" (LLM) and "acting" (tools) from the "state updating" logic. This makes the graph easier to reason about.
- **Clear Finalization Logic**: The `observe` node's check for a bare float (`FLOAT_RE.match(txt)`) provides a clear and robust signal for when the agent's work is complete, preventing premature termination.
- **Live Streaming and Debugging**: The `pp_update` function demonstrates how to use LangGraph's `stream` method to get a readable, real-time trace of the agent's internal state and decisions, which is invaluable for debugging complex flows.

```
