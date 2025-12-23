# AgenTUI Submodule Architecture Breakdown

## Summary
- Describes the high-level architecture of the AgenTUI codebase.
- Breaks down responsibilities by subsystem.
- Maps each responsibility to concrete files and directories.
- Serves as a reference for contributors navigating the project.

## Agent Core (Backend Logic)

Responsible for the agent runtime, including events, prompts, routing, and tool invocation.

## Responsibilities
- Handle incoming messages.
- Build structured prompts.
- Decide which tool to invoke.
- Dispatch actions and track internal events.

## Relevant Files
- `src/agent/index.ts` – Exports the agent interface.
- `src/agent/router.ts` – Routes requests to text generation, filesystem, notebook execution, or vision tools.
- `src/agent/events.ts` – Defines internal agent event types.
- `src/agent/prompt.ts` – Builds structured prompts from chat input.
- `src/agent/notebook-tips.ts` – Provides notebook-specific guidance to the agent.

## Tools Layer (LLM Tooling: FS, Notebook, Vision)

Implements callable functions that the agent can invoke.

## Responsibilities
- Read and write files.
- Resolve and sanitize paths.
- Execute Python or JavaScript code in notebooks.
- Analyze images.

## Relevant Files
- `src/agent/tools/index.ts` – Tool registry and exports.
- `src/agent/tools/filesystem.ts` – CRUD operations on files.
- `src/agent/tools/notebook.ts` – Notebook execution engine.
- `src/agent/tools/vision.ts` – Image recognition and analysis tools.
- `src/agent/fs/shortcuts.ts` – Common filesystem shortcuts.
- `src/agent/path/resolver.ts` – Robust path sanitizer and resolver.
- `src/agent/path/resolver.test.ts` – Tests for path resolution logic.

## State Management

Handles session data, usage statistics, and persistence.

## Responsibilities
- Track user sessions.
- Enforce usage limits.
- Maintain ephemeral and multi-turn state.

## Relevant Files
- `src/agent/state/session.ts`
- `src/agent/state/usage.ts`

## Configuration Layer

Exposes configuration commands and supports `agentui` configuration.

## Responsibilities
- Manage CLI-level settings.
- Store preferences such as path prefixes and project roots.

## Relevant Files
- `src/agent/config/index.ts`
- `src/agent/config/index.test.ts`

## CLI (Command-Line Interface)

Entry point for the `agentui` command.

## Responsibilities
- Parse CLI arguments.
- Execute commands (e.g., `config`, `smoketest`).
- Pipe input and output to the agent runtime.

## Relevant Files
- `bin/agentui.cjs` – CommonJS entry point.
- `bin/agentui.mjs` – ESM entry point invoked by the global symlink.
- `src/agent-cli.ts` – Core command logic.
- `src/cli.tsx`
- `src/models.ts`

## UI Layer (React Frontend)

Powers the interactive terminal UI (TUI) and hybrid UI.

## Responsibilities
- Render the input composer.
- Render the conversation transcript.
- Handle mentions and autocomplete.
- Process UI-side events.

## Relevant Files
- `src/ui/App.tsx`
- `src/ui/composer-renderer.ts`
- `src/ui/composer-input.test.tsx`
- `src/ui/transcript.test.tsx`
- `src/ui/mentions.ts`
- `src/ui/mentions.test.ts`

## UI Utilities

Reusable UI helpers shared across components.

## Responsibilities
- Image helpers.
- Text utilities.
- Message formatting.
- Tool summaries rendered in the UI.

## Relevant Files
- `src/utils/actions.ts`
- `src/utils/images.ts`
- `src/utils/messages.ts`
- `src/utils/text.ts`
- `src/utils/tool-summaries.ts`

## Notebook Pipeline

Manages notebook execution, artifact tracking, and result display.

## Responsibilities
- Run Jupyter and JavaScript notebooks.
- Capture execution outputs.
- Manage execution artifacts.

## Documentation
- `docs/NOTEBOOK_BEST_PRACTICES.md`
- `docs/notebook-pipeline.md`

## Sample Notebooks
- `notebooks/`
- `examples/*.ipynb`

## Documentation And Architecture Notes

Contains core architectural documentation.

## Relevant Files
- `ARCHITECTURE.md`
- `README.md`
- `docs/STATE.md`
- `docs/NOTEBOOK_BEST_PRACTICES.md`
- `docs/notebook-pipeline.md`

## Test Suite

Comprehensive test coverage across agent logic, tools, UI, and filesystem.

## Responsibilities
- Validate tool invocations.
- Ensure filesystem and notebook stability.
- Verify UI components and routing logic.

## Relevant Test Files
- `src/agent/**/*.test.ts`
- `src/ui/**/*.test.ts`
- `src/utils/**/*.test.ts`
- `src/commands/index.test.ts`

## Scripts (Utility And Smoketests)

Helper scripts for debugging and validation.

## Relevant Files
- `scripts/agent-smoketest.ts`
- `scripts/deepagents-model-test.ts`
- `scripts/notebook-smoketest.ts`
- `scripts/test-filesystem.ts`
- `scripts/image_analyzer.py`
- `scripts/plot_smoke.py`
- `scripts/test-agentui-bin.mjs`

## Sprint Markdown Documentation

Documents the evolution of the system over time.

## Location
- `sprint_markdowns/`

## Includes
- Plans
- Specifications
- Cleanup stages
- Notebook sprint documentation

## Last Review
- Arushi on 2025-12-23