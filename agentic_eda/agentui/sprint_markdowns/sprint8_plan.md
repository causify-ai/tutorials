# Sprint 8 Plan – Multimodal Image Analysis & Response Hygiene

Goal: ship real multimodal image understanding via LangChain DeepAgents (images passed directly to the model) while cleaning remaining reasoning/answer bleed-through and action accuracy issues.

Plan:
1. - [x] **Multimodal research + API wiring**
   - Verify DeepAgents/LangChain chat call shape for multimodal inputs (image_url/base64 parts) and which fields the runner exposes for tool-less image analysis.
   - Design how image blobs/paths flow from the TUI mention resolver into the agent runner without brittle overrides; prefer native multimodal messages over ad-hoc analyze_image tool calls.
2. - [ ] **Image routing & prompting**
   - Detect image requests (mentions of .png/.jpg or “what do you see”) and attach the image to the LLM call; fall back to analyze_image tool when the model lacks vision.
   - Update prompts so reasoning stays concise and the final answer summarizes findings (objects/scenes/text) instead of metadata-only captions.
3. - [ ] **Response hygiene fixes**
   - Eliminate answer text leaking into reasoning for all event paths; ensure actions reflect real outcomes (e.g., non-zero entries for listings).
   - Normalize streaming plan/answer parsing so repeated captions or updates don’t duplicate in reasoning/answer.
4. - [ ] **Tests & regressions**
   - Add automated coverage for reasoning/answer separation, action summaries (listing counts), and multimodal payload handling (mock vision model inputs).
   - Run `npm run agent -- "What do you see in @image"` against a sample image to validate TUI rendering and vision output quality.
5. - [ ] **Docs & handoff**
   - Update STATE/README with multimodal setup steps, verification commands, and any model requirements/flags for image support.
