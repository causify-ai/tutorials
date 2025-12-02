# Fix Model Switching – Findings & Next Steps

## Observed Issue
- `/model` accepted any of our catalog values, yet the backend still replied as `gpt-4.1-mini`. DeepAgents/ChatOpenAI never threw. Users had no way to know the switch silently failed.

## Fixes Implemented
1. **Response instrumentation**
   - `createAgentRunner` now captures `finalMessage.response_metadata.model|model_name` and returns it in the `AgentResult`.
   - The UI stores this as the *effective* model. If OpenAI replies with a different model than requested we surface a ⚠️ system notice and update the session widgets to the actual model.

2. **Availability gating before switching**
   - `applyModel` now calls `ensureModelAvailable`, which hits `GET https://api.openai.com/v1/models/{id}` using the user’s API key (referencing LangChain docs on `response_metadata` to ensure these ids are authoritative).
   - If the API says `model_not_found` or permission denied, we refuse the switch, keep the menu open, and show the server’s error text.
   - Successful lookups are cached for the current run so repeat switches don’t re-hit the network.

3. **State alignment**
   - Session + splash cards render the effective model (what OpenAI actually used), preventing stale UI hints.
   - Context window + undo calculations now piggyback on the effective model, so token math matches the backend.
   - We no longer emit ⚠️ system messages on every turn; the resolved model still updates UI state, but the transcript remains clean.

## Remaining Follow-ups
1. **SDK parity:** we still need to verify DeepAgents/@langchain/openai versions once OpenAI makes the GPT‑5 family generally available. For now we’re limited by what the `/models` endpoint exposes to our key.
2. **Automated tests:** add regression tests in `src/agent/index.test.ts` (mock `ChatOpenAI`) and a CLI integration test to ensure `/model` rebuilds the runner + respects availability rejections.
3. **User-facing warning enhancements:** consider persisting the “requested vs. effective” mismatch in the sidebar or explorer status so users have a permanent indicator without scrolling the transcript.

With instrumentation + gating in place, any unsupported model request now fails fast with a clear error, and successful switches reflect the authoritative model returned by OpenAI.
