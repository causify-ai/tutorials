# Cleanup Sprint – Specs

## Objectives
1. **Composer/UI polish**
   - Eliminate the duplicate-key warning raised on initial render.
   - Add wrap-around navigation in the filesystem explorer (Up from first row jumps to last, Down from last jumps to first) similar to Codex’s tree.
   - Restyle system messages so they appear as a dedicated status line above the composer: green for success, yellow for info/warnings, red for errors (matches Codex screenshot).
2. **LangGraph / DeepAgents hygiene**
   - Suppress deprecation warnings by updating summarization middleware configs from `maxTokensBeforeSummary`/`messagesToKeep` to `trigger`/`keep` per LangChain docs (“Summarization middleware” + MCP note).
   - Integrate FilesystemBackend already wired with additional regression coverage: ensure file operation prompts (read/write/delete) work end-to-end.
3. **Agent correctness & tests**
   - Reproduce and fix the recursion-limit error shown when asking the agent to delete `summary.md`. Ensure the agent uses filesystem tools (ls/read/write/edit/grep) without runaway recursion.
   - Add unit/integration tests that simulate file operation prompts so regressions are caught early (mock DeepAgents runner).
4. **Docs & housekeeping**
   - Update sprint docs (sprint5 specs/plan) plus new cleanup docs describing behavior & verification steps.

## Reference Notes
- **LangChain docs**: MCP entry “File system access” and “Quickstart” for FilesystemBackend (already cited in sprint5); plus summarization middleware API (https://docs.langchain.com/oss/javascript/langgraph/summarization). Deprecation guidance: `maxTokensBeforeSummary -> trigger.tokens`, `messagesToKeep -> keep.messages`.
- **Codex/Gemini UI**: refer to `/Users/indro/Projects/codex/codex-rs/tui/src/bottom_pane/chat_composer.rs` for wrap-around navigation & system badge styling; Gemini CLI `packages/cli/src/ui/App.tsx` for explorer wrap behavior.
- **DeepAgents FS tools**: ensure ls/read_file/write_file/edit_file/glob/grep are accessible and that recursion limits (LangGraph `recursionLimit` default 25) are configurable via runner config if needed.

## Deliverables
1. **Key-warning fix** – identify duplicated key source and enforce stable unique keys.
2. **Explorer wrap-around** – arrow navigation loops.
3. **System message banner** – colored statuses shown above composer; all `addSystemMessage` calls updated to flag severity.
4. **LangGraph config update** – adopt new trigger/keep structure to remove warnings.
5. **Recursion limit fix** – adjust agent runner (e.g., `recursionLimit` bump) or guard to prevent infinite loops when executing file operations.
6. **File operation tests** – at least one test covering delete/write/read scenario using mocked agent runner + verifying mention metadata pipeline.
7. **Docs** – update sprint5 specs/plan & new cleanup docs summarizing state.

## Status
- ✅ Items 1–6 implemented (key warning resolved, explorer wrap-around, banner, LangGraph config updates, recursion-limit override, new mention/file tests).
- ⏳ Item 7 (docs) remains and will be handled before the cleanup sprint closes.
