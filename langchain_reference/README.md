# Langchain Basics - Exercises

## E0 — Setup, Config, and “Hello LCEL”

### E0.1 — “Hello, Runnable”
**Goal:** Run a single prompt → model → string output with a stable entrypoint.  
**Deliverable:** `src/run_minimal.py` takes `--question` and prints an answer.  
**Definition of done:**
- Running twice with same input produces deterministic-ish structure (not necessarily identical text).
- Model/provider config comes from env vars (no secrets in code).
- Logs show which provider/model was selected.

### E0.2 — “Config-driven provider selection”
**Goal:** Choose among multiple LLM providers (at least 2) from env config.  
**Deliverables:**
- `src/config.py` (loads env, validates, builds provider-specific chat model)
- `src/run_minimal.py` supports `--provider` override (optional)
**Definition of done:**
- Switching env vars changes provider/model without code edits.
- Clear error messages if a provider is selected but required keys are missing.

### E0.3 — “First LCEL pipe”
**Goal:** Implement `prompt | llm | parser` as an LCEL chain.  
**Deliverable:** `src/run_lcel_pipe.py` that prints the parsed string output.  
**Definition of done:**
- Uses `ChatPromptTemplate` (or equivalent) and `StrOutputParser`.
- Chain object is reusable (not defined inside a tight loop).
- Minimal tests: `python src/run_lcel_pipe.py --question "..."` works.

---

## E1 — Runnables: invoke, batch, parallel, streaming

### E1.1 — “invoke() fundamentals”
**Goal:** Explain + demonstrate `.invoke()` with a chain.  
**Deliverable:** `src/run_lcel_pipe.py` using `.invoke({"question": ...})`.  
**Definition of done:**
- Inputs are dict-shaped (matching prompt variables).
- Output is a plain string (via parser).

### E1.2 — “RunnableParallel fan-out”
**Goal:** Run multiple subchains concurrently on the same input and merge outputs.  
**Deliverable:** `src/run_parallel.py` returns `{ "summary": ..., "risks": ... }`.  
**Definition of done:**
- Uses `RunnableParallel` (or dict-literal parallel in LCEL).
- Prints labeled outputs.
- Uses `config={"max_concurrency": ...}` (even if small).

### E1.3 — “batch() over a file”
**Goal:** Run the same chain over many inputs efficiently.  
**Deliverable:** `src/run_batch.py` reads `--questions src/questions.txt` and prints answers per line.  
**Definition of done:**
- Uses `.batch(inputs, return_exceptions=True)`.
- Preserves ordering.
- Gracefully reports per-question errors without crashing.

### E1.4 — “stream() / astream()”
**Goal:** Stream partial outputs (tokens/chunks) and reconstruct final output.  
**Deliverables:**
- `src/run_stream.py` (sync `.stream`)
**Definition of done:**
- Prints incrementally (flush output).
- Also assembles final output from chunks.
- Demonstrates difference between `stream_mode="updates"` vs `"values"` if using graphs later.

---

## E2 — Tools, ToolNode, InjectedState/Store

### E2.1 — “Tool 101”
**Goal:** Define safe, typed tools for deterministic computation.  
**Deliverable:** `tools/math_tools.py` with at least:
- `mean(xs: Sequence[float]) -> float`
- `zscore(xs: Sequence[float], x: float) -> float`
**Definition of done:**
- Validates inputs and raises clear errors.
- No side effects, no global state.

### E2.2 — “ToolNode sandbox (graph-based)”
**Goal:** Execute tool calls through ToolNode in a tiny StateGraph.  
**Deliverable:** `graphs/tool_node_smoke.py` that:
- Builds a `StateGraph` with `messages` reducer
- Adds `ToolNode([mean, zscore])`
- Feeds an `AIMessage(tool_calls=[...])`
**Definition of done:**
- ToolMessage results appear in `state["messages"]`.
- At least one tool error case is exercised.

