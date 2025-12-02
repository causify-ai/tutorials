# AgenTUI Sprint 1 – Product & Technical Specs

## 1. Vision & Context
- Build a terminal-first chat experience that visually mirrors the Codex CLI (full-screen view, magenta accent, cyan status cues, dimmed metadata).
- Power the chat with LangChain deep agents so user prompts go through an AI “agent brain” capable of light tool use.
- Target audience: engineers who already use Codex-like CLIs and want a lightweight agent they can run locally with their own OpenAI key.

## 2. Goals (Sprint 1)
1. Ship a runnable CLI (Node 20+, TypeScript) that renders a Codex-inspired chat layout via Ink.
2. Wire the input form to a LangChain deep agent (using `createDeepAgent` from `deepagents`, per LangChain docs) backed by OpenAI’s responses API via `@langchain/openai`.
3. Support at least one system prompt preset ("General Helper") and show both user + assistant turns in the transcript window.
4. Provide an `.env`-based configuration for `OPENAI_API_KEY` and a `config.ts` shim for future providers.

## 3. Non-goals
- No persistence layer or logging backend in Sprint 1.
- No tool-calling beyond the built-in reasoning (basic Q&A only).
- No sandbox execution of shell commands.
- No theming/skin customization yet.

## 4. User Stories
- **As a developer**, I can install dependencies (`npm install`) and run `npm start` to launch a Codex-style chat terminal.
- **As a user**, I see a header bar with session metadata, a scrollable transcript, and a footer input box reminiscent of Codex.
- **As a user**, when I ask a simple question ("What is LangChain?"), the agent returns an OpenAI-backed answer and the transcript updates in place.
- **As an operator**, I can set my OpenAI key via `.env` or shell env vars without touching code.

## 5. Experience & Layout Notes
- Adopt Codex color guidance (`bold` headers, `dim` secondary text, cyan status, magenta brands) even though we are using Ink instead of Ratatui.
- Layout sections:
  1. **Header** – session title, model name, connection indicator (cyan when healthy).
  2. **Transcript** – scrollable vertical flex list; each turn gets a left gutter label (`You`, `Agent`) and magenta accent bars similar to Codex.
  3. **Sidebar (optional collapsed)** – Sprint 1 shows a minimal stats column (token usage placeholder) on wider terminals; hides on <90 cols.
  4. **Footer** – multiline input prompt with instructions line (dim) and status line (pending/streaming states).
- Support dark/light terminals by limiting color palette (default fg, cyan, magenta, green, red) following `codex-rs/tui/styles.md`.

## 6. Architecture Overview
```
AgenTUI (bin)
 ├─ src/cli.ts         → bootstraps Ink render + CTRL+C handling
 ├─ src/ui/App.tsx     → top-level Ink component managing panes & theme
 │   ├─ Header
 │   ├─ Transcript (list of MessageBubble components)
 │   ├─ Sidebar (token stats)
 │   └─ Footer (InputComposer + StatusBar)
 ├─ src/agent/index.ts → LangChain deep agent factory via `createDeepAgent`
 │   └─ src/agent/openai.ts handles `ChatOpenAI` wiring & env validation
 ├─ src/state/session.ts → zustand-like store or simple reducer for messages
 └─ src/config.ts      → loads env, ensures OPENAI_API_KEY exists
```
- Use Ink’s hooks (`useInput`, `useApp`, `useStdout`) for keyboard/resize handling.
- Manage async agent calls with `useReducer` + `EventEmitter` to keep UI responsive.

## 7. Agent Implementation Details
- Import `createDeepAgent` from `deepagents` (per LangChain docs retrieved via Context7).
- Provide a very small toolset (none in Sprint 1; rely on basic reasoning) but leave hook for future `tool[]` injection.
- Use `ChatOpenAI` model `gpt-4o-mini` (configurable) via `@langchain/openai`.
- Pipeline:
  1. User submits text.
  2. Session store records pending turn and sets status `"thinking"`.
  3. Agent invoked with `messages` array (LangChain Roles) built from transcript.
  4. On resolution, append assistant content; on error, surface toast in footer (red) and keep transcript unchanged except error stub.
- Stream handling left for Sprint 2 (Sprint 1 uses one-shot `invoke`).

## 8. Configuration & Dev Ex
- Dotenv for local dev; CLI warns if `OPENAI_API_KEY` missing.
- Provide `npm scripts`: `dev` (ts-node/tsx), `build` (tsc), `start` (node dist/index.js).
- Use `tsx` for zero-config TS execution during Sprint 1.
- lint/format: `eslint` + `prettier` for `src/**/*.{ts,tsx}`.

## 9. Testing Strategy
- Unit tests for `session` reducer logic (Vitest).
- Mock agent module to verify UI dispatch? (Optional for Sprint 1; focus on reducer + config validation.)
- Manual UX QA: instructions in README for running with sample key.

## 10. Risks & Mitigations
| Risk | Mitigation |
| --- | --- |
| Ink flexbox differences vs Ratatui layout | Build with snapshot strings via `ink-testing-library` to lock layout quickly. |
| LangChain deep agent dependency instability | Pin `langchain`, `deepagents`, `@langchain/openai` versions known to work (per docs). |
| Rate limits / API failures | Provide clear footer status + instructions to retry; wrap agent call with exponential backoff util. |

## 11. Future Enhancements (Post Sprint 1)
- Streaming + typing animation.
- Tool calling (filesystem/context, Tavily search) once base agent stable.
- Persist conversations to JSONL.
- Expand layout to include file tree + approvals similar to Codex.

