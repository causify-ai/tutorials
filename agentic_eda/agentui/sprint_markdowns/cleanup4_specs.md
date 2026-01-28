# Cleanup 4 – Reasoning UX & Router Escalation

## Goals
- Give the agent fine-grained control over whether its internal reasoning is shown to the user, mirroring Codex/Gemini behavior (reasoning hidden for chit-chat, visible for complex/tool runs).
- Ensure routing transitions from conversational to tool-driven autonomously when the user makes an actionable request (for any tool in the arsenal: filesystem, notebook, vision, etc.)—no extra confirmation loops.
- Keep the CLI and TUI perfectly in sync with the new structured event metadata, including color/formatting tweaks.

## Requirements
1. **Reasoning Visibility Metadata**
   - Extend `streamAgentEvents` to produce a `show_reasoning` boolean sourced from the model (e.g., via a simple `ReasoningVisible: yes/no` marker or a lightweight schema). The default should be “false” for trivial replies and true for tool-heavy/multi-step work.
   - System prompt/middleware must instruct the model: “Only stream Reasoning when it provides value (multi-step planning, tool orchestration, non-trivial troubleshooting). Hide it for greetings/thanks/simple answers.”
   - CLI/TUI must render Reasoning only when `show_reasoning` is true; when hidden, no blank sections. When shown, render the plan text in dim gray with no “Reasoning:” heading.
   - Tests/screenshots demonstrating: (a) “hello” (Reasoning hidden), (b) “list the files in @src/” (Reasoning shown, gray text), (c) notebook command (Reasoning shown).

2. **Automatic Router Escalation**
   - Router should escalate from `conversation` to the relevant tool intent whenever the user issues a follow-up command that clearly requires tools (“yes list them”, “run the notebook now”, “open the image”). This applies across every tool we expose (filesystem, notebook, image).
   - Implement stateful detection: track the last user/agent exchange that asked for confirmation; if the next turn is affirmative (regex on “yes/please/do it/run it/create it”), immediately reroute and execute the pending plan.
   - Update prompt instructions so the LLM knows it may autonomously proceed when the router signals a tool intent even if the previous turn was conversational.
   - Document heuristics + fallback (if ambiguous, agent can still ask) but default should be automatic.

3. **Streaming & CLI/TUI Parity**
   - Structured events must include the new `show_reasoning` flag and any additional metadata required for routing context.
   - CLI formatting: Reasoning body only (dim gray), “Actions” and “Answer” remain unchanged; hide Reasoning entirely when the flag is false.
   - TUI formatting: same as CLI; ensure spacing collapses when reasoning is hidden.

4. **QA & Documentation**
   - Update README/ARCHITECTURE sections describing the Reasoning UX and routing behavior.
   - Manual QA checklist: `npm run agent -- "hello"`, `npm run agent -- "list the files in @src/"`, `npm run agent -- "create a notebook @examples/foo.ipynb"`, and a “yes list them” follow-up (watch auto escalation), plus TUI screenshots showing both hidden and visible Reasoning states.
