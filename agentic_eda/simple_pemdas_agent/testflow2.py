# math_graph.py
"""
LangGraph agent that solves expressions with BEDMAS, one tool per step.
Keeps your original state keys: expression, scratchpad, status, result.

pip install -U langgraph langchain langchain-openai pydantic
export OPENAI_API_KEY=...
"""

from __future__ import annotations

import operator
from typing import Annotated, Literal, Sequence

import helpers.hlogging as hlogging
from typing_extensions import TypedDict

try:
    import agentic_eda.simple_pemdas_agent.add as add_module
except ModuleNotFoundError:  # pragma: no cover - script fallback when run in-place
    import add as add_module  # type: ignore

try:
    import agentic_eda.simple_pemdas_agent.sub as sub_module
except ModuleNotFoundError:  # pragma: no cover - script fallback when run in-place
    import sub as sub_module  # type: ignore

try:
    import agentic_eda.simple_pemdas_agent.mult as mult_module
except ModuleNotFoundError:  # pragma: no cover - script fallback when run in-place
    import mult as mult_module  # type: ignore

try:
    import agentic_eda.simple_pemdas_agent.div as div_module
except ModuleNotFoundError:  # pragma: no cover - script fallback when run in-place
    import div as div_module  # type: ignore

try:
    import agentic_eda.simple_pemdas_agent.exp as exp_module
except ModuleNotFoundError:  # pragma: no cover - script fallback when run in-place
    import exp as exp_module  # type: ignore

# LangChain / LangGraph
from pydantic import BaseModel, Field
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

import re

LOGGER = hlogging.getLogger(__name__)


# -------------------------------
# State (original + internal messages)
# -------------------------------
class MathState(TypedDict):
    expression: str
    scratchpad: Annotated[list[str], operator.add]
    status: Literal["ongoing", "done"]
    result: float | None
    # internal messages for ToolNode; does not change your external API
    messages: Annotated[Sequence, add_messages]


# -------------------------------
# Wrap your scripts as Tools
# -------------------------------
@tool
def exponentiation(a: float, b: float) -> float:
    """Compute a^b via the helper module.

    :param a: Base operand.
    :param b: Exponent operand.
    :return: Result of the exponentiation.
    """
    LOGGER.info("[proof] exp tool being called a=%s b=%s", a, b)
    return float(exp_module.run(a, b))

@tool
def multiplication(a: float, b: float) -> float:
    """Compute a*b via the helper module.

    :param a: Left operand.
    :param b: Right operand.
    :return: Product of the operands.
    """
    LOGGER.info("[proof] mult tool being called a=%s b=%s", a, b)
    return float(mult_module.run(a, b))

@tool
def division(a: float, b: float) -> float:
    """Compute a/b via the helper module.

    :param a: Numerator operand.
    :param b: Denominator operand.
    :return: Quotient of the operands.
    """
    LOGGER.info("[proof] div tool being called a=%s b=%s", a, b)
    return float(div_module.run(a, b))

@tool
def addition(a: float, b: float) -> float:
    """Compute a+b via the helper module.

    :param a: Left operand.
    :param b: Right operand.
    :return: Sum of the operands.
    """
    LOGGER.info("[proof] add tool being called a=%s b=%s", a, b)
    return float(add_module.run(a, b))

@tool
def subtraction(a: float, b: float) -> float:
    """Compute a-b via the helper module.

    :param a: Left operand.
    :param b: Right operand.
    :return: Difference of the operands.
    """
    LOGGER.info("[proof] sub tool being called a=%s b=%s", a, b)
    return float(sub_module.run(a, b))

TOOLS = [exponentiation, multiplication, division, addition, subtraction]


# -------------------------------
# Model bound to tools (one per turn)
# -------------------------------
# parallel_tool_calls=False ensures exactly one tool call each loop
model = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(
    TOOLS, parallel_tool_calls=False
)  # Docs: bind_tools + disabling parallel tool calls. :contentReference[oaicite:0]{index=0}


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


# -------------------------------
# Nodes
# -------------------------------
def llm_agent(state: MathState):
    """Build the message stack and invoke the tool-bound LLM.

    :param state: Current math state tracked by LangGraph.
    :return: Partial state containing the latest AI message.
    """
    msgs = list(state.get("messages", []))
    if not msgs:
        msgs = [SYSTEM, HumanMessage(content=state["expression"])]
    else:
        # Filter out old HumanMessage
        current_msgs = [m for m in msgs if not isinstance(m, (SystemMessage, HumanMessage))]
        # Add current expression as HumanMessage
        msgs = [SYSTEM, HumanMessage(content=state["expression"]), *current_msgs]
    # print(f"ai = model.invoke({msgs[1:]})")
    ai = model.invoke(msgs)
    return {"messages": [ai]}



tools_node = ToolNode(TOOLS)  # Executes tool calls and adds ToolMessage with results. :contentReference[oaicite:1]{index=1}


FLOAT_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d+)?|\.\d+)$")

def _has_paren(expr: str) -> bool:
    """Return True when the expression contains parentheses."""
    return "(" in expr and ")" in expr

def _innermost_hint(expr: str) -> str:
    """Provide guidance that nudges the LLM toward the innermost parentheses."""
    return ("Focus on the innermost (...) group first. "
            "Pick a binary op inside that group and call the matching tool.")