### E2.3 — “InjectedState (system-only args)”
**Goal:** Create a tool that reads runtime state without exposing it to the LLM schema.  
**Deliverables:**
- `tools/state_tools.py` with one tool using `InjectedState("dataset_meta")`
- `graphs/injected_state_smoke.py` that proves injection works
**Definition of done:**
- Tool call args from the “model” do NOT include injected fields.
- Tool output confirms it received injected metadata from state.

### E2.4 — “InjectedStore (persistent memory handle)”
**Goal:** Persist preferences across invocations in a store injected at runtime.  
**Deliverables:**
- `tools/pref_injectedstore_tools.py` with `save_pref`, `load_pref` using `InjectedStore()`
- `graphs/injected_store_smoke.py` compiling graph with an `InMemoryStore`
**Definition of done:**
- `store.put` stores dict values (not raw strings).
- Second invocation reads what the first wrote.
- Model-facing tool schema does not include the store handle.

---

## E3 — Agent loop via create_agent + Middleware basics

### E3.1 — “Hello, create_agent”
**Goal:** Create a tool-calling agent and confirm the tool loop.  
**Deliverable:** `src/run_react_agent.py` that streams the run.  
**Definition of done:**
- Model produces tool calls.
- Tools execute and final answer uses tool outputs.
- Streaming prints meaningful intermediate steps.

### E3.2 — “Production wrapper”
**Goal:** Treat agent output as a state object and inspect message history.  
**Deliverable:** `src/run_create_agent_for_inspection.py` prints:
- state keys
- each message type (Human/AI/Tool)
- tool call names and tool outputs
**Definition of done:**
- You can clearly see the loop: Human → AI(tool_calls) → Tool → AI(final).

### E3.3 — “Middleware 101: add custom fields”
**Goal:** Add a middleware hook that writes an `audit` record into state.  
**Deliverables:**
- `middleware/log_middleware.py` defining a custom state schema containing `audit`
- `src/run_agent_with_middleware.py` prints `audit` and final answer
**Definition of done:**
- Middleware runs and `audit` exists in final returned state.
- `audit` shows at least: event name, number of messages at start.

---

## E4 — Low-level LangGraph agent + stateful routing

### E4.1 — “Hello, StateGraph”
**Goal:** Build a pure StateGraph with 2 nodes that update numeric state.  
**Deliverable:** `graphs/hello_state_graph.py`  
**Definition of done:**
- Nodes read full state, return partial updates.
- Final state shows merged updates.

### E4.2 — “Conditional routing”
**Goal:** Route to different nodes based on state.  
**Deliverable:** `graphs/route_by_flag.py`  
**Definition of done:**
- Different inputs choose different paths and outputs.

### E4.3 — “Reducers: accumulate evidence”
**Goal:** Implement a reducer to accumulate a list of findings across nodes.  
**Deliverable:** `graphs/reducer_accumulate.py`  
**Definition of done:**
- Final `evidence` contains contributions from multiple nodes (not overwritten).

### E4.4 — “ReAct loop from scratch”
**Goal:** Implement the tool-calling loop yourself using StateGraph + ToolNode.  
**Deliverable:** `graphs/react_from_scratch.py` with:
- `model` node: `llm.bind_tools(...)` then `.invoke(messages)`
- `tools` node: `ToolNode([...])`
- conditional edge: if last AIMessage has tool_calls → tools else end
- loop: tools → model
**Definition of done:**
- Printed message history shows: Human → AI(tool_calls) → ToolMessage(s) → AI(final).
- At least 2 different tools are invoked in a single run (e.g., time + math).

---

## E5 — IPYNB Operations (agent can write/run/debug notebooks + find artifacts)

### E5.1 — “Notebook as Data: create + validate + save”
**Goal:** Programmatically create a minimal `.ipynb` from scratch and write it to disk.

**Deliverables:**
- `ipynb_ops/write_notebook_min.py` (CLI)
- Output file: `notebooks/hello.ipynb`

