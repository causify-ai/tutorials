# AgenTUI Sprint 2 – Specs

## 1. Focus Areas
1. **Context Remaining Indicator** – Mimic Codex’s “x% context left” counter so users always see how much window remains.
2. **Slash Command System** – Add `/model`, `/new`, `/undo`, `/quit`, `/exit` commands to the composer for low-friction configuration and session management.
3. **Composer UX Parity** – Recreate Codex/Gemini composer ergonomics (caret placement, multiline wrapping, keybindings) so typing feels identical to the reference TUIs.

## 2. Reference Insights
- **Codex Context Indicator**
  - `codex-rs/tui/src/bottom_pane/footer.rs` renders `context_window_line(percent)` in the footer at all times.
  - Percent value flows from streaming token usage events: `chatwidget.rs:set_token_info` receives `TokenUsageInfo` with `model_context_window`, computes `percent_of_context_window_remaining` (see `protocol/src/protocol.rs`), and calls `bottom_pane.set_context_window_percent` so the footer redraws.
  - `TokenUsageInfo.percent_of_context_window_remaining` subtracts a `BASELINE_TOKENS = 12000` buffer before calculating `(remaining/effective)*100`, ensuring the UI starts at 100% after the first prompt and trends toward 0%. (Source: `protocol/src/protocol.rs:802-844`).
  - **Takeaway for AgenTUI:** track per-turn token usage from LangChain / OpenAI responses, keep latest model context window (per LangGraph docs), compute percent = `max(0, 100 - (used/effective)*100)` with similar baseline, display in footer even during typing.
- **Model selection via LangGraph**
  - Context7 LangGraph docs (https://docs.langchain.com/oss/javascript/langgraph/use-graph-api) show runtime-configurable model providers by passing `configurable` options to `StateGraph.invoke`. Example includes OpenAI models like `gpt-4o-mini`, `o1-preview`. We can mirror this by keeping a list of OpenAI-friendly IDs exposed by LangChain/Graph runtime and switching `ChatOpenAI` instantiation.
- **Composer behavior (Codex + Gemini)**
  - Codex implementation lives in `/Users/indro/Projects/codex/codex-rs/tui/src/public_widgets/composer_input.rs`: it tracks a virtual buffer with sticky visual columns, tokenizes graphemes, and keeps newline cursors visible by rendering an inverted space on blank lines. Up/down navigation uses wrapped line metadata rather than logical line offsets.
  - Gemini’s equivalent is `/Users/indro/Projects/gemini-cli/packages/cli/src/ui/components/shared/text-buffer.ts` + `InputPrompt.tsx`. Their `TextBuffer` computes `visualLines`, `visualCursor`, and exposes methods like `buffer.move('up')` that preserve column positions even when lines wrap or contain double-width characters. Ctrl+J inserts a newline, Enter submits unless Shift/Ctrl modifiers intervene, and Tab/Ctrl keys integrate with slash menus.
  - **Takeaway for AgenTUI:** composer width must match the painted box (prompt + padding), caret rendering must accommodate newline slots, and vertical navigation must stick to the captured visual column (no diagonal drift). Slash logic remains as-is but the underlying buffer must expose APIs similar to Gemini’s `TextBuffer`.

## 3. Feature Requirements
### Context Remaining Indicator
- Collect token usage & model window data
  - On every agent turn completion, capture the usage metadata from LangChain’s `LLMResult` (`response_usage` fields) or OpenAI tool output.
  - Keep running totals similar to Codex’s `TokenUsageInfo` so we can compute percent remaining even mid-session.
  - Support optional override if OpenAI returns `usage.prompt_tokens`/`completion_tokens`.
- Calculation
  - Introduce `BASELINE_TOKENS = 12000` (same as Codex) and compute `effective_window = modelWindow - baseline` (clamp >=0), `used = totalTokens - baseline`, `percent = ((effective-used)/effective)*100` clamped 0-100, round to nearest integer.
  - Model window value defaults to OpenAI metadata (LangChain `response.response_metadata.model_context_window` when available) or fallback to known defaults per model alias.
- UI Placement
  - Footer should always show `NN% context left` right-aligned next to composer hints, even while typing (mirroring Codex `footer.rs` behavior).
  - When percent is `None`, hide indicator; when ≤10% use red accent to warn.
  - Add future hook for tooltip/hint when context low.

### Slash Commands
Implement parser + executor triggered when user input starts with `/`. Validate commands case-insensitive.
1. `/model`
   - Show popover/list of supported OpenAI models (initial list: `gpt-4o-mini`, `gpt-4o`, `o1-preview`, `o1-mini`, `gpt-4.1`, extendable via config).
   - Pull names from LangGraph docs (Context7 snippet) to justify available choices.
   - Selecting a model updates config + agent runner; confirm in header + context indicator resets.
2. `/new`
   - Reset session state: clear transcript, token usage, context percent, resets `thread_id` (once persistence exists) and focus composer.
3. `/undo`
   - Remove last message pair (user + agent) and revert token usage counters accordingly. If agent is mid-turn, cancel request.
4. `/quit` & `/exit`
   - Gracefully exit CLI (equivalent to Ctrl+C). Accept either command.

Interaction rules:
- Slash commands should not be sent to the agent.
- Provide optimistic feedback (toast line or status bubble) confirming command success or errors (e.g., unknown model alias).
- If user hits `/model` with no args, show selection overlay; selection overlay should show valid models for langgrapg agents; `/model gpt-4o` should immediately apply.
- Autocomplete/backfill command list when typing? (stretch) Provide at least inline hint text.

## 4. Deliverables
1. Context indicator logic shared between agent runner + UI with tests verifying percent math & color threshold.
2. Slash command parser module + UI integration (composer, overlays) + reducer tests.
3. Updated README & sprint docs explaining new commands and context gauge.

## 5. Risks / Questions
- Need reliable token usage from OpenAI Responses API; verify LangChain deep agent exposes usage or add manual tracking via message lengths.
- Undo must coordinate with LangChain deep agent state; determine whether to re-run agent or just pop from transcript.
- Handling `/model` while request running: must queue change to apply next turn.
### Composer UX Parity
- Maintain a buffer helper mirroring Codex/Gemini logic:
  - Track `displayLines`/`visualLines` with cumulative column widths for each wrap segment.
  - Store a sticky column so repeated up/down presses stay aligned even through wraps.
  - Render the caret with an inverse space when the cursor sits on newline/empty cells so it never disappears (matches Codex screenshot behavior).
- Keybindings (reference Gemini `InputPrompt.tsx`):
  - `Enter` submits unless slash menu active; `Ctrl+J` inserts newline; Shift+Enter intentionally disabled per user request.
  - Arrow keys move freely outside slash suggestion focus; when slash popup is active we defer to suggestion navigation.
- Layout rules:
  - Compute composer width as terminal columns minus prompt prefix + padding + borders (currently subtract 8 cols); keep this calculation in sync with the actual `Box` layout so wrap calculations remain accurate.
  - Slash suggestion list continues to render below the bordered composer mirroring Codex/Gemini.
- QA targets:
  - Typing rapidly keeps the cursor at the tail (no “second-to-last character” insertion).
  - Up/down from any wrapped row lands on the expected character (compare to Codex composer screenshots).
  - Blank lines show the inverted caret and newlines render correctly when inserted via `/new` or Ctrl+J.
