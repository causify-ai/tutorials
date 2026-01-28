# Cleanup 6 Specs – Global `agentui` Command

## Functional Requirements
1. **Global launcher**
   - Running `agentui` from any directory must launch the AgenTUI CLI with that directory as the working directory (no implicit `cd` into the repo).
   - The command must pipe stdin/stdout/stderr transparently and support arguments identical to `npm run dev`/`npm run agent`.
2. **Configurable prefix**
   - The command name (default `agentui`) must be configurable in a single location (e.g., package.json `bin` entry or env var). Changing the prefix and re-linking should pick up the new name without further code edits.
   - Document the config knob and how to re-link with a different prefix.
3. **Installation guidance**
   - README must describe how to install/link the binary globally (e.g., `npm install -g .` or `npm link`) so the command becomes available on PATH.
   - STATE.md must call out the new capability and reference cleanup6 completion.
4. **Verification**
   - Provide a repeatable test (script or doc) that exercises running the command from a temp directory and confirms AgenTUI inherits that cwd (log message or prompt).
   - Ensure existing smoke tests continue to work; add a targeted test if possible (e.g., Node script invoking the new binary with a custom cwd).

## Non-Functional Requirements
- Wrapper should be minimal and not add noticeable startup latency.
- Works on macOS/Linux shells (bash/zsh) and is future-proof for Windows (document if PowerShell usage differs).
- No breaking changes to existing npm scripts.

## Out of Scope
- Changing how the CLI decides which workspace to operate on beyond inheriting cwd.
- Packaging/distribution beyond npm link/NPM global install instructions.
