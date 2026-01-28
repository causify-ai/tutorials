# Cleanup 3 – Agent Reasoning & Response Quality

## Goals
- Build an agent that mirrors Codex/Gemini behavior: naturally converses when no tool use is needed and autonomously picks the right tools when users request actions.
- Ensure `npm run agent -- "..."` shows the same Reasoning / Actions / Answer structure as the TUI, reflecting the real behavior.
- Avoid brittle regex/patch fixes; instead align system prompts, tool metadata, and middleware with DeepAgents best practices so Reasoning/Actions/Answer come from structured events (not ad-hoc fallbacks).

## Requirements
1. **Prompt Routing / Context Awareness**  
   - Build a lightweight router (rule-driven first pass) inspired by Codex/Gemini flows that classifies prompts into conversational, filesystem, notebook, or mixed tasks.  
   - Use DeepAgents docs + Context7/Tavily research to ensure the router influences prompting (one-shot reply vs. tool plan) rather than ad-hoc “small talk” patches.  
   - Validate classification by running `npm run agent -- "hello"`, `-- "copy foo"`, `-- "create notebook"`, etc.

2. **Tool Planning & Reporting**  
   - Reference Gemini CLI and Codex behavior around plan/multi-step execution.  
   - Add plan/step summarization inside the agent output (Reasoning should read like Codex: Plan + step-by-step).  
   - Actions should summarize the user-facing description (“Moved xyz → abc”), not raw JSON.  
   - Emit a structured event schema (plan updates + tool status updates) so CLI/TUI consume the same Reasoning/Actions stream.

3. **Streaming & Final Answer**  
   - TUI and CLI show live reasoning sourced from plan/todo updates plus tool events, identical across surfaces.  
   - Update the system prompt/middleware so the final assistant message always summarizes completed actions; only synthesize an Answer from actions if the model fails to produce one due to an error.  
   - Errors (recursion limit, etc.) must retain the action trail so users can see what already happened.

4. **Testing Matrix**  
   - Smoke tests via `npm run agent -- "..."` for: greetings, simple file ops, notebook creation, mixed tasks.  
   - Document expected outputs and behavior so future agents know how the conversation should look.
