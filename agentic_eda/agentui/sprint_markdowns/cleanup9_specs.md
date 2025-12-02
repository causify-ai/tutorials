# Cleanup 9 Specs – Stable Rendering & Input

## Functional Requirements
1. **Reasoning/answer hygiene**
   - Answers must never appear in the reasoning block; reasoning must not repeat the final answer (even for long streamed notebook/tool outputs or repeated captions).
   - No duplicate answer text in reasoning/actions; parsing must be resilient to interleaved chunks.
2. **TUI stability**
   - Transcript must not “spasm” (flicker, jump, jitter) during notebook/tool-heavy turns. Action rendering (including any animated states) must not cause layout thrash.
   - Streaming updates should render smoothly; no runaway rerenders from rapid plan/action updates.
3. **Composer cursor**
   - Cursor stays after the last typed character even under rapid typing; block formatting/mentions remain intact.
   - No regressions to composer sanitization or formatting features.

## Testing Requirements
1. Stream parsing tests covering notebook-length outputs and repeated captions to assert reasoning/answer separation.
2. UI/transcript rendering tests (e.g., ink testing) for a multi-event notebook scenario to ensure stable layout and no duplicated answer in reasoning.
3. Composer tests simulating rapid typing to verify cursor placement and preserved formatting.
4. Manual: `npm run agent -- "<notebook prompt>"` and similar to check for UI stability and clean sections.

## Documentation
1. Update STATE/README with the root causes found (reasoning bleed, UI spasm cause, composer cursor fix) and how to verify.
