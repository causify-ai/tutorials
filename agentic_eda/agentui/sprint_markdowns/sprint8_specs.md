# Sprint 8 Specs – Multimodal Vision & Response Cleanup

## Functional Requirements
1. **Multimodal vision path**
   - When a prompt references an image (e.g., `@foo.png`, `.jpg`, “what do you see”), pass the image directly to the LLM using the LangChain/DeepAgents multimodal API (base64 or URL parts) instead of text-only captions.
   - Detect and gracefully fall back to the `analyze_image` tool only if the selected model lacks vision; avoid redundant tool + LLM passes.
   - Responses must include useful scene/object/text descriptions, not just dominant color/metadata, and avoid repeating the same caption in reasoning/answer.
2. **Response hygiene**
   - Reasoning must never contain the final answer text; answers must not include plan/update chatter.
   - Actions must accurately reflect tool outcomes (e.g., listing counts >0 when entries exist).
   - Streaming parsing should de-duplicate repeated plan/answer snippets.
3. **TUI/CLI rendering**
   - Ensure reasoning stays in the grey block, actions in green, answers in the answer section for multimodal turns and standard turns.

## Testing Requirements
1. Unit/fixture tests for multimodal payload construction (image attachments into the chat request) and fallback selection when the model is non-vision.
2. Stream parsing tests that assert answers never leak into reasoning (including multimodal captions), and that listing actions show correct counts.
3. Snapshot/renderer tests for transcript layout on a multimodal turn (reasoning/actions/answer separation).
4. Manual checks: `npm run agent -- "What do you see in @path/to/sample.jpg"` with a known image; confirm rich description and clean sections.

## Documentation
1. Update `docs/STATE.md` (and README if helpful) with: required model flags for vision, how images are attached, fallback behavior, and verification commands.

## Non-Functional
1. No brittle overrides/patches; integrate through the existing runner/prompt pipeline.
2. Preserve existing APIs; confine changes to routing, runner multimodal wiring, stream parsing, and rendering.
