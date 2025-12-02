# AgenTUI Sprint 5 – Specs

## 1. Focus Areas
1. **Mention workflow (`@filename`)** – Provide Codex/Gemini-style inline mentions so users can quickly reference files in chat prompts.
2. **DeepAgents filesystem capabilities** – Wire up the harness “File system access” tool suite (ls/read_file/write_file/edit_file/glob/grep).
3. **Persistent local FS backend** – Give the agent durable access to the working directory using LangChain Deep Agents’ FilesystemBackend quickstart.

## 2. Reference Insights & Research
- **Codex mention UX**: The Rust composer tests at `codex-rs/tui/src/bottom_pane/chat_composer.rs:2488-2532` show how `/mention` inserts `@` tokens and ensures Tab/Enter behavior never submits the message, mirroring the mention picker. Their slash popup (`codex-rs/tui/src/bottom_pane/snapshots/...slash_popup...snap`) highlights the active option and inserts a trailing space so the cursor lands after the completed token.
- **Gemini CLI**: Composer UX (multi-line navigation, dropdown alignment) already mirrored; we’ll extend the same renderer to host a second popup for mentions (just like Codex attaches an `@` menu under the text area).
- **DeepAgents harness docs**: LangChain MCP entry “File system access” (`https://docs.langchain.com/oss/javascript/deepagents/harness`) confirms the built-in tools and expectations for ls/read_file/write_file/edit_file/glob/grep plus the pluggable backend design.
- **Local persistence quickstart**: LangChain MCP doc “Quickstart” (`https://docs.langchain.com/oss/javascript/deepagents/backends`) outlines using `new FilesystemBackend({ rootDir: ".", virtualMode: true })` to persist files on disk (instead of the default ephemeral state backend). We will follow that pattern so AgenTUI’s agent can work inside the repo.

## 3. Feature Requirements

### 3.1 Mentioning Files with `@`
- Typing `@` in the composer should open a file suggestion popup (positioned under the composer border like existing slash hints).
- Suggestions list should include the same files that the explorer exposes (cwd root, respecting visibility/filtering). Filtering rules:
  - When the user types `@src/ui`, the menu narrows to matching descendants (`src/ui/App.tsx`, etc.).
  - Multi-level paths support `/` characters; treat whitespace or punctuation as terminators (Codex behavior).
- Navigation:
  - Arrow keys cycle options.
  - `Tab` inserts the highlighted file token as `@relative/path.ext ` (note the trailing space) and leaves the cursor after the space; text should be colorized (e.g., cyan) to distinguish mention tokens, matching Codex’ highlighted `@` segments.
  - `Enter` confirms the selection but **does not** send the chat; it simply inserts the mention token and closes the popup.
  - `Esc` closes the popup without inserting anything.
  - Backspacing to a bare `@` reopens the chooser (just like slash behavior).
- Composer should support multiple mentions per message and keep slash commands working separately. Mention tokens must serialize into the message payload unchanged (`@path` text) so the agent downstream can parse it.
- Tests: UI unit tests verifying filtering, insertion, trailing space, cursor placement, and that `Enter` doesn’t dispatch send.

### 3.2 DeepAgents File System Tools
- Upgrade `createAgentRunner` so `createDeepAgent` receives a filesystem backend exposing the six harness tools (`ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`) documented in LangChain’s “File system access” section.
- Ensure tool descriptions reflect the doc summary in the system prompt or metadata so the agent knows it can use them.
- Confirm the tools operate relative to the AgenTUI workspace root (process.cwd()) and respect sandboxing (no escaping outside unless explicitly configured).
- Add logging/telemetry so we can tell when the agent executes these tools (useful for debugging mentions).

### 3.3 Local Filesystem Persistence
- Switch from the default in-memory state backend to `FilesystemBackend` with `rootDir = process.cwd()` and `virtualMode = true` (per LangChain “Quickstart” guidance) so agent-created artifacts persist on disk.
- Document the new behavior in README/spec notes: users must trust AgenTUI with local file writes.
- Provide a configuration escape hatch (environment flag) to disable persistence if needed.

### 3.4 End-to-End Mention Flow
- Users should be able to type something like: `Summarize @src/ui/App.tsx into NOTES.md`.
- Agent resolves mention text to a path, uses harness tools (`read_file`, `write_file`), and produces/updates `NOTES.md` in the workspace.
- Provide a demo command or scripted test that exercises mention → read → markdown write.

## 4. Deliverables
1. Mention popup implementation + composer highlighting/tests.
2. Refactored agent runner with filesystem backend + tool surfacing (ls/read/edit/glob/grep).
3. Configuration/README updates documenting local persistence + mention syntax.
4. Regression tests (unit + integration stub) proving the agent can read a mentioned file and write a summary markdown.

## 5. Risks / Open Questions
- Need to ensure mention parsing doesn’t conflict with `@` characters in code snippets; may require escaping (Codex history uses `@@` to type literal `@` if necessary).
- Filesystem backend must be carefully sandboxed—`virtualMode` should prevent path traversal but we need to verify.
- Mention autocomplete could be heavy for huge workspaces; may need caching/virtualization similar to the explorer.
- Agent reliability: summarizing large files might hit context limits; we should lean on context meter to warn users.

## 6. Current Status
- Mention popup, colored highlighting, and mention metadata pipeline are live (see `src/ui/App.tsx` + `src/ui/mentions.ts`).
- Agent now runs with `FilesystemBackend` + recursion-limit bump (default 100) to keep file ops stable.
- Outstanding work: docs/README updates and end-to-end QA notes (tracked in cleanup sprint).