**Exercise requirements:**
- Create a v4 notebook with:
  - 1 markdown cell (“# Hello”)
  - 1 code cell that prints something
- Validate notebook structure before writing
- Save it with `nbformat.write(...)`

**Definition of done:**
- `python ipynb_ops/write_notebook_min.py --out notebooks/hello.ipynb` creates a valid notebook file
- Opening the JSON shows `nbformat` version 4 and the expected cells

**If stuck, look here:**
- nbformat API for constructing notebooks (`new_notebook`, `new_code_cell`, `new_markdown_cell`) and writing (`nbformat.write`) :contentReference[oaicite:0]{index=0}

---

### E5.2 — “Write Notebook Tool: from spec → ipynb”
**Goal:** Wrap notebook creation in a LangChain/LangGraph **tool** the agent can call.

**Deliverables:**
- `tools/ipynb_tools.py` with tool `write_notebook(spec, out_path)`
- `graphs/ipynb_write_smoke.py` (or `run_write_tool.py`) that calls the tool once

**Exercise requirements:**
- Define a simple `spec` schema (e.g., list of cells with `{type, source}`)
- Tool writes to an **allowed workspace directory** only (no arbitrary paths)
- Tool returns the resolved notebook path

**Definition of done:**
- Agent/tool call produces a real `.ipynb`
- Attempting to write outside workspace is rejected (raise error)

**If stuck, look here:**
- nbformat “construct notebooks programmatically” + read/write API :contentReference[oaicite:1]{index=1}

---

### E5.3 — “Execute Notebook (nbclient): run and save executed copy”
**Goal:** Execute a notebook file and save an executed output notebook.

**Deliverables:**
- `ipynb_ops/execute_nbclient.py` (CLI): `--in`, `--out`, `--timeout`, `--kernel`
- `notebooks/hello.executed.ipynb`

**Exercise requirements:**
- Load notebook with `nbformat.read(..., as_version=4)`
- Execute using `nbclient.NotebookClient(...).execute()`
- Save the executed notebook with `nbformat.write(...)`
- Ensure execution happens in a specified working directory (`resources={'metadata': {'path': ...}}`)

**Definition of done:**
- Executed notebook contains populated cell outputs
- Running the script twice overwrites/creates a fresh executed notebook deterministically-ish

**If stuck, look here:**
- nbclient “Executing notebooks”: read → `NotebookClient(..., resources={'metadata': {'path': ...}})` → `execute()` :contentReference[oaicite:2]{index=2}

---

### E5.4 — “Error surfacing: catch CellExecutionError and still save”
**Goal:** If execution fails, your tool still writes an executed notebook containing the traceback up to the failing cell.

**Deliverables:**
- `notebooks/error_demo.ipynb` (created programmatically)
- `ipynb_ops/execute_nbclient_safe.py` which always writes `--out` even on failure

**Exercise requirements:**
- Create a notebook with a deliberate error (e.g., division by zero)
- Execute notebook with nbclient default behavior (stop on first error)
- Catch `CellExecutionError`
- Always save the partially executed notebook in a `finally` block

**Definition of done:**
- Script exits non-zero (or re-raises) on failure
- Output notebook exists and includes a traceback in the failing cell’s outputs

**If stuck, look here:**
- nbclient error handling patterns: `CellExecutionError`, save notebook after exceptions :contentReference[oaicite:3]{index=3}

---

### E5.5 — “Collect ALL errors: allow_errors=True + per-cell error index”
**Goal:** Execute the whole notebook even if multiple cells error, and extract a structured error report.

**Deliverables:**
- `ipynb_ops/execute_collect_errors.py`
- `artifacts/error_report.json`

**Exercise requirements:**
- Run with nbclient configured to allow errors across the notebook
- After execution, scan each code cell’s outputs and extract:
  - cell index
  - exception name/value
  - first N traceback lines
- Save that as JSON

**Definition of done:**
- Notebook runs to completion (no stop at first error)
- `error_report.json` lists every failing cell (not just the first)

**If stuck, look here:**
- nbclient: `allow_errors` behavior + how errors are recorded in outputs :contentReference[oaicite:4]{index=4}
- nbconvert execute docs also describe `allow_errors` semantics (useful cross-check) :contentReference[oaicite:5]{index=5}

---

### E5.6 — “Artifact locator: extract text outputs + inline images from executed notebook”
**Goal:** After execution, locate and export notebook artifacts:
- text outputs (stdout / `text/plain`)
- inline images (`image/png` in output mimebundle)

**Deliverables:**
- `ipynb_ops/extract_artifacts.py`
- Output folder: `artifacts/run_<id>/`
  - `cell_<k>_stdout.txt` (when present)
  - `cell_<k>_display_0.png` (when present)
  - `manifest.json` (index of exported artifacts)

**Exercise requirements:**
- Parse executed notebook JSON and find:
  - `stream` outputs (stdout)
  - `execute_result` / `display_data` mimebundles for `text/plain`, `image/png`
- Decode `image/png` base64 and write `.png` files
- Produce a manifest mapping cell index → artifact paths

**Definition of done:**
- A notebook that produces matplotlib plots results in PNGs on disk
- A notebook that prints text results in exported text files
- Manifest points to all exported files

**If stuck, look here:**
- nbclient guarantees executed notebooks have cell outputs populated after `execute()` :contentReference[oaicite:6]{index=6}
- nbformat is the reference implementation of the notebook format (you’re parsing the real schema) :contentReference[oaicite:7]{index=7}

---

### E5.7 — “Filesystem artifacts: run notebooks that write files + find them”
**Goal:** Support notebooks that produce artifacts by writing to disk (CSVs, PNGs, HTML, etc.), and reliably locate those paths afterward.

**Deliverables:**
- `notebooks/writes_files.ipynb` (created programmatically)
- `ipynb_ops/run_and_collect_files.py`
- `artifacts/run_<id>/files_manifest.json`

**Exercise requirements:**
- The notebook must write at least:
  - one `.csv`
  - one `.png` (saved to disk, not inline)
- Enforce a run directory (e.g., `workspace/runs/<id>/`) and set notebook execution `cwd`/path accordingly
- After execution, walk the run directory and collect generated files

**Definition of done:**
- All on-disk outputs appear under the run directory
- The collected manifest includes relative paths + sizes + mime guesses

**If stuck, look here:**
- nbclient supports specifying execution working directory via `resources={'metadata': {'path': ...}}` :contentReference[oaicite:8]{index=8}

---

### E5.8 — “Agent integration: ipynb operations as Tools + secure state injection”
**Goal:** Put everything behind tools so an agent can do:
- write notebook
- execute notebook
- read error report
- locate artifacts

**Deliverables:**
- `tools/ipynb_tools.py` tools:
  - `write_notebook(...)`
  - `run_notebook(...)`
  - `extract_errors(...)`
  - `extract_artifacts(...)`
  - `list_run_files(...)`
- `graphs/ipynb_agent_loop.py` (LangGraph):
  - `model` node (tool-calling)
  - `tools` node (ToolNode)
  - state includes `workspace_dir`, `run_id`, `last_run_paths`
- Add **InjectedState** for `workspace_dir` so the model never controls it

**Exercise requirements:**
- Agent prompt: “Create a notebook that plots sin(x), run it, and tell me where the outputs are.”
- Agent must solve it only by tool calls (no manual code execution outside tools)
- Tool schemas presented to the model must NOT include injected runtime-only fields

**Definition of done:**
- Run produces:
  - executed notebook path
  - artifacts directory
  - extracted PNG path(s) and/or on-disk file list
- Attempted path traversal in the user prompt does not escape workspace

**If stuck, look here:**
- nbclient CLI alternative: `jupyter execute notebook.ipynb` plus flags like `--allow-errors` (useful for validating behavior) :contentReference[oaicite:9]{index=9}

---

### E5.9 (optional bonus) — “Parameterized runs (Papermill)”
**Goal:** Parameterize a notebook run (e.g., different dataset path / hyperparameters) and save outputs per run.

**Deliverables:**
- `ipynb_ops/run_papermill.py`
- Run outputs: `runs/<id>/out.ipynb` + artifacts

**Exercise requirements:**
- Define a notebook with a `parameters` cell
- Execute using papermill (Python API or CLI) with injected parameters
- Keep run output notebooks separate per run id

**Definition of done:**
- Two runs with different parameters produce two different output notebooks
- Each run’s output notebook is saved to the correct run directory

**If stuck, look here:**
- Papermill execution examples (Python API + CLI) :contentReference[oaicite:10]{index=10}


---

## E6 — Subagents: Supervisor, Context Isolation, Subgraphs, and HITL

> **Theme:** Learn the **Subagents** architecture: a **main “supervisor” agent** coordinates specialized **subagents** by calling them as **tools**, giving you **context isolation** and cleaner orchestration. You’ll then extend that into **subgraphs** (graph-as-node composition) and **human-in-the-loop** safety gates.
>
> **Primary docs (keep open):**
> - Subagents (Supervisor ↔ subagents via tools): https://docs.langchain.com/oss/python/langchain/multi-agent/subagents
> - Subgraphs (add a graph as a node + inspect subgraph state): https://docs.langchain.com/oss/python/langgraph/use-subgraphs
> - Interrupts / HITL (pause + resume with `Command`): https://docs.langchain.com/oss/python/langgraph/interrupts
> - Human-in-the-loop (interrupt-on-tools + review workflow): https://docs.langchain.com/oss/python/langchain/human-in-the-loop

---

### E6.1 - “Supervisor + 1 subagent (as a tool)”
**Goal:** Build a supervisor agent that delegates a single specialized task to a subagent wrapped as a tool.

**Deliverables:**
- `src/subagents_supervisor_one_worker.py`

**Exercise requirements:**
- Create a subagent with `create_agent(...)` that performs **one** capability (e.g., summarization).
- Wrap it as `@tool("summarize_text", ...)` and return only the subagent’s **final** message text.
- Supervisor must call the tool when asked to summarize.

**Definition of done:**
- Running `python src/subagents_supervisor_one_worker.py` shows:
  - supervisor emits a tool call → tool returns summary → supervisor returns final answer.

**If stuck, look here:**
- Subagents “Basic implementation” (wrap subagent as a tool): https://docs.langchain.com/oss/python/langchain/multi-agent/subagents

---

### E6.2 — “Two subagents, clean tool boundaries”
**Goal:** Make the supervisor reliably pick the correct subagent by using clear tool descriptions and specialized subagent prompts.

**Deliverables:**
- `src/subagents_two_workers.py`

**Exercise requirements:**
- Create two subagents:
  - **Date agent:** normalize date/time phrases into a structured format.
  - **Email agent:** draft a short professional email body.
- Wrap both as tools with **action-oriented** descriptions.
- Use the `tests = [...]` list inside the script; uncomment/add more prompts to see which tool gets called (the file currently has 1 active test and several commented examples).

**Definition of done:**
- For each test prompt you run, the supervisor calls the expected tool and returns a correct final answer.

**If stuck, look here:**
- “Key characteristics” + “When to use” + “Basic implementation”: https://docs.langchain.com/oss/python/langchain/multi-agent/subagents

---

### E6.3 — “Context isolation proof (noisy worker, clean supervisor)”
**Goal:** Demonstrate the *reason* subagents exist: the worker can do “noisy” work internally, but the supervisor sees only a concise final result.

**Deliverables:**
- `src/subagents_context_isolation.py`

**Exercise requirements:**
- Give the **worker subagent** a tool that can generate a large output (toy: `generate_noise(n_chars)`).
- Force the worker to call it, but require the worker’s final message to be concise.
- Print debugging stats:
  - number of worker messages
  - approximate character count in worker transcript
  - supervisor transcript stats (should be much smaller)

**Definition of done:**
- You can visibly show the worker’s internal context is “large/noisy”, but the supervisor’s context stays “small/clean”.

**If stuck, look here:**
- “Context isolation / context bloat” motivation: https://docs.langchain.com/oss/python/langchain/multi-agent/subagents

---

### E6.4 — “Pass state into a subagent (ToolRuntime + runtime.state)”
**Goal:** Feed *just enough* supervisor state into a subagent call (preferences, metadata, prior results) without giving the model full control.

**Deliverables:**
- `src/subagents_pass_state.py`

**Exercise requirements:**
- Extend the agent state schema (an `AgentState` extension / TypedDict-style schema) with `user_prefs` (e.g., `{"tone": "formal"}`) and pass it via `state_schema=...` to `create_agent(...)`.
- In the subagent tool wrapper, accept `runtime: ToolRuntime[...]` and read `runtime.state["user_prefs"]`.
- Use that preference to alter the worker’s prompt/context.

**Definition of done:**
- Running `python src/subagents_pass_state.py --tone friendly` vs `python src/subagents_pass_state.py --tone formal` changes the output.

**If stuck, look here:**
- “Subagent inputs” (`ToolRuntime`, `runtime.state`): https://docs.langchain.com/oss/python/langchain/multi-agent/subagents

---

### E6.5 — “Subagent outputs update supervisor state (Command(update=...))”
**Goal:** Return a structured state update from a tool call (facts, plan, artifact registry), not just plain text.

**Deliverables:**
- `src/subagents_command_update.py`

**Exercise requirements:**
- Worker extracts structured information (toy: list of key facts) as JSON.
- Tool returns a `Command(update={...})` that:
  - writes `facts: list[str]` into supervisor state
  - returns a `ToolMessage` tied to the tool call id (use `InjectedToolCallId`)

**Definition of done:**
- Final printed state includes `facts` populated.
- Supervisor’s final answer explicitly uses `facts`.

**If stuck, look here:**
- “Subagent outputs” → “Format in code” using `Command`: https://docs.langchain.com/oss/python/langchain/multi-agent/subagents
- HITL / interrupts + `Command` example (good reference for resume/update mechanics): https://docs.langchain.com/oss/python/langchain/human-in-the-loop

---

### E6.6 — “Parallel subagent calls (multiple tools in one turn)”
**Goal:** Have the supervisor emit **multiple tool calls** in a single model turn and then merge results.

**Deliverables:**
- `src/subagents_parallel_tool_calls.py`

**Exercise requirements:**
- Create 3 tools (each wraps a subagent):
  1) summarize
  2) extract action items
  3) draft a reply
