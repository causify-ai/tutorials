# Sprint 7 – Input Composer Responsiveness & Formatting

## 1. Goals
1. **Typing responsiveness** – eliminate the “double key overwrites first key” symptom when typing quickly in the composer. Root-cause via MCP docs and lower-level ink/TextInput behavior.
2. **Multiline formatting** – make the composer gracefully handle walls of text (pasted or typed), expanding vertically up to a sensible height and then enabling an internal scroll region so the surrounding layout remains stable.

## 2. Problem Statements
- **Issue 1 (keystroke overwrite):** Users typing two letters quickly see the second character overwrite the first. Hypothesis: debounce/render lag between Ink `<TextInput>` updates and our local state sync; we need to trace the input lifecycle using MCP docs and instrumentation.
- **Issue 2 (line wrapping):** The composer currently stays single-line and lets long lines overflow horizontally, producing unreadable gutters. We need a controlled multi-line input with vertical growth capped to a threshold (e.g., 6 lines) and an internal scroll view for additional content.

## 3. Requirements
### 3.1 Typing Responsiveness
- Reproduce using a small diagnostic harness (e.g., log timestamps for `onChange` vs. `onSubmit`).
- Consult MCP/Ink docs to confirm recommended input buffering strategies.
- Fix must work in both TUI and CLI (Ink) contexts.
- Add regression test or at least a manual reproduction checklist.

### 3.2 Multiline Composer UX
- Composer should expand line-height up to a configurable limit (e.g., 6 visible rows).
- Once the limit is reached, enable vertical scrolling within the composer rather than pushing the whole UI.
- Maintain existing keyboard shortcuts (⌘+Enter send, Ctrl+C exit, etc.).
- Pastes with odd spacing should retain formatting without forcing horizontal scrolling.

## 4. Non-goals
- We are not redesigning the entire TUI layout; only the composer input box.
- No changes to message rendering or transcript history in this sprint.

## 5. Deliverables
- Updated composer component with verified fast-typing fix and scrollable multiline behavior.
- Documentation snippet in README or docs/STATE describing the new composer behavior.
- Tests/manual checklist covering rapid typing and multi-line paste scenarios.
