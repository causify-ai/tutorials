# Cleanup 8 Specs – Structured Responses & TUI Rendering

## Functional Requirements
1. **Structured rendering**
   - Reasoning is rendered only in the grey reasoning block (hidden when absent/trivial), actions remain the concise green list, and answers render in their own section every time a final reply is produced.
   - Noise such as “Update:”/status lines stays in reasoning, never duplicated in actions or answers; actions should only list actual tool effects.
2. **Clean final answers**
   - For non-tooling conversations, respond with a direct answer instead of placeholder text like “All set. Let me know what you need next.”
   - When tools are used, the final answer must summarize results clearly without leaking tool chatter or intermediate “update” lines.
3. **Prompt/route consistency**
   - Routing/prompting must enforce a consistent structured payload (reasoning/actions/answer) with no reliance on overrides or manual post-hoc patching.
   - Tool-less turns must not emit action sections; tool-using turns must not omit the answer section.

## Testing Requirements
1. Add renderer/transcript tests that feed representative event streams (conversation-only, tool runs, mixed) and assert the resulting layout keeps reasoning/actions/answers in their correct sections/colors.
2. Include regression coverage for the “Update:” noise scenario (codex-clipboard-gcJG4f.png) to ensure updates stay in reasoning and actions remain concise.
3. Provide guided manual checks using `npm run agent -- "prompt"` (e.g., simple Q&A, directory list, mixed reasoning) to validate the live TUI output; document expected screens.

## Documentation
1. Update `docs/STATE.md` (and README if helpful) to describe the cleaned rendering rules, the proper fallback for non-tool replies, and how to run the automated/manual checks.

## Non-Functional
1. Solution must be robust (no brittle string hacks or one-off overrides); keep existing behavior stable elsewhere.
2. Preserve current API/event contracts; confine changes to prompting/routing/renderer logic and related tests.