- In the supervisor prompt: explicitly instruct it to call **all three tools** and then synthesize.

**Definition of done:**
- In streaming output, you can see a single assistant message that contains **3 tool calls** before tool results arrive.

**If stuck, look here:**
- “Parallel execution” characteristic of subagents: https://docs.langchain.com/oss/python/langchain/multi-agent/subagents

---

### E6.7 — “Subgraphs: add a graph as a node (workflow encapsulation)”
**Goal:** Implement a worker as a small LangGraph graph and embed it inside a parent graph as a node.

**Deliverables:**
- `graphs/subgraph_worker.py` (defines a compiled subgraph + a parent graph that calls it)

**Exercise requirements:**
- Subgraph: two nodes (toy: parse → format).
- Parent graph: calls subgraph node and returns result.
- Stream with `subgraphs=True` and observe events.

**Definition of done:**
- Parent graph run works.
- Streaming shows subgraph activity when `subgraphs=True`.

**If stuck, look here:**
- “Add a graph as a node” + “View subgraph state”: https://docs.langchain.com/oss/python/langgraph/use-subgraphs

---

### E6.8 — “Shared vs private memory boundaries (checkpointers)”
**Goal:** Understand persistence boundaries: when state is shared vs isolated across graph components.

**Deliverables:**
- `graphs/subgraph_memory_boundaries.py`

