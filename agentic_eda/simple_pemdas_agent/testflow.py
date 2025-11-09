"""
Math Expression Solver using LangGraph
Evaluates math expressions using BEDMAS order of operations
"""

from __future__ import annotations

import operator
from typing import Annotated, Literal

import helpers.hlogging as hlogging
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel
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

LOGGER = hlogging.getLogger(__name__)
MODEL = ChatOpenAI(model="gpt-4o", temperature=0)

# Define the state
class MathState(TypedDict):
    expression: str
    scratchpad: Annotated[list[str], operator.add]
    status: Literal["ongoing", "done"]
    result: float | None


# Define tool wrappers (these call your actual scripts)
def call_exponentiation(a: float, b: float) -> float:
    """Invoke exponentiation helper.

    :param a: Base operand.
    :param b: Exponent operand.
    :return: Result of `a ** b`.
    """
    return exp_module.run(a, b)


def call_multiplication(a: float, b: float) -> float:
    """Invoke multiplication helper.

    :param a: Left operand.
    :param b: Right operand.
    :return: Result of `a * b`.
    """
    return mult_module.run(a, b)


def call_division(a: float, b: float) -> float:
    """Invoke division helper.

    :param a: Numerator operand.
    :param b: Denominator operand.
    :return: Result of `a / b`.
    """
    return div_module.run(a, b)


def call_addition(a: float, b: float) -> float:
    """Invoke addition helper.

    :param a: Left operand.
    :param b: Right operand.
    :return: Result of `a + b`.
    """
    return add_module.run(a, b)


def call_subtraction(a: float, b: float) -> float:
    """Invoke subtraction helper.

    :param a: Left operand.
    :param b: Right operand.
    :return: Result of `a - b`.
    """
    return sub_module.run(a, b)


# Map tool names to functions
TOOLS = {
    "exponentiation": call_exponentiation,
    "multiplication": call_multiplication,
    "division": call_division,
    "addition": call_addition,
    "subtraction": call_subtraction,
}


# Define the LLM node
class MathOperation(BaseModel):
    tool_name: str
    a: float
    b: float
    simplified: str
    status: str
    # tool_return: float

def llm_agent(state: MathState) -> MathState:
    """Plan and execute the next BEDMAS operation.

    :param state: Current math state.
    :return: Updated state delta for LangGraph.
    """

    system_prompt = """You are a math expression solver that follows BEDMAS order of operations.
    
Available tools:
- exponentiation(a, b): computes a^b
- multiplication(a, b): computes a*b
- division(a, b): computes a/b
- addition(a, b): computes a+b
- subtraction(a, b): computes a-b

Given the expression and scratchpad, determine the NEXT SINGLE operation to perform following BEDMAS.
If the expression is fully solved, return the final result in place of the new expression, and set status to 'done'. Otherwise, keep status
as 'ongoing'.
"""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Expression: {state['expression']}\nScratchpad: {state['scratchpad']}")
    ]
    
    # Check if we should return final result or next operation
    # You could add logic here to determine which schema to use
    # For simplicity, let's try to get MathOperation first

    structured_model = MODEL.with_structured_output(MathOperation)
    response = structured_model.invoke(messages)
    
    # Execute the tool
    tool_result = TOOLS[response.tool_name](response.a, response.b)
    LOGGER.info(
        "tool=%s a=%s b=%s result=%s new_expression=%s status=%s",
        response.tool_name,
        response.a,
        response.b,
        tool_result,
        response.simplified,
        response.status,
    )
    
    return {
        "expression": response.simplified,
        "scratchpad": [f"Performed {response.tool_name}({response.a}, {response.b}) = {tool_result}"],
        "status": response.status,
        "result": float(response.simplified) if response.status == "done" else None
    }

# Define routing logic
def should_continue(state: MathState) -> Literal["llm_agent", END]:
    """Route execution based on the state's status flag.

    :param state: Current math state.
    :return: `END` if solved, otherwise the `llm_agent` node name.
    """
    if state["status"] == "done":
        # print(state["expression"])
        state["result"] = float(state["expression"])
        # print(state['result'])
        return END
    return "llm_agent"


# Build the graph
builder = StateGraph(MathState)

# Add nodes
builder.add_node("llm_agent", llm_agent)

# Add edges
builder.add_edge(START, "llm_agent")
builder.add_conditional_edges(
    "llm_agent",
    should_continue,
    ["llm_agent", END]
)

# Compile
graph = builder.compile()


# Example usage
if __name__ == "__main__":
    expression = "(5^2) + (3-4) * (6 * 2) / (3 + 20)"
    state = {
        "expression": expression,
        "scratchpad": [],
        "status": "ongoing",
        "result": None
    }
    # while state["status"] != "done":
    state = graph.invoke(state)
    LOGGER.info("Final result: %s", state["result"])


# print(call_exponentiation(2, 3))
# print(call_division(2, 3))
# print(call_multiplication(2, 3))
# print(call_addition(2, 3))
# print(call_subtraction(2,3))
