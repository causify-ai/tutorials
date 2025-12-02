# Cleanup 4 – Plan

1. **Reasoning UX / Structured Events**
   - [ ] Extend the agent’s structured event schema with a `show_reasoning` flag emitted by the model (default true for complex plans, false for trivial replies).
   - [ ] Update the CLI/TUI renderers to respect the flag: hide the Reasoning section when the flag is false, and render it in dim gray text (no “Reasoning:” heading) when true.
   - [ ] Adjust the base system prompt/middleware guidance so the model itself decides when Reasoning should be visible (e.g., only for multi-step/tool work).

2. **Automatic Tool Routing Escalation**
   - [ ] Replace the “ask for confirmation before switching from conversation → tool use” behavior with an automatic escalation policy: if the user’s words clearly request any supported tool operation (filesystem, notebook, etc.), the router emits a higher-intent classification and immediately executes the necessary tools.
   - [ ] Research best practices from DeepAgents/Codex for dynamic re-routing mid-conversation and document the heuristics (keywords, follow-up signal, mention detection).
   - [ ] Update the router + middleware to reclassify turns when the user explicitly repeats a toolable request (“yes list them”, “run the notebook”, “create it now”) and ensure the agent’s response reflects the new intent without prompting again.

3. **Streaming Parity & Testing**
   - [ ] Verify the new Reasoning visibility flag flows through `streamAgentEvents`, CLI, and TUI.
   - [ ] Add regression tests (unit + manual) for: greetings (Reasoning hidden), a filesystem task, a notebook command, and auto-escalation after a confirmation turn.
   - [ ] Capture screenshots/logs demonstrating both hidden + visible Reasoning behavior.

4. **Docs & Oversight**
   - [ ] Draft cleanup4 specs describing the decision matrix (when to hide reasoning, routing escalation rules, required prompts/tool metadata).
   - [ ] Update README/ARCHITECTURE after implementation to keep the Reasoning UX and routing behavior discoverable.
