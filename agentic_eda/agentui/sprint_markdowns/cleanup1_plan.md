# Cleanup Sprint – Plan

## Tasks
1. **Composer/system UI**
   - [x] Locate and fix duplicate key warning (likely MentionSuggestions or message lines); add regression test if feasible.
   - [x] Implement wrap-around navigation in FileExplorer (Up from idx 0 → last, Down from last → 0).
   - [x] Introduce system status banner:
     - Maintain a queue of recent system messages.
     - Render above composer with color coding (success/info/warn/error).
     - Update `addSystemMessage` API to accept severity.
2. **LangGraph/DeepAgents config**
   - [x] Update DeepAgents middleware configuration to use `trigger`/`keep` options, removing deprecation warnings.
   - [x] Allow recursion limit override (config/env) to prevent errors when executing file operations; set default >25 per screenshot.
3. **File operations & tests**
   - [x] Ensure agent invocation includes mention metadata and that FilesystemBackend is used for tool calls.
   - [x] Write integration-style tests for file operations (mock agent runner to verify requested actions for delete/read/write).
   - [x] Verify failure surfaces produce red system messages.
4. **Docs**
   - [ ] Update sprint5 specs/plan with new behavior (mentions, FS backend, warnings).
   - [ ] Document cleanup sprint status + testing instructions.

## Execution Order
1. Fix key warning + add explorer wrap-around (small UI changes, unblock rest).
2. Add system message banner (touches composer & state).
3. Update DeepAgents config + recursion limit.
4. Implement tests & regression fix for file operations.
5. Update documentation.
