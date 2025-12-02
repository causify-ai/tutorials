# Sprint 6 – Robust Tooling & Notebook Intelligence

## 1. Objectives
1. **Repository structure & tooling framework** – consolidate all scripts and runtime helpers under consistent folders (`src/commands`, `src/config`, `src/tools`, `src/fs`, etc.), expose a documented pattern for adding new DeepAgents tools, and ensure CLI/TUI both consume those modules.
2. **Notebook tooling** – design a reliable `ipynb` toolchain so the agent can create, execute, and critique Jupyter notebooks (including image outputs). This includes dependencies, execution sandbox, validation, and feedback loop.
3. **Image understanding** – allow the agent to accept images (via `@image.png`) and use OpenAI’s multimodal APIs to describe or inspect them; integrate this with the notebook tooling so plots/images produced in cells can be re-interpreted by the agent.

## 2. Research & References
- **DeepAgents harness** (LangChain docs, [Deep Agents overview](https://docs.langchain.com/oss/javascript/deepagents/overview)): confirms that DeepAgents already expose filesystem tools and pluggable backends; new tools should extend the existing middleware pattern (custom `BaseTool` implementations passed to `createDeepAgent`).
- **LangChain tooling guide** ([Implement a LangChain integration](https://docs.langchain.com/oss/javascript/contributing/implement-langchain)): details the `BaseTool` interface and how schemas/args are defined—critical for the custom notebook + image-analysis tools.
- **LangGraph/DeepAgents FS middleware**: underscores the importance of sandboxing via `FilesystemBackend` with `virtualMode`. Notebook execution must run in a controlled workspace path to avoid corrupting user files.
- **OpenAI multimodal support** (OpenAI docs via Context7): models like `gpt-4o`, `gpt-5`, `o1` accept image inputs when payload contains `image_url` items. We can piggyback on LangChain’s `ChatOpenAI` multi-modal messages to feed `@image` references into tool outputs or system prompts.
- **Jupyter automation options**: `nbclient` (Python) or `jupyter_client` allows programmatic execution with cell-by-cell outputs; `papermill` can parameterize notebooks. These libraries can run inside a sandboxed subprocess and report status back to the TypeScript runner through a JSON IPC layer.

## 3. Feature Requirements
### 3.1 Repository/Layout cleanup
- Create dedicated folders:
  - `src/commands/` – slash command parsing & tests.
  - `src/config/` – loader, types, tests (already there but restructure exports).
  - `src/tools/` – reusable tool implementations (filesystem shortcuts, delete/copy, upcoming notebook/image tools).
  - `src/fs/` – filesystem helpers (`shortcuts`, mention normalization).
  - `scripts/` – CLI utilities (`agent-cli`, deepagents smoke tests, new regression scripts) with README.
- Provide an `ARCHITECTURE.md` explaining folder responsibilities and how CLI/TUI share modules.

### 3.2 Tooling framework
- Move existing custom tools (`delete_file`, `copy_file`) into `src/tools/filesystem.ts`. Export a builder function that returns an array of tools so `createAgentRunner` can import them cleanly.
- Document how to add a new tool:
  1. Implement a class/function conforming to LangChain’s `BaseTool` with Zod args schema.
  2. Provide unit tests hitting the tool directly.
  3. Register it inside `src/tools/index.ts`, which `createAgentRunner` consumes.
  4. Update README with usage examples / CLI shortcuts if needed.

### 3.3 Notebook tool suite
- **Tool set** (`ipynb_create`, `ipynb_run`, `ipynb_analyze`):
  - `ipynb_create`: accepts a plan (list of sections/objectives) + optional base file, produces a structured notebook using `nbformat` (Python service) and saves under workspace.
  - `ipynb_run`: executes a notebook (via `nbclient` or `papermill`) capturing stdout, errors, and artifacts (including image files). Execution should happen in a Python child process invoked with `python scripts/ipynb_runner.py --input path --output path`.
  - `ipynb_analyze`: loads a notebook, summarizes each cell, extracts plots/data, and surfaces key findings. Should allow filtering by cell index range.
- **Execution backend**:
  - Introduce a small Python helper inside `scripts/ipynb/` with dependencies `nbformat`, `nbclient`, `matplotlib` (for base plots), and optional `ipykernel`.
  - Maintain a temp directory under `.agentwork/ipynb` for outputs; mount via `FilesystemBackend` to keep DeepAgents state consistent.
- **Self-correction loop**: after running a notebook, parse each cell’s output. If any cell errors, feed the traceback back to the LLM along with the cell source so it can decide whether to rewrite a cell and re-run.
- **Testing**: Provide sample notebooks (e.g., `examples/notebooks/regression.ipynb`) plus scripts `npm run notebook:test` that execute them via the tool to ensure pipeline stability.

### 3.4 Image inputs & outputs
- Mention syntax `@images/chart.png` should:
  - Resolve the path via mention helpers.
  - Pass the absolute path into a new `analyze_image` tool that uploads the file using OpenAI vision API (`ChatOpenAI` multimodal message with `type: "image_url"` referencing a `data:` URL or local upload).
- Notebook integration:
  - When `ipynb_run` detects image outputs (typically base64 PNGs), save them to disk (`.png` files next to the notebook) and automatically call the `analyze_image` tool so the agent can describe the plot or anomalies.
  - Provide metadata linking the image back to the originating cell for context (e.g., `[Plot from cell 7 saved at /plots/run-123/cell-7.png]`).
- Add CLI examples:
  - `npm run agent -- "Analyze the chart at @plots/figure.png"`.
  - `npm run agent -- "Run @analysis.ipynb and describe the latest plot."`

### 3.5 Documentation
- Extend README / create `docs/tools.md` covering:
  - Folder organization.
  - How to register a new tool (with code snippet).
  - Notebook tool usage, including CLI commands and expected file locations.
  - Image analysis workflow.
- Add a `docs/notebook-pipeline.md` showing sequence diagrams (Agent → Tool → Python runner → Filesystem → Agent).

## 4. Risks & Open Questions
- **Security**: Running arbitrary notebooks poses risk; need to sandbox (e.g., Python venv, resource limits, disable network, maybe run with `timeout`). Capture in plan.
- **Performance**: Notebook execution could block the TUI; consider job queue / streaming updates.
- **Large images**: Vision API costs; add config to disable auto-analysis or limit resolution.
- **Cross-language tooling**: TypeScript app calling Python script—must handle failures gracefully (non-zero exit codes).

## 5. Deliverables
1. New repo layout + documentation (`ARCHITECTURE.md`, README updates).
2. Tool registry + guidelines (`src/tools/` module, docs).
3. Notebook tooling (create/run/analyze) with Python runner + sample notebooks.
4. Image analysis tool wired into mentions + notebook outputs.
5. CLI regression scripts proving each tool works (ls, read, glob, notebook, image).
