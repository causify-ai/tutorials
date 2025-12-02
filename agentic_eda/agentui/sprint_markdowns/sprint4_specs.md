# AgenTUI Sprint 4 – Specs

## 1. Focus Areas
1. **Filesystem Explorer Panel** – Persistent left-hand panel spanning the full height of the TUI showing the current working directory tree (think IDE explorer).
2. **Navigation & Actions** – Keyboard shortcuts (Shift+F toggle, Enter on folder/file) for browsing and opening items, with dynamic updates when files/folders change.
3. **Layout Alignment** – Match the provided wireframe: folder widget on far left, AEDA splash centered top, session details widget on the right, input prompt spanning the bottom (folder panel always visible).

## 2. Reference Insights & Best Practices
- **IDE/TUI explorers** (VS Code, Codex IDE panel) show a vertically stacked tree with indentation per depth, highlight the active entry, and support collapsing/expanding folders. Use indentation/chevrons (`▸`, `▾`) for clarity. Codex inspiration: `/Users/indro/Projects/codex/codex-rs/tui/src/sidebar` (file tree widgets) and Gemini explorer components if applicable.
- **Best practices** (Tavily search): treat nested folders as trees where each node can be expanded without collapsing siblings (avoid “compact folders” pitfalls); ensure names remain readable, and use monospace alignment for clarity.
- **Terminal UX**: ensure arrow keys or `j/k` navigate, but per requirement we’ll keep primary navigation Enter + current cursor (likely still using `useInput`).

## 3. Feature Requirements
### Filesystem Explorer Panel
- Render on the left side (fixed width) from top to bottom, always visible, matching the wireframe (full-height column).
- Shows root as the cwd; directories appear with folder icon/chevron; files as plain rows with indentation.
- Panel updates when filesystem changes (e.g., after agent creates/deletes files). Use `fs.watch` or polling to refresh tree.
- Support deep nesting gracefully: indentation but consider horizontal scrolling/truncation for long names.

### Navigation & Shortcuts
- `Ctrl+F` toggles focus to the filesystem panel (i.e., composer loses focus, panel receives keyboard events). Toggle again or ESC to return to composer. Layout remains consistent: explorer left, splash center top, session widget right, composer bottom.
- `/files` slash command toggles showing/hiding the files widget; when hidden the layout collapses back to the previous chat+sidebar view.
- Within panel:
  - Arrow keys / `j/k` move selection (consistent with other navigation metaphor), but at minimum ensure Enter acts on the highlighted item.
  - Enter on folder toggles expand/collapse to show children.
  - Enter on file opens the file with the OS default (use `open` on macOS or `xdg-open` on Linux; Windows `start`).
- Panel should scroll if more items than vertical space.

### Dynamic Updates
- Detect new/removed files (e.g., watch the cwd). When agent writes new files, they appear automatically.
- Provide minimal feedback if watch fails (e.g., on unsupported platforms).

## 4. Deliverables
1. Filesystem panel component with tree rendering + keyboard navigation.
2. Global input routing: Shift+F toggle, composer focus regained when panel closed.
3. File open action (platform-aware `spawn`).
4. Tests covering tree builder (sorting, indentation) + input reducer.
5. README/spec updates describing new controls.

## 5. Risks / Questions
- `fs.watch` reliability across OSes—may need polling fallback.
- How to handle extremely large directories (maybe limit depth or require manual refresh?).
- Security: launching files via default app should be opt-in; confirm with user if needed.

## 6. Current Status / Next Steps
- `/files` slash command implemented; toggles explorer visibility and posts system hints.
- Ctrl+F focuses the explorer (auto-shows it if hidden); explorer highlights only when focused.
- Virtualized explorer view keeps the selection centered even for large directories (node_modules) so navigation stays in-context.
- Remaining polish ideas: add scroll indicators, remember last expanded state across `/files` toggles.
