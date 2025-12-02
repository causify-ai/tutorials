# AgenTUI Sprint 1 Plan

## Sprint Objective
Deliver a runnable AgenTUI prototype that mirrors Codex’s chat look-and-feel and answers basic questions via a LangChain deep agent backed by OpenAI.

## Work Streams & Tasks

### 1. Project Scaffolding & Tooling
- [x] Initialize npm workspace with TypeScript, tsconfig, eslint/prettier, and tsx runner.
- [x] Add dotenv-based config loader with runtime validation + helpful error copy.
- [x] Document setup (`README` stub, env instructions) inside AgenTUI.

### 2. LangChain Deep Agent Integration
- [x] Install and pin `langchain`, `deepagents`, and `@langchain/openai`.
- [x] Implement `src/agent/index.ts` factory wrapping `createDeepAgent` (Context7 docs) with our system prompt + OpenAI model selection.
- [x] Write minimal unit test or smoke script to confirm agent answers "What is LangChain?" when `OPENAI_API_KEY` is set.

### 3. TUI Shell (Ink)
- [x] Create Ink App skeleton with Header, Transcript, Sidebar, Footer components.
- [x] Apply Codex-inspired styling (bold headers, cyan status, magenta accents, dim metadata) per `codex-rs/tui/styles.md`.
- [x] Implement transcript state + reducer to append turns and show pending spinner/state.
- [x] Wire footer input to dispatch agent calls, show pending statuses.

### 4. QA & Polish
- [x] Add Vitest coverage for session reducer + config guardrails.
- [x] Provide manual QA checklist in README (launch, ask sample question, error path w/out API key).
- [ ] Review Sprint goals, mark tasks complete, and prep demo script.

## Dependencies & Assumptions
- Node.js ≥ 20, npm available (Rust not required, per user constraint).
- User supplies `OPENAI_API_KEY`.
- Terminal supports ANSI colors + >= 100 columns for full layout (app should degrade gracefully).

## Acceptance Criteria
1. Running `npm start` renders Codex-style UI with header, transcript, footer, sidebar (auto-hides on narrow width).
2. Entering a prompt triggers a LangChain deep agent call and displays the assistant’s reply.
3. Missing API key results in a clear, non-crashing error message.
4. Specs + plan remain in repo for reference; README documents setup.

## Out of Scope (Sprint 1)
- Streaming tokens, tool calling, conversation persistence, packaging for npm/pip.
