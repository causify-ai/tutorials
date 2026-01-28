# Cleanup 3 – Plan

1. **Research & Prompt Alignment**  
   - [ ] Review `/Users/indro/Projects/gemini-cli` or `/Users/indro/Projects/codex` and search up docs (context7/tavily) for agent planning patterns.  
   - [ ] Update system prompt/tool descriptions to emphasize conversations first, tools second, and require the final assistant turn to summarize completed actions so UIs don’t need to invent answers.

2. **Agent Middleware Improvements**  
   - [ ] Add router/decision module that selects conversational vs. tool-driven flows and integrate into both CLI/TUI.  
   - [ ] Normalize tool-stream events (Reasoning plan updates + Action status summaries) so UI/CLI receive the same structured payloads.

3. **Streaming UI/CLI Parity**  
   - [ ] Ensure Reasoning/Actions/Answer appear in CLI exactly as in TUI using the structured event schema.  
   - [ ] Teach the model (via prompt + middleware) to always emit a final conversational summary; only synthesize fallback answers when runs terminate early due to errors.

4. **Testing**  
   - [ ] Run `npm run agent -- "hello"`, `"list .md files"`, `"create notebook ..."`, etc.  
   - [ ] Validate the TUI visually with screenshots if needed.

5. **Docs & Scripts**  
   - [ ] Update README/ARCHITECTURE with new behavior expectations.  
   - [ ] Add script/log describing how to verify agent conversational flow.