**Exercise requirements:**
- Implement a subgraph that increments a counter `n`.
- Run two “turns” (same `thread_id`) in:
  - (A) shared mode: parent carries forward `n`
  - (B) private mode: subgraph persists with its own checkpointer/thread namespace
- Print `n` after each turn.

**Definition of done:**
- You can demonstrate different persistence behavior in shared vs private.

**If stuck, look here:**
- Subgraphs + persistence guidance: https://docs.langchain.com/oss/python/langgraph/use-subgraphs

---

### E6.9 — “Human-in-the-loop gate for sensitive tools (interrupt + resume)”
**Goal:** Add a safety gate: pause execution for review before a sensitive action runs, then resume with an approval decision.

**Deliverables:**
- `graphs/hitl_worker.py`

**Exercise requirements:**
- Create a “sensitive tool” (toy: delete a file within a sandbox dir).
- Add an interrupt step before executing the tool.
- Implement resume flow using `Command(resume=...)`.

**Definition of done:**
- First invocation returns an `__interrupt__` payload you can display to the user (this repo’s `graphs/hitl_worker.py` demonstrates `invoke(...)` returning `__interrupt__` rather than raising).
- Second invocation with `Command(resume="approve")` completes the action (the demo currently auto-resumes; swap in `input()` if you want an actual pause).
- With `resume="reject"`, the action does not run.

