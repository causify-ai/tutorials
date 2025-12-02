# Cleanup 7 Specs – Deterministic Reasoning Visibility Streaming

## Functional Requirements
1. **Deferred rendering until visibility known**
   - While `ReasoningVisible: yes|no` is not yet parsed, buffer all reasoning chunks and do not emit `plan` events.
   - When the flag arrives, emit `reasoning_visibility` and, if visible, flush the cleaned buffer as the first plan update; if not visible, drop the buffer and never emit reasoning.
2. **No double rendering / flashing**
   - Ensure buffered text never appears before the flag is resolved, even if reasoning arrives earlier than the flag in the stream, or both arrive in one chunk.
3. **Missing-flag fallback**
   - If a stream ends without any `ReasoningVisible` marker, default to hiding reasoning (no plan emitted).

## Testing Requirements
1. Add unit tests around `streamAgentEvents` to cover:
   - Flag and reasoning in the same chunk.
   - Reasoning chunks before the flag (buffered, then flushed once the flag appears).
   - No flag present (no plan events emitted).
2. Assert emitted plan text has the flag stripped and is only emitted after visibility is known.

## Documentation
1. Update `docs/STATE.md` and/or `README.md` to note the visibility-gated rendering and the default suppression when the flag is missing.

## Non-Functional
1. Preserve existing API surface and event kinds; only adjust streaming internals.
2. Keep runtime behavior stable under concurrent tool events; buffering must not block action updates.
