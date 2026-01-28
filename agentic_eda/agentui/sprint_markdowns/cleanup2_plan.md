# Cleanup Sprint 2 – Plan

## Tasks
1. **Inline CLI command**
   - [ ] Add a script (e.g. `npm run agent -- "prompt"`) that loads config, builds the agent runner, parses mentions, and prints the response once.
   - [ ] Support `/model` style overrides via flags/env if needed.
2. **Mention dropdown polish**
   - [ ] Remove leading `@` from option labels and show only relative paths.
   - [ ] Rank suggestions by depth + alpha (shallow matches first).
   - [ ] Ensure filtering matches tokens containing `@scope` segments.
3. **Harness tool bugfixes**
   - [ ] Investigate why `ls/read_file/glob/grep` return “empty” results and fix path normalization or tool invocation.
   - [ ] Add fallback logic for large directories (e.g. limit ls output but still return real data).
4. **Path highlighting**
   - [ ] Confirm new cyan-highlighting covers both user + agent responses (adjust regex if needed).
5. **Deterministic tests**
   - [ ] Create scripted integration tests (or snapshots) invoking each tool via the inline command (mock FS if necessary).
   - [ ] Document exact commands to run tests.

## Order
1. Inline CLI command (enables deterministic testing).
2. Mention dropdown + normalization tweaks.
3. Harness bugfixes (ls/read/write/edit/glob/grep).
4. Tests + documentation/examples.
