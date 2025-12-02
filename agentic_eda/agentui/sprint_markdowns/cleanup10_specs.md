# Cleanup 10 Specs – Autocomplete Cursor, 4o-mini Refinements, Vision Fallback

## Functional Requirements
1. **Mention autocomplete cursor**
   - When completing an `@` mention with tab/enter, the cursor moves to immediately after the inserted path so typing can continue; no cursor freeze.
2. **4o-mini response refinement**
   - 4o-mini responses match the established structure (reasoning/actions/answer), with clean summaries and no regression to GPT-5 output quality.
   - GPT-5 behavior remains unchanged.
3. **Vision fallback**
   - If the active model lacks vision, image analysis automatically uses a GPT-5-nano multimodal path (or a dedicated subagent) instead of the Pillow-based tool.
   - Maintain existing multimodal flow for vision-capable models; keep a safe fallback if vision fails.

## Testing Requirements
1. Unit/UI test for mention completion cursor position after tab/enter.
2. Verification run of `npm run agent -- "<suite of prompts>"` on 4o-mini; confirm structured responses and no formatting regressions.
3. Tests for vision fallback selection (model capability detection → GPT-5-nano multimodal call) and safe fallback to Pillow/tool.

## Documentation
1. Update `docs/STATE.md` (and README if helpful) with: mention autocomplete fix, 4o-mini tuning guidance, and vision fallback behavior/setup.
