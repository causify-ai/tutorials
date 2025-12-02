# Sprint 5 – Plan

## Trackers
- [ ] **P0** Mention picker UX parity
- [ ] **P1** DeepAgents filesystem tools
- [ ] **P1** Local persistence + mention-to-summary demo

## Actionable Steps
1. **Study mention UX & data sources**
   - [x] Review Codex mention handling (`codex-rs/tui/src/bottom_pane/chat_composer.rs`) and Gemini composer to confirm cursor/Tab semantics.
   - [x] Inventory workspace files (reuse explorer tree service) and define filtering rules for `@` prefixes.
2. **Implement composer mention mode**
   - [x] Extend composer state machine to detect `@` tokens, render a suggestions panel (same anchor as slash menu), and keep slash logic untouched.
   - [x] Support navigation (↑/↓/Tab/Enter/Esc) plus colored mention tokens in the textarea. Ensure Enter inserts without sending, Tab inserts and keeps caret after trailing space, Esc cancels.
   - [x] Unit tests for filtering, insertion, and cursor placement.
3. **Connect mentions to agent context**
   - [x] Map inserted `@path` tokens to absolute paths before dispatching messages.
   - [x] Add lightweight resolver so the agent prompt can include structured metadata (e.g., “User referenced file: …”) to encourage tool usage.
4. **Enable DeepAgents filesystem harness**
   - [x] Instantiate `FilesystemBackend` (per LangChain DeepAgents “File system access” / “Quickstart” docs) rooted at `process.cwd()` with `virtualMode: true`.
   - [x] Confirm ls/read_file/write_file/edit_file/glob/grep tools appear in the agent harness; add logging/telemetry.
   - [x] Allow opt-out via config/env flag; document prerequisites.
5. **Local persistence + mention demo**
   - [x] Script an integration test (or CLI recipe) where the user mentions a file and the agent produces a markdown summary via `write_file`.
   - [ ] Update README/specs to describe mention syntax, FS tools, and safety considerations.

## Validation
- [ ] `npm run typecheck && npm run test` stay green.
- [ ] Manual scenario: mention `@src/ui/App.tsx`, ask for a summary, verify the agent reads the file and writes `Summary.md`.
- [ ] Document new capabilities in sprint logs.
