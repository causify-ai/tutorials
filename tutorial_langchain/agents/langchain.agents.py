# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # LangChain Agents, Local LLMs (Ollama: Qwen, Gemma)
#
# Concise, agent-focused notebook. Uses **LangChain** with **Ollama** (Qwen, Gemma) locally.
#
# **Some of the items in this tutorial:**
# - Run local chat models via Ollama.
# - Define tools and build **ReAct** agents.
# - Control iterations, handle parsing errors, and debug.
# - EDA agent with tools
#

# %% [markdown] jp-MarkdownHeadingCollapsed=true
# ## Table of Contents
# 1. [Prerequisites](#prereqs)
# 2. [Verify Ollama & Pull Models](#verify)
# 3. [Initialize LLMs & Embeddings](#init)
# 4. [Define Tools](#tools)
# 5. [Minimal ReAct Agent](#minimal)
# 6. [Multi-Tool Agent](#multi)
# 7. [EDA Agent](#eda)
#

# %% [markdown] jp-MarkdownHeadingCollapsed=true tags=["prereqs"]
# ## 1) Prerequisites <a id='prereqs'></a>
#
# Install Python packages (uncomment to run if needed):
#
# ```bash
# # !pip install -U langchain langchain-community langchain-ollama faiss-cpu tiktoken
# # !pip install -U langchain-text-splitters pydantic requests
# ```
#
# Install **Ollama** from https://ollama.com/download and ensure the service is running.

# %%
# !pip install -U langchain langchain-community langchain-ollama faiss-cpu tiktoken
# !pip install -U langchain-text-splitters pydantic requests

# %% [markdown] tags=["verify"]
# ## 2) Verify Ollama, Pull Models & Imports <a id='verify'></a>
#
# The following cell checks whether Ollama is responding locally and lists installed models.
# If models are missing, pull them (uncomment the `ollama pull` commands).

# %%
# Imports
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Union
from urllib.request import urlopen

import pandas as pd
import numpy as np
from langchain.agents import AgentExecutor, create_react_agent
from langchain.agents.format_scratchpad import format_log_to_messages
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.tools import tool

from typing import List, TypedDict
from langchain_ollama import ChatOllama
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import BaseTool
import matplotlib.pyplot as plt

# %% id="check_ollama"
try:
    with urlopen('http://host.docker.internal:11434/api/tags', timeout=2) as r:
        data = json.loads(r.read().decode('utf-8'))
    print('Ollama is running. Installed models:')
    for m in data.get('models', []):
        print(' -', m.get('name'))
except Exception as e:
    print('Ollama not reachable on http://127.0.0.1:11434. Start it with `ollama serve`.', file=sys.stderr)
    print('Error:', e, file=sys.stderr)

print('\nTo pull models (uncomment as needed):')
print('  # !ollama pull qwen2:7b')
print('  # !ollama pull gemma2:9b')
print('  # !ollama pull nomic-embed-text  # embeddings')


# %% [markdown] tags=["init"]
# ## 3) Initialize LLMs & Embeddings <a id='init'></a>
#
# We use **ChatOllama** for Qwen2/Gemma2 and **OllamaEmbeddings** for local embeddings.

# %%
# Choose one main chat model
llm = ChatOllama(model='qwen3:latest', temperature=0, num_ctx=8192, request_timeout=180)
# Alternative:
# llm = ChatOllama(model='gemma2:9b', temperature=0, num_ctx=8192, request_timeout=180)

# Local embeddings via Ollama (pull the model first)
embeddings = OllamaEmbeddings(model='nomic-embed-text')

print('LLM and embeddings initialized.')


# %% [markdown] tags=["tools"]
# ## 4) Define Tools <a id='tools'></a>
#
# Tools should be **small, typed, deterministic** with clear docstrings. We also include a file reader and a simple summarizer.

# %%
@tool
def calc(expression: str) -> str:
    """Evaluate a simple Python arithmetic expression like '37*42'."""
    try:
        return str(eval(expression, {"__builtins__": {}}))
    except Exception as e:
        return f"error: {e}"

@tool
def now() -> str:
    """Return current local datetime ISO string."""
    return datetime.now().isoformat(timespec='seconds')

