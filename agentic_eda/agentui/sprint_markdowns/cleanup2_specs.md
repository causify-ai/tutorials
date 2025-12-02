# Cleanup Sprint 2 – File Operations & Inline Commands

## Goals
1. **Inline command execution**: Add a CLI command (Codex-style) that allows running direct agent instructions without launching the full TUI. This enables deterministic testing of file actions via `npm run agent -- "list files in src"` (exact interface tbd but string arg required).
2. **Harness tool correctness**: Ensure the deep agent can successfully use all built-in filesystem tools (`ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`) plus our custom `copy_file` and `delete_file`. Prompts like “list files in @node_modules/…” should enumerate the actual directory, not claim empty results.
3. **Mention UX fixes**: The mention picker should prioritize shallow matches (e.g. `@src`) and visually show plain relative paths (no leading `@` repeated). Filtering should prefer top-level matches before deep ones.
4. **Transcript highlighting**: Mentioned file paths should be cyan in both user and agent bubbles (already partially done; verify completeness).
5. **Deterministic testing**: Provide scripted tests or CLI recipes to verify each harness tool, so regressions are caught without manual chat sessions.

## Requirements & Constraints
- Inline command interface can reuse LangChain Deep Agents directly; follow Codex’s approach (docs/context7) where `codex "prompt"` invokes the agent once and prints the response.
- Mention dropdown should rank paths by depth/shortness and avoid redundant prefixing (only show `src/…` once).
- When the agent receives paths via mentions, replace `@` tokens with absolute paths before calling DeepAgents so tool prompts have valid inputs (already implemented, but confirm for inline mode).
- Provide example CLI commands for each harness tool (ls/read/write/edit/glob/grep/copy/delete), ensuring they succeed against real files.

## Deliverables
1. `cleanup2_plan.md`
2. Inline command entry point (likely `npm run agent -- "…"`) that supports mention syntax.
3. Fixes to mention suggestions and harness prompts so `ls`, `read_file`, etc. work correctly.
4. Automated tests or scripts exercising all filesystem tools.
5. Documentation snippet describing how to run the inline command and the sample file operations.
