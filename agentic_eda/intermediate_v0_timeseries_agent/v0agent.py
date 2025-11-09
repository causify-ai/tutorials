from __future__ import annotations

import argparse
import json
import operator
import pathlib
import subprocess
from typing import Annotated, Any, Literal

import helpers.hlogging as hlogging
import helpers.hmarkdown_formatting as hmarkdown_formatting
import langchain_core.messages as lc_messages
import langchain_openai
import nbformat
import nbformat.v4 as nbformat_v4
import pydantic
import typing_extensions

from langgraph.graph import StateGraph, START, END

try:
    import agentic_eda.intermediate_v0_timeseries_agent.calculate_mean as calculate_mean_module
except ModuleNotFoundError:  # pragma: no cover - fallback when run inside agentic_eda
    import calculate_mean as calculate_mean_module  # type: ignore

LOGGER = hlogging.getLogger(__name__)
TOOL_ERROR_TEMPLATE = "Command %s failed with exit code %s"
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
MAX_STEPS = 10


class AgentState(typing_extensions.TypedDict):
    csv_path: str
    question: str
    datetime_column: str
    numeric_columns: list[str]
    insights: Annotated[list[dict[str, Any]], operator.add]
    notebook_cells: Annotated[list[dict[str, Any]], operator.add]
    final_report: str | None
    status: Literal["ongoing", "done"]
    step_count: int
    trace: Annotated[list[dict[str, Any]], operator.add]
    thought_log: Annotated[list[str], operator.add]


class AgentDecision(pydantic.BaseModel):
    action: Literal["tool", "final_report"]
    tool_name: Literal[
        "calculate_mean",
        "calculate_median",
        "detect_seasonality",
        "detect_trends",
    ] | None = None
    column: str | None = None
    visualize: list[int] = []
    reasoning: str

    @pydantic.model_validator(mode="after")
    def _validate_action(self) -> "AgentDecision":
        if self.action == "tool" and not self.tool_name:
            raise ValueError("tool_name is required when action is 'tool'.")
        if self.action == "final_report" and self.tool_name is not None:
            raise ValueError("tool_name must be omitted when action is 'final_report'.")
        return self


TOOL_SPECS = {
    "calculate_mean": {
        "script": "calculate_mean.py",
        "requires_column": True,
        "summary_key": "mean",
        "description": "Calculate the mean of a numeric column.",
    },
    "calculate_median": {
        "script": "calculate_median.py",
        "requires_column": True,
        "summary_key": "median",
        "description": "Calculate the median of a numeric column.",
    },
    "detect_seasonality": {
        "script": "detect_seasonality.py",
        "requires_column": True,
        "description": "Detect seasonality for a numeric series.",
    },
    "detect_trends": {
        "script": "detect_trends.py",
        "requires_column": False,
        "description": "Detect trends across numeric columns.",
    },
}


def _invoke_subprocess(command: list[str]) -> str:
    """
    Execute a subprocess command and return its stdout, encoding failures as JSON.

    :param command: command arguments to execute.
    :return: stdout content or a JSON payload describing the error.
    """
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        return result.stdout.strip()

    error_message = result.stderr.strip() or result.stdout.strip()
    if not error_message:
        error_message = TOOL_ERROR_TEMPLATE % (" ".join(command), result.returncode)
    LOGGER.error(TOOL_ERROR_TEMPLATE, " ".join(command), result.returncode)
    payload = {
        "error": error_message,
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }
    return json.dumps(payload)


def _prepare_messages(state: AgentState) -> list[lc_messages.BaseMessage]:
    """
    Build the message stack describing the current agent context.

    :param state: current agent state.
    :return: list of LangChain messages.
    """
    tool_descriptions = "\n".join(
        f"- {name}: {spec['description']}" for name, spec in TOOL_SPECS.items()
    )
    insights = state.get("insights", [])
    if insights:
        insight_lines = "\n".join(
            f"{insight['insight_id']}: {insight['text']}" for insight in insights[-5:]
        )
        inventory = f"Current insight inventory:\n{insight_lines}"
    else:
        inventory = "No insights collected yet."

    numeric_columns = ", ".join(state["numeric_columns"])

    prompt = (
        "You are a timeseries analyst. Each step you must produce a structured decision.\n"
        "Available actions:\n"
        "1. action='tool' to run one of the supported tools. Provide tool_name and, if needed, column.\n"
        "2. action='final_report' when you are ready to conclude. Provide a comprehensive report in reasoning, "
        "and list insight IDs to visualise in visualize.\n"
        "Supported tools:\n"
        f"{tool_descriptions}\n"
        "If you choose a tool requiring a column, select one exactly from the numeric columns list provided "
        "in the human message. Do not invent column names.\n"
        "Consult the insight inventory to avoid repeating the same tool-column combination. Each plan must move the "
        "analysis forward. Use summary statistics on a representative subset of columns rather than exhaustively "
        "iterating over every sensor.\n"
        f"Wrap up with action='final_report' as soon as you have enough evidence and always finish within {MAX_STEPS} steps.\n"
        "Always explain your reasoning field briefly."
    )
    context = (
        f"Step: {state['step_count']}\n"
        f"Dataset: {state['csv_path']}\n"
        f"Datetime column: {state['datetime_column']}\n"
        f"Numeric columns: {numeric_columns}\n"
        f"Maximum steps allowed: {MAX_STEPS}\n"
        f"User question: {state['question']}\n"
        f"{inventory}"
    )
    return [
        lc_messages.SystemMessage(content=prompt),
        lc_messages.HumanMessage(content=context),
    ]