@tool
def read_file(path: str) -> str:
    """Read a small UTF-8 text file from disk."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

@tool
def summarize(text: str) -> str:
    """Summarize a short passage (naive)."""
    return (f"Summary: {text[:200]}..." if len(text) > 220 else f"Summary: {text}")

tools_basic = [calc, now, read_file, summarize]
print('Tools defined:', [t.name for t in tools_basic])


# %% [markdown] tags=["minimal"]
# ## 5) Minimal ReAct Agent <a id='minimal'></a>
#
# A single-tool agent that uses `calc`. We use `create_react_agent` and `AgentExecutor`. Always bound iterations and enable parsing error handling.

# %%
# 1) LLM points to your working Ollama endpoint
llm = ChatOllama(
    model="gemma3",                            # must match your installed model name
    base_url="http://host.docker.internal:11434",
    temperature=0,
    timeout=60,
)

# 2) Simple calc tool
@tool
def calc(expression: str) -> str:
    """Compute a Python arithmetic expression like '37*42+5'."""
    return str(eval(expression))

tools = [calc]

# 3) ReAct prompt (keep agent_scratchpad as a STRING slot to avoid BaseMessage type errors)
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a calculator assistant. Use tools to compute.\n\n"
     "You have access to the following tools:\n{tools}\n\n"
     "When you need to call a tool, use EXACTLY this format:\n"
     "Action: one of [{tool_names}]\n"
     "Action Input: <JSON or plain text>\n\n"
     "When done, reply with:\n"
     "Final Answer: <answer>"),
    ("human", "{input}\n\n{agent_scratchpad}")
])

# 4) Build agent + executor
agent = create_react_agent(llm, tools, prompt=prompt)
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=6,
)

# 5) Run
res = executor.invoke({"input": "Compute (37*42)+5 using the tool."})  # do NOT pass agent_scratchpad explicitly
print(res["output"])

# %% [markdown] tags=["multi"]
# ## 6) Multi-Tool Agent <a id='multi'></a>
#
# Expose additional tools (`read_file`, `summarize`, `now`) and let ReAct orchestrate them. Keep prompts explicit and concise.

# %%
# demo_file_creator.py
# This script creates a demo.txt file with some sample content.

content = """\
This is the first line of the demo file.
It is meant for testing the LangChain ReAct agent.
Here is the third line, which should also be summarized.
Fourth line: more filler text for the demo.
Fifth line: final sample content.
"""

with open("demo.txt", "w", encoding="utf-8") as f:
    f.write(content)

print("demo.txt created with sample content:")
print(content)


# %%
# -------- LLM --------
llm = ChatOllama(
    model="gemma3",
    base_url="http://host.docker.internal:11434",
    temperature=0,
)

# -------- Tools --------

@tool
def head_file(args: dict = None) -> str:
    """Return the first N lines of a UTF-8 text file.
    Expects args like {"path": "./demo.txt", "n": 3}. Defaults shown if missing.
    """
    args = args or {}
    path = Path(args.get("path", "./demo.txt"))
    n = int(args.get("n", 3))
    if not path.exists():
        return f"ERROR: file not found: {path}"
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    return f"FILE: {path}\nLINES:\n" + "\n".join(lines[:n])

@tool
def now_time(args: dict = None) -> str:
    """Return current local time in ISO8601 (seconds). Ignores args."""
    return datetime.now().isoformat(timespec="seconds")

# Register for your agent
tools_basic = [head_file, now_time]

# -------- Prompt --------
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You can use tools. Prefer minimal steps.\n"
     "Tools available:\n{tools}\n\n"
     "TOOL CALL FORMAT (strict):\n"
     "Action: one of [{tool_names}]\n"
     "Action Input: <JSON or plain text>\n\n"
     "RULES:\n"
     "- Emit EXACTLY ONE tool call per step.\n"
     "- For reading first lines, call: Action: head_file  |  Action Input: {{\"path\": \"./demo.txt\", \"n\": 3}}\n"
     "- For current time, call:       Action: now_time   |  Action Input: \"\"\n"
     "- Final output must be a SINGLE line starting with:\n"
     "Final Answer: <answer>\n"),
    ("human", "{input}\n\n{agent_scratchpad}"),
])

# -------- Output parser --------
class PreferFinishParser:
    _pair_re = re.compile(
        r"Action:\s*(?P<tool>[^\n|]+?)\s*(?:\|\s*)?Action Input:\s*(?P<input>.*?)(?=\nAction:|\Z)",
        flags=re.S
    )
    def __call__(self, text: str) -> Union[AgentAction, AgentFinish]:
        if "Final Answer:" in text:
            final = text.split("Final Answer:", 1)[1].strip()
            return AgentFinish(return_values={"output": final}, log=text)
        pairs = list(self._pair_re.finditer(text))
        if not pairs:
            raise ValueError(f"Could not parse action from:\n{text}")
        first = pairs[0].groupdict()
        tool = first["tool"].strip()
        raw_inp = first["input"].strip()
        if raw_inp in ('""', "''", ""):
            parsed = {}
        else:
            try:
                parsed = json.loads(raw_inp)
            except Exception:
                parsed = raw_inp
        if tool == "head_file" and not isinstance(parsed, dict):
            parsed = {"path": "./demo.txt", "n": 3}
        return AgentAction(tool=tool, tool_input=parsed, log=text)

output_parser = PreferFinishParser()

# -------- Agent --------
agent = (
    RunnablePassthrough()
    .assign(
        tools=lambda x: "\n".join(f"- {t.name}: {t.description or ''}" for t in tools_basic),
        tool_names=lambda x: ", ".join(t.name for t in tools_basic),
        agent_scratchpad=lambda x: "\n".join(
            m.content for m in format_log_to_messages(x.get("intermediate_steps", []))
        ),
    )
    | prompt
    | llm
    | RunnableLambda(lambda m: output_parser(m.content if hasattr(m, "content") else str(m)))
)

executor = AgentExecutor(
    agent=agent,
    tools=tools_basic,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=4,
    early_stopping_method="generate",
)

# -------- Demo --------
result = executor.invoke({
    "input": "Read ./demo.txt, summarize the first 3 lines (cite the filename), then tell the current time."
})
print(result["output"])


# %% [markdown]
# ## 7) EDA with LangChain Agents <a id='eda'></a>

# %% [markdown]
# ### 7.1) Data

# %%
demo_csv_path = "demo_sales.csv"
demo_df = pd.DataFrame(
    {
        "region": ["Northeast", "Midwest", "South", "West"] * 5,
        "month": list(range(1, 21)),
        "units_sold": np.random.randint(10, 500, size=20),
        "price": np.random.uniform(5.0, 30.0, size=20).round(2),
    }
)
demo_df.to_csv(demo_csv_path, index=False)
demo_df.head()


# %% [markdown]
# ## 7.2) Tools

# %%
@tool
def read_head(path: str, n: int = 5) -> str:
    """
    Preview the top rows of a CSV.

    :param path: path to the CSV file
    :param n: number of rows to show
    :return: table preview
    """
    df = pd.read_csv(path)
    display(df.head(n))
    return "Displayed preview."

@tool
def plot_histogram(path: str, column: str, bins: int = 20) -> str:
    """
    Display a histogram for a numeric column from a CSV.

    :param path: path to the CSV file
    :param column: column to plot
    :param bins: number of bins to use
    :return: confirmation message after rendering
    """
    df = pd.read_csv(path)
    values = pd.to_numeric(df[column], errors="coerce").dropna()
    plt.figure()
    plt.hist(values, bins=bins)
    plt.xlabel(column)
    plt.ylabel("Count")
    plt.title(f"Histogram of {column}")
    plt.tight_layout()
    plt.show()
    return "Displayed histogram."

@tool
def groupby_agg(path: str, by: str, metric: str) -> str:
    """
    Compute the mean of a numeric column grouped by a categorical column.

    :param path: path to the CSV file
    :param by: categorical column to group by
    :param metric: numeric column to aggregate (mean)
    :return: grouped table summary
    """
    df = pd.read_csv(path)
    grouped = df.groupby(by, dropna=False)[metric].mean().reset_index()
    display(grouped)
    return "Displayed grouped means."

EDA_TOOLS = [read_head, plot_histogram, groupby_agg]


# %%
# ---- 1) LLM with tools bound (Qwen local via Ollama) ----
llm = ChatOllama(
    model="qwen3:latest",                       
    base_url="http://host.docker.internal:11434",
    temperature=0,
).bind_tools(EDA_TOOLS)

# ---- 2) Agent "state" type ----
class AgentState(TypedDict):
    messages: List[AnyMessage]

# ---- 3) Assistant node: produce next AI message from conversation ----
def assistant_node(state: AgentState) -> AgentState:
    ai_msg: AIMessage = llm.invoke(state["messages"])
    return {"messages": [ai_msg]}

# ---- 4) Tool node: execute tools requested by the model ----
_tool_map = {t.name: t for t in EDA_TOOLS}    # type: dict[str, BaseTool]

def tools_node(state: AgentState) -> AgentState:
    last: AIMessage = state["messages"][-1]   # the AI that requested tools
    out: list[ToolMessage] = []
    for tc in (last.tool_calls or []):
        name = tc.get("name")
        args = tc.get("args", {}) or {}
        tool = _tool_map.get(name)
        if tool is None:
            result = f"ERROR: unknown tool '{name}'"
        else:
            result = tool.invoke(args)
        out.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
    return {"messages": out}

# ---- 5) assistant -> (if tool_calls) tools -> assistant -> ... else END
def run_app(user_text: str, max_loops: int = 4) -> List[AnyMessage]:
    msgs: List[AnyMessage] = [HumanMessage(content=user_text)]
    for _ in range(max_loops):
        # assistant
        step = assistant_node({"messages": msgs})
        msgs.extend(step["messages"])
        ai: AIMessage = step["messages"][-1]
        if not ai.tool_calls:                  # assistant chose to answer -> END
            break
        # tools
        tstep = tools_node({"messages": [ai]})
        msgs.extend(tstep["messages"])         # feed tool outputs back
    return msgs



# %% [markdown]
# ## 7.3) Demo

# %%
agent = run_app(
    "Read the top 5 rows from './demo_sales.csv', then plot a histogram of 'price'. "
)

for m in agent:
    if isinstance(m, AIMessage) and not m.tool_calls:
        print("\nFINAL ANSWER:\n", m.content)
