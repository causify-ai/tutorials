# Sprint 6 – Notebook & Image Plan

## Phase 0 – Guardrails & Research
1. **Codify notebook best practices**  
   - Summarize the Context7 findings into `NOTEBOOK_BEST_PRACTICES.md` (plot/save same cell, `plt.show()`, nbformat summaries, nbclient error handling, optional `--allow-errors`).  
   - Update the router/system prompt so `intent === 'notebook'` injects these reminders once per notebook-centric exchange.  
   - Add a short unit test ensuring the router exports/include the guardrail text.
2. **Inventory current notebooks**  
   - Capture a baseline for `examples/notebooks/*` and `notebooks/sine_plot*.ipynb`.  
   - Document current regressions (blank PNG, missing metadata) for comparison after later phases.

## Phase 1 – Runner & Tool Enhancements
1. **Runner metadata** (`scripts/ipynb/runner.py`)  
   - Add optional args: `--allow-errors`, `--max-retries`, `--run-id`.  
   - Emit `{ started_at, finished_at, python_version, backend }` plus structured `errors`, `artifacts[]`, and run folder.  
   - Mirror the nbclient `try/except CellExecutionError` save pattern (per spec).  
   - Unit tests in Python to ensure `image/png` outputs create deterministic artifact paths.
2. **LangChain tool wiring**  
   - Update `ipynb_run` to surface metadata + errors + artifact info in JSON.  
   - Ensure `tool-summaries.ts` renders the new metadata (“2 plots saved, 0 errors”).  
   - Expand `scripts/notebook-smoketest.ts` to log metadata for CI diffing.
3. **Creation improvements**  
   - Allow `ipynb_create` to accept optional `dataSources[]` + `plot_specs[]` so the Python runner can pre-populate imports/tests.  
   - Validate output notebooks contain at least one markdown “inputs/outputs” cell.

## Phase 2 – Notebook Patching & Auto Re-run
1. **Notebook patch helper**  
   - Implement `src/tools/notebook_patch.ts` that loads a notebook, finds cells by index/substring, applies replacements/insertions, and emits a diff summary.  
   - Provide a DeepAgents tool (`ipynb_patch`) with schema: `{ inputPath, editInstructions[], outputPath? }`.
2. **Agent workflow integration**  
   - Ensure router instructions mention `ipynb_patch` when user asks to “change the code”, followed by `ipynb_run`.  
   - Update `scripts/notebook-smoketest.ts` with a scenario that edits a notebook and runs it again.
3. **Retry semantics**  
   - Honor `AGEN_TUI_NOTEBOOK_MAX_RETRIES`, but make `allowErrors` opt-in when user says “run even if errors”.

## Phase 3 – Artifact Tracking & Image Intelligence
1. **Artifact foldering**  
   - Runner saves PNGs under `<executed>-artifacts/cell-N.png` and returns `{ cell, path }`.  
   - Tools propagate this metadata so the UI and future prompts can mention `@notebooks/demo-executed-artifacts/cell-0.png`.
2. **Answering “where is the image?”**  
   - Implement a helper that searches the last notebook run metadata to answer location questions without rerunning the notebook.

## Phase 4 – Output Summaries & CLI Coverage
1. **Enhanced `ipynb_analyze`**  
   - Support options: `{ includeMarkdown, includeTables, includeArtifacts }`.  
   - Provide formatting utilities that mirror the `show_notebook` example (cell type + preview).  
   - Provide mention-aware responses when summarizing executed notebooks.
2. **CLI/TUI flows**  
   - Update `npm run agent:smoke` to issue a “plot CSV” request and verify the condensed outputs.  
   - Add dedicated smoke prompts:  
     - “Create @tmp/plot.ipynb from @data/sample.csv.”  
     - “Edit @notebooks/demo.ipynb to double the amplitude, rerun.”  
     - “Summarize @notebooks/demo-executed.ipynb outputs and list saved plots.”

## Phase 5 – QA, Docs, and Sign-off
1. **Regression matrix**  
   - `npm run test`, `npm run agent:testfs`, `npm run agent:smoke`, `scripts/notebook-smoketest.ts`.  
   - Manual TUI check replicating screenshot scenario (ensure figures save correctly).  
   - Verify `sine_plot` now produces a non-blank PNG inside the same cell.
2. **Documentation**  
   - Update README, `docs/notebook-pipeline.md`, and `docs/STATE.md` with new flows + guardrails.  
   - Add troubleshooting tips (“Why is my plot blank?”, “Where are artifacts stored?”).
3. **Handoff checklist**  
   - Record final state in `docs/STATE.md` and add follow-up tickets (e.g., sandboxing improvements) if necessary.

## Validation Checklist (Exit Criteria)
- [ ] Guardrail markdown is referenced in router/system prompt and verified via unit test.
- [ ] Runner outputs metadata + artifacts with deterministic paths.
- [ ] Notebook patching tool works for insert/replace/delete operations and is covered by tests.
- [ ] Smoke scripts demonstrate the three target flows (create from CSV, patch/rerun, summarize outputs).
- [ ] QA commands pass without breaking filesystem features.
