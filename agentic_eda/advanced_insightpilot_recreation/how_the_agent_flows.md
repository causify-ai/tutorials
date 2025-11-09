## InsightPilot Agent Flow

This note captures how the current `insightpilot.py` orchestrates a run, what tools the LLM-driven agent can call, and how data moves through the pipeline.

### 1. Bootstrapping the State
- `run_insightpilot(...)` seeds the state dict with dataset path, question, empty insight inventory, notebook cell buffer, trace log, and a `meta_done` flag.
- The `StateGraph` connects the nodes: `llm_agent → tools → observe`, forming a loop until the status becomes `done`.
- `_dataset_brief` loads the CSV via `qin._load_dataset`, computes candidate dimensions/measures, and builds a textual briefing the LLM sees in its very first turn.

### 2. LLM Node (`llm_agent`)
- Builds the conversational context:
  - `SYSTEM_PROMPT` describes the four InsightPilot actions (`UNDERSTAND`, `SUMMARIZE`, `COMPARE`, `EXPLAIN`) and instructs how to finish (`FINAL_REPORT` + `VISUALIZE` directive).
  - Subsequent turns include an inventory of recent insights and the agent’s running thought log.
- The LLM returns either:
  - A tool call (one per turn) with arguments, or
  - A `FINAL_REPORT` block once it believes the story is complete.
- Console logging prints `[Thinking...]` then sleeps briefly to mimic latency; each LLM plan is echoed to the trace log.

### 3. Tool Bridge (`call_tools`)
- Examines the latest AI message; for each `tool_call`, it looks up the registered tool (`quick_insights_tool`, `meta_insights_tool`, `xinsight_tool`).
- Automatically injects the dataset path plus the user’s question (for QuickInsights) into the call.
- Logs the invocation details (`[InsightPilot] call_tools invoking ...`) and collects the JSON string returned by the tool into `ToolMessage`.

### 4. Tool Implementations

#### 4.1 QuickInsights (`quick_insights_tool`)
- Loads and normalises the dataset with `qin._load_dataset`, which now prints shape, parsing decisions, and caches the cleaned frame.
- Applies optional filters, auto-detects the most variable columns, drops low-variance measures when the dataset is wide, and samples rows when tall.
- Calls `qin.run_quickinsights`, which logs task progress and returns high-impact insights; a fallback auto-explanation step uses XInsight for top categories.
- Notebook output:
  - A markdown summary of the mined insights.
- JSON payload is sanitised so every value is JSON serialisable (timestamps are stringified).

#### 4.2 MetaInsight (`meta_insights_tool`)
- Reloads the dataset, honours the optional `measure`, `breakdown`, and `mode` (`summarize` vs `compare`).
- Seeds QuickInsights to build base scopes, then invokes `metain.generate_meta_insights`, logging each evaluated scope.
- Returns the top MetaInsights with descriptive markdown.

#### 4.3 XInsight (`xinsight_tool`)
- Reloads the dataset and re-applies any bucketing steps provided in the normalized arguments.
- Prints the query configuration, evaluates candidate predicates, and constructs causal/non-causal explanations summarising how conditioning shrinks the observed gap.
- The tool payload contains markdown only; visualisations are deferred until the final report requests them.

### 5. Observer Node (`observe`)
- Parses tool responses, normalises them into the shared `insights` list (assigning incremental IDs), and appends notebook cells.
- Records each tool result in the JSON trace log.
- If the model answers without a tool call, the node verifies the `FINAL_REPORT` format:
  - The report body (natural-language story).
  - A mandatory `VISUALIZE: ...` directive indicating which insight IDs require charts.
- After validation, the node:
  - Stores the final narrative.
  - Auto-generates Plotly visualisation cells for each referenced insight (using the shared dataset loader).
  - Appends all steps to the trace (including which IDs will be visualised).
- When max steps are hit without completion, the agent auto-finalises with the latest insights.

### 6. Output Artefacts
- Notebook: built from `notebook_cells` at the end of `run_insightpilot`.
- Trace: one JSON line per event (LLM plans, tool results, nudges, final report).
- Console: enriched with diagnostic logs from every stage for transparent execution on large datasets.

### 7. Summary of Available Functions & Access
- `qin._load_dataset`: shared ingestion helper (auto-parses datetimes, enriches time features, caches global frame).
- `qin.run_quickinsights`: core mining engine (supports wide/tall datasets through sampling/logging).
- `metain.generate_meta_insights`: interprets QuickInsights output to find homogeneous scopes.
- `xin.explain_difference`: explains Why-queries using predicate search.
- Agent utilities in `insightpilot.py`: formatting, auto-detection, visualisation builders, plan/trace management.

### 8. Execution Tips
- For debugging, watch the console diagnostics (prefixed `[QuickInsights]`, `[MetaInsight]`, `[XInsight]`, `[InsightPilot]`) to see progress and data reductions.
- When crafting prompts, ensure the final LLM response includes both `FINAL_REPORT:` and `VISUALIZE:` lines; the observer enforces this contract.
- Large CSVs can be explored safely—the instrumentation highlights any bottlenecks, and row/column guardrails prevent runaway computation.
