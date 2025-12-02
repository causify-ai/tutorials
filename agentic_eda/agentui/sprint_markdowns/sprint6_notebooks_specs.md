# Sprint 6 – Notebook & Image Flows Specifications

## 1. Background & Current Observations
- Sprint 6 already delivered the Python runner (`scripts/ipynb/runner.py`), LangChain tools (`ipynb_create`, `ipynb_run`, `ipynb_analyze`), and a lightweight vision helper, but the workflows are brittle: the agent can still emit notebooks that save plots in a separate cell (yielding blank PNGs such as `notebooks/sine_plot.executed.ipynb` → `tmp/sine_wave.png`), lacks a way to patch/re-run notebooks, and does not surface notebook artifacts back into the chat.
- User requests cluster around three flows: (1) “create a notebook that plots @<csv>”, (2) “edit @<notebook> to change <this> to <that> and run it again”, and (3) “inspect the outputs of @<notebook> (e.g., find where an image was saved, summarize results, explain errors).”
- The notebook tooling must not regress any filesystem shortcuts or mention resolution rules that Cleanup 5 established.

## 2. Notebook Best-Practice Prompt (Context7 Research)
We need a reusable snippet that the router/system prompt can inject whenever a request is routed to the notebook intent. The guardrails should paraphrase the following documented practices so the LLM avoids mistakes:
1. **Plot and save in the same cell** – Matplotlib’s figure intro shows that calling `fig, ax = plt.subplots()` and `fig.savefig('MyFigure.png', dpi=200)` keeps the file in sync with the plot ([Context7 `/matplotlib/matplotlib` → `doc/galleries/users_explain/figure/figure_intro.rst`]). Always capture the figure handle and save (and `plt.close(fig)`) inside the cell that builds the plot.
2. **Show inline results if the user expects them** – The official binder example notebook plots sine/cosine and immediately calls `plt.show()` ([Context7 `/jupyter/notebook` → `binder/example.ipynb`]). Include `plt.show()` unless the instructions say to keep the plot headless.
3. **Summaries iterate through cells** – The `show_notebook` helper provided in Jupyter’s “Importing Notebooks” example iterates over `nb.cells` and records `cell.cell_type` plus a preview ([Context7 `/jupyter/notebook` → `docs/source/examples/Notebook/Importing Notebooks.ipynb`]). Use `nbformat` rather than regexp scraping when summarizing or locating code to edit.
4. **Execution should fail fast but persist notebooks** – The nbclient docs demonstrate wrapping `client.execute()` in `try/except CellExecutionError` with a `finally: nbformat.write(...)` block, emitting a helpful error that points at the executed copy ([Context7 `/jupyter/nbclient` → `docs/client.rst`]). Our tools should mirror that pattern, logging tracebacks and saving the executed notebook even if a cell fails.
5. **Optional “run despite errors” mode** – nbclient’s CLI exposes `jupyter execute notebook.ipynb --allow-errors`, so the tool should only enable the equivalent flag when the user explicitly asks to gather all failures ([same reference as #4]).

We will codify these bullets as a Markdown fragment (e.g., `NOTEBOOK_BEST_PRACTICES.md`) that the router/system prompt can concatenate or reference when `intent === 'notebook'`.

## 3. Functional Requirements

### 3.1 Notebook Creation from Source Data
- When the user says “make me a notebook that plots @foo.csv”, the agent must:
  - Resolve the mention via the existing resolver.
  - Inspect the CSV header/column types to propose a short plan (markdown seed + code cells) before calling `ipynb_create`.
  - Ensure the generated code reads the CSV relative to the workspace and saves plots with deterministic filenames (reuse `@tmp` or a user-provided output dir).
  - Immediately call `ipynb_run` with an executed-path suffix (e.g., `<notebook>-executed.ipynb`), then describe the outputs (cells, saved plots, textual summary).
- Runner enhancements:
  - Allow `create` to accept structured metadata (data source path, requested plots) so the Python helper can pre-populate imports and scaffolding.
  - Add validation that generated notebooks contain at least one markdown “context” cell explaining inputs/outputs.

### 3.2 Notebook Editing / Patching & Re-run
- Provide a `notebook_patch` helper (TypeScript) that:
  - Uses `nbformat` to locate cells by index or substring, applies replacements, and writes an updated notebook (similar to `apply_patch` for JSON).
  - Emits a diff summary so the UI can show what changed.
- Extend the router/tool schema so the agent can express prompts like “replace the plot range from 0-10 with 0-20” or “add a cell after cell 2 to normalize the data”.
- After patching, automatically trigger `ipynb_run` (respecting the retry limit / error handling) and post a concise execution summary.

### 3.3 Execution Resilience & Metadata
- Update the Python runner to:
  - Record execution start/end timestamps, kernel info, and environment details (Python version, matplotlib backend).
  - Optionally accept `--allow-errors` and `--max-retries` flags.
  - Attach any stack traces to the `errors` array exactly as nbclient emits them so the agent can quote specific cells.
- Update `ipynb_run` tool output so DeepAgents sees artifacts, error counts, and metadata in structured JSON (the tool summary will continue to produce human-friendly descriptions).

### 3.4 Artifact Tracking & Image Intelligence
- The runner already writes PNGs for cells containing `image/png` output; extend it to:
  - Save images into a run-specific folder (`<executed-basename>/artifacts/cell-#`).
  - Return `{ cell, image_path }` pairs so the TUI can link to them.
- After execution, enqueue `analyze_image` for each new PNG and embed the caption in the chat transcript (“Cell 3 plot saved to … – dominant color …”).
- Permit users to ask “where is the sine plot saved?”; the analyze/summarize commands should respond using the recorded artifact metadata.

### 3.5 Output Summaries & Q&A
- Expand `ipynb_analyze` to optionally include:
  - Markdown extraction (headers, bullet points).
  - Numeric output snapshots (first N rows of pandas tables).
  - Artifact references.
- Build a `summarize_notebook_outputs` helper used by the agent when the user asks for “what happened in the executed notebook?” (should prefer the executed copy if it exists).

### 3.6 CLI/TUI Flow Support
- `scripts/notebook-smoketest.ts` must cover:
  - Create-from-plan + run + artifact detection.
  - Patch + re-run scenario (ensure diff is printed).
  - Summaries referencing an image path.
- Update `npm run agent:smoke` to include a notebook request, verifying that the plan/resolution/responses remain deterministic.

## 4. Constraints & Non-Goals
- **No regressions**: All filesystem shortcuts, mention resolution, and Cleanup 5 behavior must continue to pass (`npm run agent:testfs`, `npm run test`, `npm run agent:smoke`).
- **Sandbox only**: The runner must continue to operate inside the workspace root with no network access (aside from the existing OpenAI image caption tool when explicitly requested).
- **Performance**: Notebook execution should stream progress (or at least emit a status notification) if runs exceed ~5 seconds; for now we will log start/end timestamps for debugging.
- **Security**: Consider adding an allowlist of imports or a timeout guard in the Python runner to prevent runaway notebooks (documented for future work if not implemented now).

## 5. Deliverables & Acceptance Criteria
1. `NOTEBOOK_BEST_PRACTICES.md` (or similar) referenced by the agent router/system prompt.
2. Enhanced Python runner + TS tools with structured metadata, patch helper, artifact linkage, and error handling patterns described above.
3. Updated UI copy/action summaries highlighting notebook operations (e.g., “Ran notebooks/demo.ipynb → notebooks/demo-executed.ipynb (1 plot saved, no errors)”).
4. Tests/smoke scripts proving the three target flows work end-to-end.
5. Documentation updates (README, docs/notebook-pipeline.md, STATE handoff) summarizing the new flows and reminding maintainers not to break filesystem functionality when extending notebooks further.
