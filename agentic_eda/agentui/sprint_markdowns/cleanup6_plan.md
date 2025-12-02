# Cleanup 6 Plan – Global `agentui` Launcher

## Goal
Allow developers to type a single `agentui` command inside **any** workspace directory and have the TUI start with that directory as its working directory. The prefix (`agentui`) must remain configurable so it can be renamed later without touching the code paths again.

## Approach
1. - [x] **Executable entrypoint**
   - Ship a tiny executable (Node or shell wrapper) that lives in `bin/agentui` (or similar) and re-exports our current CLI start (`tsx src/cli.tsx` / built binary).
   - Ensure the wrapper forwards STDIN/STDOUT and arguments to the existing CLI and keeps the cwd inherited from where the command was invoked.
2. - [x] **Configurable command prefix**
   - Track the preferred command name in repo config (e.g., package.json `bin` map, plus a `.env` override or `AGENTUI_PREFIX` env var) so it can be swapped to something else later.
   - Document how to change the prefix and re-link.
3. - [x] **Installation instructions**
   - Add documentation (README + STATE) describing how to install the binary globally (npm link / pnpm link / `npm install -g .`) so the wrapper becomes available everywhere.
4. - [x] **Tests / verification**
   - Scripted check that running the wrapper from a temp directory prints the resolved working directory inside the TUI/CLI (use `npm run agent --cwd <dir>` equivalent).

## Deliverables
- New plan-compliant executable + configuration knob.
- Updated docs covering installation and prefix switching.
- Automated smoke verification demonstrating the new wrapper respects cwd.
- Added entries to README + STATE referencing cleanup6 completion.