**If stuck, look here:**
- Interrupts concept + resume semantics: https://docs.langchain.com/oss/python/langgraph/interrupts
- “Responding to interrupts” end-to-end flow: https://docs.langchain.com/oss/python/langchain/human-in-the-loop

---
## E7 — Deep Agents (DA1 → DA8.1)

> Scope: DA1 through DA8.1 only (no DA8.2+).  
> Goal: Become proficient with Deep Agents primitives: planning (todos), filesystem surface, backends, subagents, compiled subagents, HITL gates, and sandboxing.

---

### E7.1 — Hello, Deep Agent

**Goal:** Run a deep agent end-to-end on a multi-step toy task.

**Deliverable:** `deepagents/hello_deepagents.py`

**Definition of done:**
- Running `python deepagents/hello_deepagents.py` prints a coherent multi-step answer.
- You can print the returned state keys (e.g., `messages`, possibly `todos`, `files`).

**Hints if stuck:**
- Deep Agents overview: https://docs.langchain.com/oss/python/deepagents/overview
- `create_deep_agent` reference (args + state shape): https://reference.langchain.com/python/deepagents/graph/

---

### E7.2  — Planning tool: write_todos

**Goal:** Force the agent to create and update an explicit todo list using the built-in planning tool.

**Deliverable:** `deepagents/todos.py`

