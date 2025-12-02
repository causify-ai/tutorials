# Cleanup 9 Plan – Stable Rendering, Reasoning Hygiene, Composer Cursor

Goal: eliminate reasoning/answer bleed, stop TUI spasms during long/async tool runs (especially notebooks), and fix composer cursor drift under fast typing without regressing formatting features.

Plan:
1. - [x] **Reasoning/answer separation (root fix)**
   - Trace the full stream path (DeepAgents stream → streamAgentEvents → App transcript assembly) to ensure answers never enter the reasoning buffer; normalize content before buffering and strip duplicates at the stream layer, not ad-hoc.
   - Add regression coverage for long notebook outputs and repeated captions so reasoning and answer stay disjoint.
2. - [ ] **TUI stability under notebook/tool load**
   - Reproduce the “spasming” during notebook-heavy turns; profile render/update cadence and action rendering (including animated “…”) to find the root cause (e.g., rapid action updates, plan churn, or width recalcs).
   - Harden render scheduling (debounce/batch if needed), tame action updates, and ensure layout isn’t thrashing during tool streams.
   - Add a regression test or recorded scenario to keep the UI stable while streaming notebook/tool events.
3. - [ ] **Composer cursor drift fix**
   - Reproduce fast-typing cursor misplacement; inspect composer input state, string-width handling, and sanitize pipeline.
   - Fix cursor tracking without breaking block formatting/mentions; add targeted tests for rapid typing and multi-line/block formatting.
4. - [ ] **Verification**
   - Run `npm run agent -- "notebook + listing + read"` style prompts to confirm no spasm and clean reasoning/actions/answers.
   - Add/extend automated tests for stream parsing, transcript rendering, and composer cursor behavior.
