# LangChain Agents Tutorial

<!-- toc -->

- [Introduction](#introduction)
- [Agent Concepts](#agent-concepts)
- [Setting Up](#setting-up)
  * [Dependencies](#dependencies)
  * [Keys & Environment](#keys--environment)
- [Tools](#tools)
  * [Defining Tools](#defining-tools)
  * [Good Tool Design](#good-tool-design)
- [Prompting & Policies](#prompting--policies)
- [Build a Minimal Agent](#build-a-minimal-agent)
- [ReAct Multi-Tool Agent](#react-multi-tool-agent)
- [Retrieval-Augmented Agent (FAISS)](#retrievalaugmented-agent-faiss)
- [Function-Calling Models](#functioncalling-models)
- [State & Memory](#state--memory)
- [Evaluation & Tracing](#evaluation--tracing)
- [Safety & Guardrails](#safety--guardrails)
- [Deployment Notes](#deployment-notes)
- [Complete Minimal Template](#complete-minimal-template)

<!-- tocstop -->

## Introduction

Focus: **LangChain agents**, LLM driven controllers that decide which **tools** to call, in what order, to solve a task. In this tutorial there is:

- A minimal single-tool agent.
- A ReAct multi-tool agent.
- A retrieval-augmented agent with FAISS.
- An agent that uses function-calling models.
- Observability, safety, and deployment patterns.

## Agent Concepts

- **Agent policy**: how the LLM chooses actions. Commonly **ReAct** (reasoning + acting).
- **Tools**: callable functions with JSON-serializable inputs/outputs.
- **Agent executor**: runtime loop that feeds observations back to the model.
- **Memory**: state across turns (chat history, task scratchpads).
- **Callbacks/Tracing**: inspect decisions, latencies, and tool I/O.

## Setting Up

### Dependencies

```bash
pip install -U langchain langchain-openai langchain-community faiss-cpu tiktoken
# Some addditional toolkits
pip install -U wikipedia requests
```

### Keys & Environment

```bash
export OPENAI_API_KEY=...
```

```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
```

## Tools

### Defining Tools

Use `@tool` (LangChain Core) to declare inputs/outputs and docstrings:

```python
from langchain_core.tools import tool

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers a and b."""
    return a * b

@tool
def fetch_weather(city: str) -> str:
    """Return current weather description for a city (mock)."""
    return f"Sunny in {city}, 27°C"
```

Third-party tools (examples):

```python
from langchain_community.tools.tavily_search import TavilySearchResults
search = TavilySearchResults(k=3)  # requires TAVILY_API_KEY

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=2))
```

### Good Tool Design

- **Narrow scope**; single responsibility.
- **Clear docstring** → better tool selection.
- **Deterministic I/O**; raise explicit errors.
- **Small, typed inputs**; return concise text/JSON.

## Prompting & Policies

**ReAct** uses a prompt that encourages: *Thought → Action → Observation → … → Final Answer*.

```python
from langchain_core.prompts import ChatPromptTemplate

react_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a precise assistant. Use tools only if needed."),
    ("human", "{input}"),
    ("system", "Follow ReAct: Thought -> Action: tool_name, Action Input: JSON, Observation ...")
])
```

You can also start from LangChain’s built-in ReAct prompt.

## Build a Minimal Agent

Single tool, deterministic:

```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

tools = [multiply]
prompt = ChatPromptTemplate.from_messages([
    ("system", "You can do integer multiplication via the multiply tool only."),
    ("human", "{input}")
])

agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

resp = executor.invoke({"input": "What is 37 * 42?"})
print(resp["output"])
```

**What happens:** the agent chooses `multiply`, calls it, reads the observation, and returns the final answer.

## ReAct Multi-Tool Agent

Add search + Wikipedia + weather; keep ReAct general:

```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

tools = [search, wikipedia, fetch_weather]

react_agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=ChatPromptTemplate.from_messages([
        ("system",
         "You are a research assistant. Use tools when necessary. "
         "Cite sources if derived from search/Wikipedia."),
        ("human", "{input}")
    ])
)

react_exec = AgentExecutor(agent=react_agent, tools=tools, verbose=True, handle_parsing_errors=True)

q = "Compare the climate of Barcelona and Berlin in July. Summarize differences."
out = react_exec.invoke({"input": q})
print(out["output"])
```

Notes:

- `handle_parsing_errors=True` tolerates occasional malformed tool calls.
- Add post-processing (e.g., cite URLs from search results) if needed.

## Retrieval-Augmented Agent (FAISS)

Use a tool that performs vector search and returns relevant snippets.

```python
# 1) Build FAISS index
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.tools import tool

docs = [
    ("doc1.txt", "LangChain agents orchestrate tools via ReAct..."),
    ("doc2.txt", "FAISS provides fast similarity search over embeddings..."),
]
texts = [t for _, t in docs]
splits = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).create_documents(texts)

emb = OpenAIEmbeddings(model="text-embedding-3-large")
vs = FAISS.from_documents(splits, emb)

# 2) Wrap retrieval as a tool
@tool
def vector_search(query: str) -> str:
    """Semantic search over internal knowledge base. Returns top snippets."""
    hits = vs.similarity_search(query, k=4)
    return "\\n\\n".join([f"[{i+1}] {d.page_content}" for i, d in enumerate(hits)])

# 3) Agent that can choose retrieval when helpful
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

tools = [vector_search, search]
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Answer with grounded facts. Prefer vector_search for internal docs; "
     "use web search only for external info. Include brief citations like [1],[2]."),
    ("human", "{input}")
])

rag_agent = create_react_agent(llm, tools, prompt)
rag_exec = AgentExecutor(agent=rag_agent, tools=tools, verbose=True)

out = rag_exec.invoke({"input": "How do FAISS and agents work together in LangChain?"})
print(out["output"])
```

**Pattern:** the agent selects `vector_search` to fetch context, then synthesizes a grounded answer.

## Function-Calling Models

If using function-calling models, prefer LangChain’s tool schema → model decides arguments. This reduces prompt-fragility.

```python
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

class WeatherInput(BaseModel):
    city: str = Field(..., description="City name, e.g. 'Guatemala City'")

def _weather(city: str) -> str:
    return f"Sunny in {city}, 27°C"

weather_fc = StructuredTool.from_function(
    func=_weather,
    name="get_weather",
    description="Get the current weather for a city.",
    args_schema=WeatherInput,
)

fc_tools = [weather_fc]

fc_agent = create_react_agent(
    llm=llm.bind_tools(fc_tools),   # <-- exposes JSON schema to the model
    tools=fc_tools,
    prompt=ChatPromptTemplate.from_template(
        "Use tools when needed. Be concise.\n\nQuestion: {input}"
    ),
)
fc_exec = AgentExecutor(agent=fc_agent, tools=fc_tools, verbose=True)
print(fc_exec.invoke({"input": "What's the weather in Antigua Guatemala right now?"})["output"])
```

## State & Memory

For simple chat memory, include history in the prompt:

```python
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

history = [
    HumanMessage(content="Track our conversation context."),
    AIMessage(content="Acknowledged.")
]

prompt = ChatPromptTemplate.from_messages([
    ("system", "Use tools responsibly. Keep answers terse."),
    *history,
    ("human", "{input}")
])

agent = create_react_agent(llm, [multiply], prompt)
exec_ = AgentExecutor(agent=agent, tools=[multiply], verbose=False)
```

For complex workflows or multi-turn tool plans, consider **LangGraph** (state machine around agents). Keep nodes (tools), edges (control flow), and state (scratchpad/history) explicit.

## Evaluation & Tracing

- **Tracing/Debugging**: enable LangSmith (recommended).

```bash
# pip install -U langsmith
export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_API_KEY=...
export LANGCHAIN_PROJECT="agents-tutorial"
```

- **Eval**:
  - Golden-set tasks → compare outputs (exact/semantic).
  - Tool-use metrics: #steps, failures, latency per tool.
  - Hallucination checks: require citations; verify against retrieved context.

## Safety & Guardrails

- **Input filters**: block dangerous intents before agent loop.
- **Tool allowlist**: expose only safe tools; validate args.
- **Rate limits**: timeouts, max iterations (`max_iterations` in `AgentExecutor`).
- **Data boundaries**: separate internal vs external tools; redact secrets in logs.

```python
safe_exec = AgentExecutor(
    agent=react_agent,
    tools=tools,
    verbose=True,
    max_iterations=8,
    handle_parsing_errors=True,
)
```

## Deployment Notes

- **Determinism**: `temperature=0`, tight prompts, structured tools.
- **Cold starts**: load vectorstores at startup; lazy-load heavy tool deps.
- **Concurrency**: prefer stateless executors; keep vectorstores in a shared service.
- **Monitoring**: LangSmith traces + custom metrics per tool call.

## Complete Minimal Template

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain.agents import create_react_agent, AgentExecutor

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

@tool
def calc(expression: str) -> str:
    """Evaluate a simple Python arithmetic expression like '37*42'."""
    try:
        return str(eval(expression, {"__builtins__": {}}))
    except Exception as e:
        return f"error: {e}"

tools = [calc]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a calculator assistant. Use the calc tool for math."),
    ("human", "{input}")
])

agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

print(executor.invoke({"input": "What is (37*42) + 5?"})["output"])
```
