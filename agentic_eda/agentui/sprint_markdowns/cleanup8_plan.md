# Cleanup 8 Plan – Response Rendering & Answer Cleanliness

Goal: clean up the agent’s structured output so reasoning stays in the grey reasoning block, actions remain the concise green list, and answers are properly rendered without noisy “Update:” preambles or placeholder replies (see codex-clipboard-gcJG4f.png).

Plan:
1. - [ ] **Response shaping**
   - Trace the LLM → event stream → renderer pipeline and normalize structured outputs so “Update:”/status chatter is kept inside the reasoning block, not duplicated in actions or answers.
   - Strip redundant prefixes and merge consecutive reasoning notes to prevent wall-of-text spam.
2. - [ ] **Answer rendering correctness**
   - Ensure the TUI always shows a dedicated answer section even when tools are used; reasoning stays grey/italics, actions stay green as-is, with no mixing of sections.
   - Fix the “All set. Let me know what you need next.” fallback so non-tool questions (e.g., counts, small facts) receive real answers.
3. - [ ] **LLM prompt/route adjustments**
   - Tighten prompt/route guidance so structured messages (reasoning/actions/answer) are emitted consistently, with noise captured as reasoning and no ad-hoc overrides/patch fixes.
   - Add safeguards so tool-less conversations do not emit action blocks unless tools actually ran.
4. - [ ] **Tests and regression harness**
   - Add a test suite that validates the rendered transcript (reasoning/actions/answer colors/sections) given representative event streams.
   - Include guided `npm run agent -- "prompt"` scenarios to verify the cleaned output in the real TUI, plus snapshot coverage where feasible.
5. - [ ] **Docs/STATE refresh**
   - Record the cleanup scope and verification commands in `docs/STATE.md` (and README if needed) so future contributors know how to validate the rendering.