**Definition of done:**
- The agent calls `write_todos` (verify via streaming logs or by inspecting `out_state["todos"]`).
- The final answer references the todo list.
- You can print `out_state.get("todos")` and see non-empty content.

**Hints if stuck:**
- Middleware / todo list: https://docs.langchain.com/oss/python/deepagents/middleware
- Deep Agents overview (todos + planning): https://docs.langchain.com/oss/python/deepagents/overview

---

### E7.3  — Filesystem surface: read/write notes

**Goal:** Make the agent offload content into a file, then read it back and cite it in the final answer.

**Deliverable:** `deepagents/filesystem_notes.py`

**Definition of done:**
- Agent uses `write_file` to create `/workspace/notes.md`.
- Agent uses `read_file` and the final answer quotes exactly 2 bullets from that file.
- If your version exposes a `files` channel, you can confirm the path exists in state.

**Hints if stuck:**
- Backends + filesystem tools: https://docs.langchain.com/oss/python/deepagents/backends
- `create_deep_agent` reference (backend/store/checkpointer): https://reference.langchain.com/python/deepagents/graph/

---

### E7.4  — Backends matrix: State vs Filesystem vs Store

**Goal:** Understand where files live and what persists across turns/threads by comparing three backend setups.

**Deliverable:** `deepagents/backends_matrix.py`

