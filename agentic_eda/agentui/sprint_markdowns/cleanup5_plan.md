# Cleanup 5 – Plan

1. **Action Summaries**
   - [ ] Design a parser that inspects DeepAgents tool events (name + input + output) and emits concise, natural-language summaries for the transcript.
   - [ ] Update `streamAgentEvents` to attach these summaries to `MessageAction.detail` so the CLI/TUI both render human-friendly actions (no raw JSON).
   - [ ] Cover filesystem tools (`ls`, `read_file`, `write_file`, etc.), notebook helpers, notebook analysis, todo updates, and provide a reasonable fallback for unknown tools.

2. **Path Highlighting**
   - [ ] Replace the current regex highlighter with a more robust path detector that:
       - Colors entire absolute/relative paths (including nested directories).
       - Highlights bare filenames that look like files (has a known extension) without requiring preceding punctuation.
       - Avoids false positives (e.g., random words that merely include a dot).
   - [ ] Consider reusing mention prefixes or workspace resolver heuristics if necessary for accuracy.

3. **Testing & Docs**
   - [ ] Update README/ARCHITECTURE (or cleanup5 specs) to describe the action summary behavior and improved path highlighting.
   - [ ] Extend the CLI smoke prompts (or add manual instructions) to verify: plain greeting (no reasoning/actions), filesystem listing (friendly actions + path colors), and notebook creation.