def _run_tool(tool_name: str, state: AgentState, column: str | None) -> tuple[str, dict[str, Any]]:
    """
    Execute a helper tool script based on the requested tool name.

    :param tool_name: tool identifier requested by the LLM.
    :param state: current agent state.
    :param column: optional column parameter.
    :return: tuple of stdout text and parsed payload.
    """
    spec = TOOL_SPECS[tool_name]
    if spec["requires_column"] and not column:
        raise ValueError(f"Tool '{tool_name}' requires a column but none was provided.")

    script_path = SCRIPT_DIR / spec["script"]
    command = ["python", str(script_path), "--path", state["csv_path"]]
    if spec["requires_column"] and column:
        command.extend(["--column", column])
    if tool_name in {"detect_seasonality", "detect_trends"}:
        command.extend(["--datetime_column", state["datetime_column"]])

    raw_output = _invoke_subprocess(command)
    try:
        payload = json.loads(raw_output)
    except json.JSONDecodeError:
        payload = {"raw_output": raw_output}
    return raw_output, payload


def visual_cells_for_insight(
    insight: dict[str, Any],
    csv_path: str,
    datetime_column: str,
) -> list[nbformat.NotebookNode]:
    """
    Generate notebook cells for a given insight when visualisation is requested.

    :param insight: insight metadata captured during the run.
    :param csv_path: path to the dataset.
    :param datetime_column: name of the datetime column.
    :return: notebook cells implementing the requested visualisations.
    """
    tool_name = insight.get("tool")
    payload = insight.get("payload", {})
    insight_id = insight.get("insight_id")
    if tool_name != "detect_trends":
        return []

    code = f"""
import pandas as pd
import plotly.express as px
df = pd.read_csv('{csv_path}', parse_dates=['{datetime_column}'], skiprows=[1]).sort_values('{datetime_column}')
trend_data = {json.dumps(payload)}
increasing = [column for column, label in trend_data.items() if label == 'increasing']
decreasing = [column for column, label in trend_data.items() if label == 'decreasing']
if increasing:
    fig = px.line(df, x='{datetime_column}', y=increasing, title='Increasing Trends', labels={{'value': 'Value', '{datetime_column}': 'Date'}})
    fig.show()
if decreasing:
    fig = px.line(df, x='{datetime_column}', y=decreasing, title='Decreasing Trends', color_discrete_map={{column: 'red' for column in decreasing}})
    fig.show()
"""
    return [
        nbformat_v4.new_markdown_cell(f"#### Visualization for Insight {insight_id}"),
        nbformat_v4.new_code_cell(code),
    ]


BASE_MODEL = langchain_openai.ChatOpenAI(model="gpt-4o", temperature=0)
STRUCTURED_MODEL = BASE_MODEL.with_structured_output(AgentDecision)


