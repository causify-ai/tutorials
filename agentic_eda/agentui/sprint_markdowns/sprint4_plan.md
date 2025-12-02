# AgenTUI Sprint 4 Plan

## Objective
Introduce a Codex-style filesystem explorer panel with keyboard navigation and live updates, keeping the composer workflow intact.

## Workstreams & Tasks

### 1. Filesystem Panel Foundation
- [ ] Build tree builder utility (read cwd recursively, sort folders/files, limit depth if needed).
- [ ] Render left-hand panel with full-height border, indentation, and scroll support (per wireframe).
- [ ] Wire panel into App layout alongside chat/Sidebar, ensuring final layout matches the provided mock: explorer left, splash centered top, session widget right, composer bottom.

### 2. Navigation & Shortcuts
- [ ] Add global Ctrl+F toggle that hands focus to the panel (and back to composer on toggle/ESC).
- [ ] Implement `/files` slash command to show/hide the explorer (when hidden, layout collapses to the original view).
- [ ] Implement selection movement + expand/collapse behavior (Enter on folder toggles children, Enter on file runs `open`/`xdg-open`).
- [ ] Handle nested directories gracefully (indentation, horizontal truncation when needed).

### 3. Dynamic Updates
- [ ] Watch cwd (fs.watch + fallback polling) and refresh tree when files/folders change (agent-created files should appear).
- [ ] Provide manual refresh fallback (e.g., `r` inside panel) in case watch fails.

### 4. Docs & QA
- [ ] Update README/specs with controls (Shift+F, Enter behavior).
- [ ] Extend QA checklist (deep nesting, file open, agent-generated files).

## Acceptance Criteria
1. Layout mirrors the provided wireframe when explorer visible; when `/files` hides it, layout reverts to previous chat+sidebar arrangement.
2. Panel spans full height on the left, showing cwd tree with indentation and live updates.
3. Ctrl+F toggles focus; composer retains typed text when panel active.
4. `/files` toggles show/hide without breaking other widgets.
5. Enter on folder expands/collapses; Enter on file launches default app.
6. Panel reflects new files within a short interval after creation.
7. Documentation updated to describe the new UI/shortcuts.

## Status Snapshot
- Filesystem panel + slash command `/files` completed (docs updated).
- Explorer virtualization keeps selection centered; large folders no longer jump the viewport.
- Ctrl+F + `/files` interactions verified (auto-show on focus, composer regains focus when hidden).
- Remaining TODOs (if revisiting): optional scroll hints, persistence of expanded state, manual refresh command once watchers are added.
