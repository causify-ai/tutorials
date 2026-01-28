# AgenTUI

Codex-inspired terminal client that wraps LangChain Deep Agents. The app exposes a full-screen Ink TUI for day-to-day chatting plus a single-shot CLI command that you can use to test the agent deterministically.

## Highlights

- **DeepAgents integration** with OpenAI `gpt-5-mini` by default.
- **Filesystem-aware mentions**: typing `@src/ui/App.tsx` auto-completes paths and turns them into the virtual `/src/ui/App.tsx` references DeepAgents expects.
- **Filesystem harness shortcuts**: natural prompts such as "list the files in @node_modules/" or "search for 'FilesystemBackend' in @src/" automatically call the correct tools (`ls`, `read_file`, `glob`, `grep`, etc.). The shortcuts now understand both the legacy `targetPath` style arguments and DeepAgents' canonical `file_path` / `dir_path` names, so GPT-4o-mini and GPT-5-mini both stay happy.
- **Intent-aware routing** that classifies each prompt as conversational, filesystem, notebook, or mixed so the agent responds naturally when no tools are needed and plans multi-step work when they are.
- **Notebook IQ** – `ipynb_create`, `ipynb_patch`, `ipynb_run`, `ipynb_analyze`, and the new `ipynb_artifacts` tool let the agent create, edit, execute, summarize, and look up artifact locations without manual spelunking. See `docs/notebook-pipeline.md`.
- **Responsive composer** – the input box now buffers keystrokes locally (no more overwritten characters), expands up to 6 lines, scrolls internally when you paste large blocks of text, sanitizes clipboard junk (CR/LF/tabs) so borders never explode, and is backed by a deterministic `renderComposerView(value, cursor, width)` helper so layout/viewport changes are snapshot-tested.
- **Global `agentui` binary** – after building once, run `npm install -g .` (or `npm link`) to expose an `agentui` command that launches the TUI from whatever directory you invoke it in. Change the prefix later with `npm run bin:set -- <new-name>` and re-link.
- **Inline CLI mode** via `npm run agent -- "prompt"` for deterministic testing.
- **Reasoning visibility control**: the model emits `ReasoningVisible: yes|no` before every response; reasoning is buffered until the flag arrives so trivial replies stay clean and multi-step/tool work streams a dim gray plan without flicker.
- **Natural-language action summaries** so the Actions list reads like “Listed / (23 entries)” instead of raw JSON blobs.
- **Reasoning → Actions → Answer parity** between the TUI and CLI: both surfaces stream plan updates, normalized tool summaries, and a final conversational answer sourced from the same structured event pipeline.
- **Robust path highlighting** keeps entire filenames/paths cyan (even when the agent returns bare filenames like `sprint1_plan.md`) without lighting up random sentences.
- **Slash commands** for `/model`, `/new`, `/undo`, `/files`, `/quit`.

## Installation

```bash
npm install
cp .env.example .env   # fill OPENAI_API_KEY
npm run dev             # launch the Ink TUI
```

Build/run the compiled binary with:

```bash
npm run build && npm start
```

### Global CLI command

1. Build the project so `dist/cli.js` exists:
   ```bash
   npm run build
   ```
2. Link or install globally (either works):
   ```bash
   npm install -g .   # or: npm link
   ```
3. From any directory, run:
   ```bash
   agentui
   ```
   The TUI will start with that directory as its working directory.

Need a different prefix? Run:
```bash
npm run bin:set -- my-new-prefix
npm run build
npm install -g .
```
The script updates `package.json`'s `bin` entry so the next global install exposes the new command name.

## Environment

`.env` example:

```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5-mini # optional override
```

## Scripts

