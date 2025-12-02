# Sprint 6 – Plan

## Phase 0: Repo & Tooling Foundation
- [x] **Inventory current code paths**
  - [x] Map every file under `src/` and `scripts/`.
  - [x] Identify modules that belong to new folders (`commands`, `config`, `tools`, `fs`, `ui`, etc.).
- [x] **Restructure**
  - [x] Move files without breaking imports (update tsconfig paths if needed).
  - [x] Add `ARCHITECTURE.md` summarizing folders + dependency flow.
- [x] **Tool registry skeleton**
  - [x] Create `src/tools/index.ts` exporting `buildTools(workspaceRoot)` that returns existing filesystem tools.
  - [x] Update `createAgentRunner` to import from `src/tools`.
  - [ ] Add docs snippet on how to add a tool.
- [x] Ensure both the TUI and `npm run agent -- "..."` use the same modules after refactor.

## Phase 1: Notebook Tooling
- [x] **Python helper**
  - [x] Create `scripts/ipynb/runner.py` (venv with `nbformat`, `nbclient`, `matplotlib`, `pandas`).
  - [x] CLI options: `create`, `run`, `summarize`. Use JSON stdin/stdout.
- [x] **LangChain tools**
  - [x] `ipynb_create_tool`: accepts plan/sections + output path.
  - [x] `ipynb_run_tool`: executes notebook, returns summary, errors, artifact locations.
  - [x] `ipynb_analyze_tool`: ingests notebook file and emits commentary per cell.
  - [x] Add unit tests mocking the Python runner responses.
- [x] **Self-correction loop**
  - [x] Inside the tool or middleware, detect failing cells and re-run until success limit (configurable).
- [x] **Sample notebooks & CLI**
  - [x] Place simple regression notebook in `examples/notebooks`.
  - [x] Add CLI script `npm run notebook:test` invoking the new tools end-to-end.
  - [x] Ensure `npm run agent -- "..."` can call the new notebook tools.

## Phase 2: Image Analysis
- [x] **Mention handling**
  - [x] Extend mention parser to tag image references (file extension check).
  - [x] When user references `@image.png`, enqueue the `analyze_image` tool.
- [x] **Tool implementation**
  - [x] `analyze_image_tool` converts/inspects the file and returns a textual description (currently dominant color + resolution, configurable for richer models).
  - [x] Provide options for summarization vs OCR vs “describe anomalies” *(baseline summarization implemented; follow-up enhancements noted).* 
- [ ] **Notebook integration**
  - [ ] When `ipynb_run` sees a base64 image in cell outputs, save as PNG under `plots/run-id/`.
  - [ ] Auto-trigger `analyze_image`.
- [ ] Ensure image analysis is available via `npm run agent -- "..."`.

## Phase 3: CLI regression scripts & docs
- [ ] `npm run agent -- "..."`
  - [ ] Add `scripts/fs-smoketest.ts` calling the inline CLI for ls/read/glob (existing shortcuts).
  - [ ] Add `scripts/ipynb-smoketest.ts` invoking notebook tools.
  - [ ] Document expected outputs (fail build if mismatch).
- [ ] README/docs
  - [ ] Update README sections (inline examples, notebook workflow, image handling).
  - [ ] Add `docs/tools.md` + `docs/notebook-pipeline.md`.

## Phase 4: QA & Rollout
- [ ] Run `npm run typecheck`, `npm run test`, `npm run notebook:test`.
- [ ] Manual scenario:
  - [ ] TUI: mention `@notebooks/demo.ipynb`, ask agent to “run and summarize the plots”.
  - [ ] CLI: `npm run agent -- "create a notebook that plots sin(x)"`.
- [ ] Collect follow-up tasks (perf/security).
