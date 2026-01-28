# Cleanup 7 Plan – Deterministic Reasoning Visibility Streaming

Goal: prevent partial buffering from flashing into the Reasoning panel mid-stream. Reasoning should only render after the `ReasoningVisible: yes|no` flag is detected, with a single, cleaned flush, and stay hidden when the flag is absent or `no`.

Plan:
1. - [x] **Stream buffering change**
   - Add a `pendingReasoning` buffer to `streamAgentEvents` that collects model chunks until `ReasoningVisible` is resolved.
   - Once the flag appears, emit `reasoning_visibility`, flush a cleaned buffer as the first `plan` (if visible), then continue streaming normally; drop the buffer entirely when visibility is `no`.
2. - [x] **Fallback behavior**
   - Decide on a default if the stream ends without a visibility flag (default to hidden) and ensure no buffer flash occurs.
3. - [x] **UI placeholder + formatting**
   - Add a shimmer/working placeholder in the UI while visibility is unknown; suppress raw/JSON interim content in the reasoning panel.
   - Sanitize/format `write_todos` tool output before emitting `plan` events to avoid raw JSON flashing.
4. - [x] **Tests/notes**
   - Extend coverage for tool-sourced plans (write_todos) and ensure placeholders hide interim content.
   - Update STATE/README once the UI placeholder and plan formatting land.
