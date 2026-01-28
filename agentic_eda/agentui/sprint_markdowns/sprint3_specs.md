# AgenTUI Sprint 3 – Specs

## 1. Focus Areas
1. **Thinking-State Composer UX** – Allow users to keep typing while the agent is running, but block submission until the pending turn completes.
2. **Startup Status Panel** – Show an ASCII info box (“splash”) on launch that mirrors Codex’s banner (renamed to AEDA) so users immediately see version, model, and cwd.

## 2. Reference Insights
- **Gemini CLI composer** (`/Users/indro/Projects/gemini-cli/packages/cli/src/ui/components/InputPrompt.tsx` + `shared/text-buffer.ts`)
  - Buffer remains editable during tool/agent execution; only the submit handler is gated by `props.isInputActive`/`disableSubmit`. We should mimic this split (editable buffer + submit guard).
- **Codex CLI composer** (`/Users/indro/Projects/codex/codex-rs/tui/src/public_widgets/composer_input.rs` & `bottom_pane/mod.rs`)
  - `ChatComposer::handle_key_event` always mutates its buffer; `AppState` ignores `InputResult::Submitted` when the agent is busy and surfaces a system line (“Agent is working…”). Use the same approach in AgenTUI.
- **Codex startup box** (`/Users/indro/Projects/codex/codex-rs/tui/src/app.rs`, render helpers in `tui/src/render/mod.rs`)
  - On mount, Codex draws an ASCII banner with product version, active model, and cwd (`~/path`). Borders use `╭─╮` glyphs and the brand color. Replicate structure but swap text for AEDA.

## 3. Feature Requirements
### Thinking-State Composer UX
- **Typing allowed**: `ComposerInput` stays focused during `state.status === 'thinking'`; keystrokes update internal buffer and slash suggestion logic.
- **Submission blocked**: Enter (or slash command execution) should no-op with a visual hint (“Agent is finishing previous turn…”). Slash commands that mutate state (e.g., `/model`) should queue/reject with a system toast rather than running mid-turn.
- **Post-completion behavior**: Once the agent returns, whatever text the user typed remains in the composer and can be submitted immediately.

### Startup Status Panel
- Render on first paint (before any conversation) an ASCII box:
  ```
  ╭────────────────────────────╮
  │ >_ AEDA (v0.0.1)          │
  │                           │
  │ model:     gpt-4o-mini    │
  │ directory: ~/Projects/... │
  ╰────────────────────────────╯
  ```
  - Model line ends with ` /model to change` (per requirement).
  - Directory uses `~` shorthand; auto-truncate if wider than terminal.
- Splash disappears once the first user/system message is added (so transcript occupies the space).
- Remove the existing top header panel (`┌ AgenTUI … Ready … model ┐`); the sidebar/session widget already shows the same data, so after the splash renders we should no longer draw that redundant header.

## 4. Deliverables
1. Updated composer reducer/hooks + tests covering “typing while thinking” and “submit blocked when busy”.
2. ASCII splash component wired into `App` with dynamic data (version constant, current model, cwd).
3. README + sprint docs updated with behavior notes + QA checklist.

## 5. Risks / Questions
- Need to ensure agent cancellation/undo doesn’t conflict with queued text.
- Splash must handle very narrow terminals gracefully (maybe collapse to single column).
- Confirm version string source (e.g., `package.json` vs hardcoded) before shipping.
