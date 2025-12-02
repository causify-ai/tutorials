# Cleanup 10 Plan – Autocomplete Cursor, 4o-mini Refinements, Vision Fallback

Goal: fix mention autocomplete cursor placement, refine 4o-mini responses without regressing GPT-5 behavior, and make image analysis default to a GPT-5-nano multimodal path instead of the Pillow tool when the selected model lacks vision.

Plan:
1. - [ ] **Composer mention autocomplete**
   - Fix `@` mention completion (tab/enter) so the cursor moves to just after the inserted path, enabling immediate typing.
   - Add a targeted test for mention insertion + cursor position.
2. - [ ] **4o-mini response refinement**
   - Switch the model to 4o-mini for a full `npm run agent -- "<suite>"` check; adjust prompts/formatting so answers stay consistent with GPT-5 agents (no regressions in structure: reasoning/actions/answer separation, clean summaries).
   - Keep GPT-5 behavior intact; limit adjustments to model-specific config/formatting.
3. - [ ] **Vision fallback**
   - For image analysis, detect non-vision models and automatically use a GPT-5-nano multimodal call (or subagent) instead of the Pillow tool; keep a safe fallback path.
   - Ensure vision fallback integrates with the existing multimodal attachments pipeline; avoid breaking current GPT-5 vision behavior.
4. - [ ] **Tests & docs**
   - Add tests for mention autocomplete cursor, and for vision fallback selection logic.
   - Update STATE/README with the new defaults (4o-mini tuning, vision fallback) and verification steps.
