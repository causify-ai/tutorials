# Cleanup 5 – Action Summaries & Path Highlighting

## Goals
- Replace the raw JSON “Actions Taken” output with natural, human-readable summaries across CLI and TUI.
- Improve file/path highlighting so entire paths (absolute, relative, extension-only names) are colored without triggering on unrelated words.

## Requirements
1. **Action Summaries**
   - Build a `describeToolAction` helper that understands DeepAgents filesystem tools (`list_path`, `read_file`, `write_file`, `append_file`, `copy_path`, `move_path`, `delete_path`, `make_directory`, `glob_path`), todo planning (`write_todos`), notebook helpers (`ipynb_create`, `ipynb_run`, `ipynb_analyze`), and any aliases emitted by the agent (`ls`, `cat`, etc.).
   - Use tool inputs/outputs to produce short descriptions such as “Listed / (23 entries)” or “Read README.md (first 4000 chars)”.
   - Hook the helper into `streamAgentEvents` so `MessageAction.detail` always contains a natural-language sentence; CLI/TUI should simply render the detail (no JSON fallback). Provide a generic fallback (“Completed tool_name (…summary…)”) for unknown tools.

2. **Path Highlighting**
   - Update the text renderer to detect whole paths:
     - Absolute (`/foo/bar/baz.ts`, `~/src/app.ts`), relative (`./foo`, `../bar`), mention (`@src/index.ts`).
     - Bare filenames ending with common extensions (`.md`, `.ts`, `.tsx`, `.js`, `.json`, `.py`, `.ipynb`, `.yaml`, `.yml`, `.sh`, `.txt`, etc.).
   - Highlight the entire path/filename (not just fragments) and avoid false positives (e.g., “e.g.” should not be colored). Consider validating patterns (must contain slash or recognized extension) before coloring.

3. **Testing & Docs**
   - Update README/ARCHITECTURE (or relevant docs) to mention the natural-language action summaries and refined path highlighting.
   - Extend manual QA / smoke prompts (e.g., `npm run agent:smoke`) to confirm:
     - Greeting (no reasoning/actions).
     - Filesystem listing shows friendly action text and correctly colored filenames.
     - Notebook creation summarises actions properly.