| Script | Description |
| --- | --- |
| `npm run dev` | Start the Ink TUI with live reload.
| `npm run build` | Type-check and emit JS into `dist/`.
| `npm start` | Run the compiled CLI from `dist/`.
| `npm run test` | Vitest test suite (config loader, session reducer, agent, mention utilities, composer renderer snapshots).
| `npm run lint` / `npm run lint:fix` | ESLint checks for `src/`.
| `npm run agent -- "prompt"` | Fire a single prompt without launching the TUI (see below).
| `npm run agent:smoke` | Runs six representative prompts (greeting, listing, summary, notebook creation, notebook summarize, patch+run) via the CLI for a quick end-to-end smoke test. Retries each prompt once if the model hiccups. |
| `npm run agent:testfs` | Filesystem regression harness (resets `tmp/fs-spec`, then exercises list/copy/read/glob/delete prompts against the real workspace). |
| `npm run bin:set -- <name>` | Update the global command prefix (default `agentui`). Re-run `npm run build` + `npm install -g .` afterwards. |
| `npm run test:agentui-bin` | Self-test for the global binary. Requires a fresh `npm run build`. |

### Inline CLI examples

This shares the same mention parsing/high-level behavior as the TUI and is useful for verifying filesystem features:

```bash
npm run agent -- "list the files in @src/"           # uses ls
npm run agent -- "show the first 5 lines of @README.md"  # uses read_file
npm run agent -- "search for 'FilesystemBackend' in @src/"  # uses grep
npm run agent -- "copy @README.md to README.backup"   # custom copy tool
npm run agent -- "delete @README.backup"               # custom delete tool
```

## Slash Commands (in the TUI)

- `/model [name]` – switch models (supported: gpt-5-mini, gpt-5, gpt-5.1, gpt-4o, gpt-4.1, o1, o1-preview, o1-mini). Run `/model` with no args to open the inline picker.
- `/new` – clear the transcript and reset usage.
- `/undo` – remove the last user/agent turn.
- `/files` – toggle the filesystem explorer panel.
- `/quit` or `/exit` – exit AgenTUI.

## CLI Tips

- Keep a second terminal running CLI prompts for iterative development. Example: `npm run agent -- "list the files in @tmp/"`.
- For filesystem-heavy changes, run `npm run agent:testfs` before and after edits to ensure list/copy/read/delete flows continue to work.
- `npm run agent:smoke` is useful after touching prompt routing or notebook behavior—it now exercises greeting, listing, notebook summarization, notebook creation, and a patch → run → artifact listing workflow. See [`docs/notebook-pipeline.md`](docs/notebook-pipeline.md) for the full create → patch → run → summarize → artifacts diagram.
- Want the TUI available as a global binary? Run `npm run build && npm install -g .`, then launch it anywhere via `agentui`. Use `npm run bin:set -- <prefix>` before linking if you want a different command name.

## Filesystem Shortcuts

The app intercepts natural language instructions before they reach the LLM. Every path travels through `src/path/resolver.ts`, which coerces `@mentions`, `~/`, `/examples/...`, or even accidental `/tmp/...` references back into the workspace sandbox before executing anything.

| Shell intent | Example prompts | AgenTUI handler |
| --- | --- | --- |
| List directory / `ls` | `list the files in @node_modules/` | `list_path` tool (shortcut + DeepAgents) |
| Read file / `cat`, `head` | `show the first 5 lines of @sprint4_specs.md` | `read_file` tool with byte limit |
| Search / `rg` | `search for "FilesystemBackend" in @src/` | `search_text` (wraps DeepAgents `grep`) |
| Copy / `cp` | `copy @README.md to @tmp/README.copy.md` | Shortcut + `copy_path` tool (handles directories + overwrite) |
| Move / `mv` | `move @tmp/README.copy.md to @tmp/README.archive.md` | Shortcut + `move_path` tool |
| Delete / `rm -rf` | `delete @tmp/README.archive.md` | Shortcut + `delete_path` |
| Make directories / `mkdir -p` | `mkdir @tmp/new_docs` | Shortcut + `make_directory` |
| Diff | `diff @README.md @ARCHITECTURE.md` | Shortcut + `diff_paths` |
| Notebook helpers | `run notebook @examples/notebooks/demo.ipynb` | Notebook tools (create/run/analyze) |
| Glob | `glob "*.test.ts" @src/` | DeepAgents glob tool |

