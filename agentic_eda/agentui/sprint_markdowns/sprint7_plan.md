# Sprint 7 Plan – Composer Responsiveness & Formatting

- [x] **Diagnostics**
  - [x] Instrument the composer to capture keystroke timing (measure `onChange` vs. render) and reproduce the overwrite bug.
  - [x] Review MCP/Ink docs (TextInput, raw-mode handlers) for best practices on buffering input.
- [x] **Deterministic Renderer/Test Harness**
  - [x] Extract a pure `renderComposerView(value, cursor, width)` helper that returns an ASCII representation of the viewport (lines, clipped flags).
  - [x] Write Vitest-style snapshots covering: wall-of-text paste, stray pipes, repeated `UP`/`DOWN` commands, etc.
- [x] **Composer Scroll & Layout Fix**
  - [x] Fix cursor-tracking when scrolling up/down (ensure caret remains visible, no border encroachment).
  - [x] Prevent characters from extending outside the left/right borders (pad/measure using string width).
  - [x] Validate that arrow navigation works on every wrapped line (esp. those without a left border marker).
- [ ] **QA & Docs**
  - [x] Update README/STATE once the deterministic renderer + final composer patch lands.
  - [x] Record manual QA steps (paste, arrow navigation).
  - [ ] Re-run `npm run agent:smoke`.