**Definition of done:**
- **StateBackend**: thread B cannot read the file written in thread A under `/workspace/...`.
- **FilesystemBackend**: thread B can read the file written in thread A (stored on disk under `root_dir`).
- **StoreBackend (via CompositeBackend routes like `/memories/`)**: thread B can read the file written in thread A under `/memories/...`.

**Hints if stuck:**
- Backends (StateBackend, FilesystemBackend, StoreBackend, CompositeBackend) + security notes: https://docs.langchain.com/oss/python/deepagents/backends
- `create_deep_agent` reference: https://reference.langchain.com/python/deepagents/graph/

---

### E7.5 — Subagents inside deepagents (task delegation + context quarantine)

**Goal:** Configure a dict-based subagent and delegate a piece of work to it via the built-in `task(...)` tool.

**Deliverable:** `deepagents/dict_subagents.py`

**Definition of done:**
- Main agent uses `task(...)` to call the subagent.
- Final answer is concise and clearly reflects the delegated result (without dumping long intermediate scratch).

**Hints if stuck:**
- Subagents docs (dict subagents): https://docs.langchain.com/oss/python/deepagents/subagents
  
**Notes (repo-specific):**
- The `task` tool signature is `task(description=..., subagent_type=...)` (not `task(name=..., task=...)`).

---

### E7.6  — CompiledSubAgent: subagent as a compiled LangGraph runnable

**Goal:** Replace a dict subagent with a compiled runnable (LangGraph agent/graph) using `CompiledSubAgent`.

**Deliverable:** `deepagents/compiled_subagent.py`

**Definition of done:**
- You build a compiled runnable (e.g., from `langchain.agents.create_agent` or your own `StateGraph(...).compile()`).
- Register it as a `CompiledSubAgent(name=..., runnable=...)`.
- Main agent delegates via `task(description="...", subagent_type="...")` and returns a cleaned-up final response.
- No state-schema errors (compiled runnable must have `messages` in its state).

**Hints if stuck:**
- Subagents docs (CompiledSubAgent requirements): https://docs.langchain.com/oss/python/deepagents/subagents
- LangGraph subgraphs concept (if building your own runnable): https://docs.langchain.com/oss/python/langgraph/use-subgraphs

---

### E7.7  — HITL gates: interrupt_on + resume

**Goal:** Require human approval before a risky operation (e.g., `edit_file`) and resume execution after approval.

**Deliverable:** `deepagents/hitl.py` (CLI-based HITL is fine)

**Definition of done:**
- First run interrupts when the gated tool is about to run.
- You surface the pending action to the human (at minimum: print/stream events).
- You resume with a HITLResponse payload, e.g. `Command(resume={"decisions": [{"type": "approve"}]})` (or `"reject"`), using the same `thread_id`.
- The run completes and you can verify the gated action did/didn’t happen.

**Hints if stuck:**
- Deep Agents HITL: https://docs.langchain.com/oss/python/deepagents/human-in-the-loop
- `create_deep_agent` needs checkpointer + thread_id for resumability: https://reference.langchain.com/python/deepagents/graph/

---

### E7.8  — Security posture: sandboxed FilesystemBackend (virtual_mode=True)

**Goal:** Configure a least-privilege sandbox so the agent can read/write only within a safe root, and cannot escape to host paths.

**Deliverable:** `deepagents/sandboxing.py`

**Definition of done:**
- Files under `/workspace/...` can be written/read successfully.
- Attempts to read outside the sandbox (e.g., `../.env`, `/etc/hosts`) are blocked by `virtual_mode=True` (often as a `ValueError: Path traversal not allowed` unless you catch/convert tool errors).
- Files written by the agent end up under your chosen sandbox `root_dir`.
- You use `FilesystemBackend(root_dir=..., virtual_mode=True)`.

**Hints if stuck:**
- Backend security warnings; `virtual_mode=True` prevents `..`, `~`, and escape paths: https://docs.langchain.com/oss/python/deepagents/backends
- `create_deep_agent` backend parameter: https://reference.langchain.com/python/deepagents/graph/