Because these shortcuts run before the LLM sees your message, the agent never wastes tokens trying to reason about basic shell commands and you get deterministic output in both the TUI and `npm run agent -- "..."` mode.

## Reasoning → Actions → Answer Flow

Every turn goes through an intent router that attaches metadata to the prompt:

1. **[Intent] block** – describes whether the user is just chatting or asking for filesystem/notebook work. The agent reads this block before acting so small-talk gets a conversational answer while real tasks trigger planning.
2. **[Mentioned files] block** – lists sandbox-vetted paths derived from `@mentions`, so the model never guesses at arbitrary filesystem locations.

The DeepAgents runner streams structured events that both the CLI and TUI consume:

- `plan` events come from the agent’s `write_todos` planning tool or live reasoning tokens.
- `action` events normalize tool output into user-friendly summaries (e.g., `Listed / (23 entries)` instead of raw JSON).
- `reasoning_visibility` lets the model decide whether to display its plan. When `ReasoningVisible: no`, the UI/CLI hide the Reasoning block entirely; when `yes`, it renders in dim gray text without a heading.
- `answer` events ensure the final assistant turn summarizes exactly what happened, referencing the important actions.
- The router automatically escalates from conversation to filesystem/notebook/image tasks—even if the user simply replies “yes, do it”—so you never have to confirm twice.

The UI and CLI render these events as the familiar **Reasoning → Actions → Answer** sections, so verifying one surface automatically verifies the other.

## Project Structure

| Path | Description |
| --- | --- |
| `src/cli.tsx` | Ink entry point. Loads config, spins up the agent, renders the TUI, handles slash commands.
| `src/agent/` | `index.ts` constructs the LangChain deep agent (ChatOpenAI, filesystem backend, delete/copy tools) and exposes a typed runner. `index.test.ts` mocks the pieces to ensure correct wiring.
| `src/config/` | Zod-validated config loader plus tests. `config.ts` exports `loadConfig` used by both TUI and CLI.
| `src/state/` | Session reducer + hook for transcript, usage tracking, context meter.
| `src/ui/` | React components for App layout, footer/composer, file explorer, sidebar, transcript, etc. Includes mention highlighting + tests (`mentions.test.ts`).
| `src/fs/shortcuts.ts` | Natural-language parser that recognizes filesystem intents and calls DeepAgents tools before involving the LLM.
| `src/agent-cli.ts` | Single-shot CLI runner. Applies mention parsing + filesystem shortcuts and prints the agent response.
| `src/commands.ts` | Slash command parser + tests.
| `scripts/deepagents-model-test.ts` | Lightweight script for manually invoking a DeepAgent with arbitrary model/prompt (useful for debugging specific models or backends).

## QA Checklist

1. `npm run typecheck`
2. `npm run test`
3. Inline CLI smoke tests: run the examples above plus `npm run agent -- "hello"` and `npm run agent -- "create a notebook @examples/foo.ipynb"` to confirm the router flips between conversational and tool-driven flows, or use `npm run agent:smoke` to execute the default prompt set sequentially.
4. Filesystem regression: `npm run agent:testfs` to exercise list/copy/read/glob/delete flows against the real `tmp/fs-spec` fixture whenever filesystem changes are introduced.
5. Launch `npm run dev`, exercise slash commands (`/model`, `/new`, `/undo`, `/files`), and watch the dim-gray Reasoning block appear only when meaningful plan output exists.
6. Composer manual QA: with the TUI focused on the composer, paste a wall of text (≥8 lines), verify only 6 lines are visible with `⋮` glyphs above/below when clipped, and use arrow keys across wrapped lines to confirm the cursor never bleeds outside the border.
7. Global launcher: after `npm run build`, run `npm run test:agentui-bin` to confirm the `agentui` shim respects the invoking directory. Then `npm install -g .` (or `npm link`) and launch `agentui` from a throwaway directory to double-check manually.

## Notes

- Mentions resolve relative to the workspace root and the explorer keeps track of real filesystem changes.
- The default model can be overridden via `OPENAI_MODEL` if required. The known context windows are defined in `src/models.ts`.