def llm_agent(state: AgentState) -> dict[str, Any]:
    """
    Select the next action using the structured-output paradigm and execute it if needed.

    :param state: current agent state.
    :return: state updates after performing the selected action.
    """
    decision = STRUCTURED_MODEL.invoke(_prepare_messages(state))
    updates: dict[str, Any] = {"step_count": state["step_count"] + 1}
    updates.setdefault("thought_log", []).append(decision.reasoning)

    if decision.action == "final_report":
        report_text = hmarkdown_formatting.md_clean_up(decision.reasoning.strip())
        updates["final_report"] = report_text
        updates["status"] = "done"
        updates.setdefault("notebook_cells", []).append(
            nbformat_v4.new_markdown_cell(f"### Final Report\n{report_text}")
        )

        visualize_cells: list[nbformat.NotebookNode] = []
        for insight_id in decision.visualize:
            insight = next((item for item in state["insights"] if item["insight_id"] == insight_id), None)
            if insight:
                visualize_cells.extend(
                    visual_cells_for_insight(insight, state["csv_path"], state["datetime_column"])
                )
        if visualize_cells:
            updates.setdefault("notebook_cells", []).extend(visualize_cells)

        trace_entry = {
            "step": updates["step_count"],
            "event": "llm_final",
            "reasoning": decision.reasoning,
            "visualize": decision.visualize,
        }
        updates.setdefault("trace", []).append(trace_entry)
        LOGGER.info("Final report drafted with %s visualization(s).", len(decision.visualize))
        return updates

    tool_name = decision.tool_name
    raw_output, payload = _run_tool(tool_name, state, decision.column)

    insight_id = len(state.get("insights", [])) + 1
    summary = f"Tool `{tool_name}` output: {raw_output}"
    insight = {
        "insight_id": insight_id,
        "tool": tool_name,
        "payload": payload,
        "text": summary,
        "column": decision.column,
    }
    updates.setdefault("insights", []).append(insight)
    updates.setdefault("notebook_cells", []).append(
        nbformat_v4.new_markdown_cell(f"### Tool: `{tool_name}`\n{summary}")
    )
    trace_entry = {
        "step": updates["step_count"],
        "event": "tool_result",
        "tool": tool_name,
        "column": decision.column,
        "reasoning": decision.reasoning,
        "payload": payload,
    }
    updates.setdefault("trace", []).append(trace_entry)
    LOGGER.info("Executed %s with column=%s", tool_name, decision.column)
    return updates


def should_continue(state: AgentState) -> str | object:
    """
    Decide whether to continue the agent loop based on status and step budget.

    :param state: current agent state.
    :return: next node name or END sentinel.
    """
    if state.get("status") == "done":
        return END
    if state.get("step_count", 0) >= MAX_STEPS:
        LOGGER.warning("Maximum step count reached without final report.")
        return END
    return "llm_agent"


def run_agent(csv_path: pathlib.Path, question: str, output_notebook: pathlib.Path, trace_path: pathlib.Path) -> None:
    """
    Run the EDA agent and persist both the notebook and execution trace.

    :param csv_path: dataset to inspect.
    :param question: question to ask the agent.
    :param output_notebook: path where the notebook will be written.
    :param trace_path: path where the trace will be written.
    """
    calculate_mean_module.configure_logging()
    dataframe = calculate_mean_module.read_dataframe(csv_path)
    datetime_column = dataframe.columns[0]
    numeric_columns = dataframe.select_dtypes(include="number").columns.tolist()

    initial_state: AgentState = {
        "csv_path": str(csv_path),
        "question": question,
        "datetime_column": datetime_column,
        "numeric_columns": numeric_columns,
        "insights": [],
        "notebook_cells": [],
        "final_report": None,
        "status": "ongoing",
        "step_count": 0,
        "trace": [],
        "thought_log": [],
    }

    graph = StateGraph(AgentState)
    graph.add_node("llm_agent", llm_agent)
    graph.add_edge(START, "llm_agent")
    graph.add_conditional_edges("llm_agent", should_continue, {"llm_agent": "llm_agent", END: END})

    final_state = graph.compile().invoke(initial_state)

    output_notebook.parent.mkdir(parents=True, exist_ok=True)
    trace_path.parent.mkdir(parents=True, exist_ok=True)

    nbformat.write(nbformat_v4.new_notebook(cells=final_state["notebook_cells"]), output_notebook)
    trace_path.write_text("\n".join(json.dumps(entry) for entry in final_state["trace"]))

    final_report = final_state.get("final_report")
    if final_report:
        headline = final_report.splitlines()[0] if final_report else ""
        LOGGER.info("Analysis complete. Final report headline: %s", headline)
    else:
        LOGGER.info("Analysis complete. No final report was produced.")
    LOGGER.info("Notebook written to %s", output_notebook)
    LOGGER.info("Trace written to %s", trace_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a mini-timeseries analysis agent.")
    parser.add_argument("--path", required=True, help="Absolute path to the timeseries CSV file.")
    parser.add_argument("--question", default="Analyze this timeseries data.", help="The question to ask the agent.")
    parser.add_argument("--output", required=True, help="Path to save the output Jupyter notebook.")
    parser.add_argument("--trace", required=True, help="Path to save the execution trace.")
    arguments = parser.parse_args()
    run_agent(pathlib.Path(arguments.path), arguments.question, pathlib.Path(arguments.output), pathlib.Path(arguments.trace))
