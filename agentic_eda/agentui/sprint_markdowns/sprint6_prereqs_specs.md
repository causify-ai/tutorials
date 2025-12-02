# Sprint 6 Prereqs – Specifications

## 1. Objectives
- Deliver a **battle-tested path resolution layer** so every tool invocation (DeepAgents filesystem helpers, notebook runner, mention metadata, CLI shortcuts) uses sandbox-safe absolute paths. No command may leak `/examples/...` literals to DeepAgents anymore.
- Ensure the agent can reliably execute **every file-oriented shell command** the Codex/Gemini CLIs automate (copy, move, remove, mkdir, list, diff, grep/search, open, chmod, etc.) inside the workspace sandbox. Users should be able to type natural-language requests or shell-equivalent prompts and see the correct action happen.
- Validate everything via `npm run agent -- "..."` smoke scripts plus Vitest/unit coverage before resuming Sprint 6 proper.

## 2. Research Summary
- **Gemini CLI operational coverage** (`gemini-cli/docs/cli/commands.md`, `docs/tools/mcp-server.md`): beyond slash commands, their MCP filesystem harness covers listing directories, globbing, copying, moving, deleting, patching files, running editors, diffing, and searching with `ripgrep`. The CLI ensures every request is scoped via a resolver that rewrites user paths relative to the sandbox before invoking MCP tools.
- **Codex CLI** (`codex/docs/slash_commands.md`, `codex-rs/core/src/seatbelt.rs`, `codex-rs/tui/.../chat_composer.rs`): same sandbox rules but the agent frequently receives shell-style requests (“copy src/lib.rs to src/lib.old.rs”) and Codex rewrites them using a centralized resolver plus command parser in Rust.
- AgenTUI currently normalizes mentions and notebook code, yet filesystem tools (copy/delete/move) still see raw `/examples/...` and the DeepAgents backend blocks destructive operations. We need a full parity resolver + shell-command bridge so the agent can run any file manipulation without hitting the virtual-mode guard.

## 3. Path-Handling Requirements
1. **Central resolver module** (TS) that:
   - Accepts a workspace root + user provided string and returns `{ absolutePath, displayPath, isDir, reason }`.
   - Auto-detects `@mentions`, `~/`, `./`, `../`, Windows drive letters, and bare `/examples/...`.
   - Keeps trailing slash semantics (directories) as Codex/Gemini do.
2. **Tool adaptors**:
   - Wrap every DeepAgents filesystem tool with resolver before `backend.call`.
   - Update CLI shortcuts + slash handlers to consume resolver results (shared lib, no duplication).
   - Notebook runner already rewrites code cells; extend to also rewrite metadata for summary outputs.
3. **Safety + diagnostics**:
   - Return friendly system messages when resolution fails (no more backend errors).
   - Log canonical + display path for auditing (mirrors `codex-rs/core/src/safety.rs`).
4. **Testing matrix**:
   - Unit tests for resolver (Vitest) covering all path styles + error branches.
   - Integration tests via `npm run agent -- "copy @path ..."` for each filesystem capability (list, read, write, delete, move, diff, search) using new CLI harness.

## 4. Shell Command Coverage Requirements
- **Target command set:** replicate Codex/Gemini coverage for file operations: `ls`, `tree`, `cat`, `head`/`tail`, `open`, `cp`, `mv`, `rm`, `mkdir`, `rmdir`, `touch`, `chmod` (or equivalent), `diff`, `rg`/`grep`, search/replace, `apply_patch`, archiving/unarchiving, and notebook helpers (create/run/summarize). Where a direct shell call is risky, provide a dedicated tool (e.g., `copy_file`, `move_file`, `delete_path`, `list_tree`).
- **Natural language translation:** ensure the DeepAgent can interpret prompts like “duplicate @src/index.ts as @src/index.backup.ts” by feeding it the normalized paths + tool schema instructions.
- **Safety:** destructive commands must confirm target root ownership and honor workspace-only rules similar to Codex’ seatbelt (`codex-rs/core/src/seatbelt.rs`). Provide clear errors for attempts outside workspace.
- **Documentation:** capture a table of supported file operations vs. their AgenTUI handler in README.

## 5. Deliverables Before Sprint 6
1. **Resolver package** under `src/path/` with exported API + hooks for UI + tools.
2. **Shell-command capability matrix** describing every supported filesystem action and the tool/function implementing it.
3. **Tests & scripts**:
   - `npm run agent -- "..."` scenarios for copy/move/delete/mkdir/list/diff/search/read/write/open plus notebook smoke tests.
   - Vitest suites for resolver + command dispatcher.
4. **Docs**: Updated README/ARCHITECTURE with resolver overview, shell-command mapping, testing workflow, and these prereq markdowns.

Meeting these specs ensures AgenTUI’s sandbox + command behaviors match Codex/Gemini expectations before resuming the original Sprint 6 roadmap.