def observe(state: MathState):
    """Inspect the latest message and decide how to update MathState.

    :param state: Current math state.
    :return: Dict of field updates (expression, result, scratchpad, status).
    """
    updates: dict = {}

    last = state["messages"][-1]
    # print(f"state: {state}")
    # print(f"last: {last}")

    # (A) Finalization path: AI replied with a bare float (no further tool call)
    if isinstance(last, AIMessage) and not getattr(last, "tool_calls", None):
        txt = str(last.content).strip()
        # Accept only a numeric terminal; otherwise force a tool call.
        if FLOAT_RE.match(txt):
            updates["status"] = "done"
            updates["result"] = float(txt)
            updates["expression"] = txt
            return updates
        # It's a new expression, update it
        updates["expression"] = txt
        return updates
        

    # (B) Tool just ran; log to scratchpad
    if isinstance(last, ToolMessage):
        tool_name = getattr(last, "name", "tool")
        try:
            out = float(str(last.content))
        except Exception:
            out = str(last.content)
        updates["scratchpad"] = [f"{tool_name} -> {out}"]
        # The LLM is expected to send a follow-up AI message giving the next expression,
        # so we don't set expression here. We'll wait for the next llm_agent step.
        return updates

    return updates


# -------------------------------
# Routing
# -------------------------------
def has_tool_call(state: MathState) -> bool:
    """Return True when the latest AI message requests a tool invocation."""
    last = state["messages"][-1]
    return isinstance(last, AIMessage) and bool(getattr(last, "tool_calls", None))

def from_llm(state: MathState):
    """Route either to the tool executor or to observe based on the AI output."""
    # If AI wants a tool, run tools; else observe (maybe final)
    return "tools" if has_tool_call(state) else "observe"

def next_step(state: MathState):
    """Return the next node identifier given the state's status flag."""
    # If done, stop; else loop back to llm
    return END if state["status"] == "done" else "llm_agent"


# -------------------------------
# Build & compile graph
# -------------------------------
def build_graph():
    """Construct and compile the LangGraph state machine."""
    g = StateGraph(MathState)
    g.add_node("llm_agent", llm_agent)
    g.add_node("tools", tools_node)
    g.add_node("observe", observe)

    g.add_edge(START, "llm_agent")
    g.add_conditional_edges("llm_agent", from_llm, {"tools": "tools", "observe": "observe"})  # conditional edges. :contentReference[oaicite:2]{index=2}
    g.add_edge("tools", "observe")
    g.add_conditional_edges("observe", next_step, {"llm_agent": "llm_agent", END: END})
    return g.compile()

graph = build_graph()


# --- pretty streaming ---------------------------------------------------------
from typing import Any, Dict
from langchain_core.messages import AIMessage, ToolMessage

def pp_update(update: Dict[str, Any]) -> str:
    """Turn a stream(update) chunk into a concise one-liner.

    :param update: Streaming payload from `graph.stream`.
    :return: Readable line summarizing the change.
    """
    # Each chunk is {"node_name": <node_update_dict>}
    (node_name, payload), = update.items()

    # llm_agent: show planned tool or final text
    if node_name == "llm_agent":
        msgs = payload.get("messages", [])
        if not msgs:
            return "[llm] (no message)"
        ai = msgs[-1]
        if isinstance(ai, AIMessage) and getattr(ai, "tool_calls", None):
            tc = ai.tool_calls[0]
            name = tc.get("name")
            args = tc.get("args", {})
            return f"[llm] plan → {name}({', '.join(f'{k}={v}' for k,v in args.items())})"
        # no tool call → model replied with text (expression or final)
        txt = str(getattr(ai, "content", "")).strip()
        return f"[llm] text → {txt}"

    # tools: show executed tool + return
    if node_name == "tools":
        msgs = payload.get("messages", [])
        if not msgs:
            return "[tool] (no message)"
        tm = msgs[-1]
        if isinstance(tm, ToolMessage):
            val = str(tm.content).strip()
            return f"[tool] {getattr(tm, 'name', 'tool')} ⇒ {val}"
        return "[tool] (unknown tool message)"

    # observe: show state deltas we care about
    if node_name == "observe":
        bits = []
        if "expression" in payload:
            bits.append(f"expr={payload['expression']}")
        if "scratchpad" in payload:
            # only newest scratch entry
            bits.append(f"note={payload['scratchpad'][-1] if payload['scratchpad'] else ''}")
        if payload.get("status") == "done":
            bits.append(f"done result={payload.get('result')}")
        return "[obs] " + ", ".join(bits) if bits else "[obs] (no-op)"

    # fallback
    return f"[{node_name}] {payload}"



# -------------------------------
# CLI / in-script test
# -------------------------------
if __name__ == "__main__":
    import os
    os.environ.setdefault("OPENAI_API_KEY", "<your key>")

    expr = "(5^2) + (3-4) * (6 * 2) / (3 + 20)"
    # expr = "(5^2) / (3 + 20)"
    init: MathState = {
        "expression": expr,
        "scratchpad": [],
        "status": "ongoing",
        "result": None,
        "messages": [],   # internal; we’ll seed it inside llm_agent
    }

    LOGGER.info("Running expression: %s", expr)

    config = {"recursion_limit": 100}

    # (1) See which functions ran (live):
    #     stream_mode="updates" yields an event after each node (AI tool_call, Tool execution, AI reply)
    for update in graph.stream(init, stream_mode="updates", config=config):  # streaming how-to. :contentReference[oaicite:3]{index=3}
        # print("UPDATE:", update)
        LOGGER.info(pp_update(update))

    # # (2) Final state:
    # final = graph.invoke(init, config=config)
    # print("FINAL:", final["result"])
