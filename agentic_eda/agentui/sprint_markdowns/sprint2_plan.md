# AgenTUI Sprint 2 Plan

## Objective
Give users Codex-parity awareness (context remaining) and powerful slash commands for quick control over sessions/models.

## Workstreams & Tasks

### 1. Context Remaining Indicator
- [x] Capture token usage + model window from LangChain/OpenAI responses (store in session state).
- [x] Implement percent calculation utility (baseline 12k tokens, clamp 0–100, color thresholds) with unit tests.
- [x] Render indicator in footer (always visible, red ≤10%) and reset when `/new` or model switches.

### 2. Slash Command System
- [x] Build slash command parser + dispatcher (`/model`, `/new`, `/undo`, `/quit`, `/exit`).
- [x] `/model`: list/select LangGraph-documented OpenAI models; update config + agent runner, confirm in header.
- [x] `/new`: clear transcript, usage stats, context meter.
- [x] `/undo`: remove last user+agent turn and adjust usage meter; handle no-op states gracefully.
- [x] `/quit` & `/exit`: graceful shutdown (same path as Ctrl+C).
- [x] Unit tests for parser + reducer effects.

### 3. UX & Docs
- [x] Add hints/tooltips describing slash commands + context meter to README and in-app footer.
- [x] Update sprint plan/specs and manual QA checklist for new flows (model swap, undo, new chat).

### 4. Composer UX Parity
- [ ] Mirror Codex/Gemini display-line math (`codex-rs/tui/src/public_widgets/composer_input.rs`, `gemini-cli/packages/cli/src/ui/components/shared/text-buffer.ts`) so wrapped lines track per-column widths.
- [ ] Preserve sticky visual column when navigating up/down across wrapped rows; ensure arithmetic factors in prompt padding/borders.
- [ ] Render inverse caret on newline/blank cells and keep newline insertion (Ctrl+J) distinct from Enter submission.
- [ ] QA checklist for cursor alignment (fast typing, blank lines, slash-menu interaction) and document known edge cases.

## Acceptance Criteria
1. Footer always shows accurate `NN% context left` (verified via mocked token usage tests) and updates after each turn.
2. Slash commands execute immediately without sending prompts to the agent; `/model` supports both inline arg + interactive picker.
3. `/new` and `/undo` leave the CLI in a consistent state (input cleared, usage recalculated).
4. Composer matches Codex/Gemini ergonomics: caret never disappears, up/down stay in-column, width calculations match the rendered box.
5. README + specs capture slash/context + composer behaviors; plan reflects progress.
