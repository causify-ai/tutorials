# AgenTUI Architecture

```
src/
├── agent/              # DeepAgents runner + unit tests
├── agent-cli.ts        # Single-shot CLI entrypoint
├── cli.tsx             # Ink TUI entrypoint
├── commands/           # Slash command parser + tests
├── config/             # Config loader (Zod) + tests
├── fs/                 # Filesystem helpers (mention-aware shortcuts)
├── path/               # Workspace-safe resolver shared by UI + tools
├── models.ts           # Model metadata (context windows)
├── state/              # Session + usage reducers/tests
├── tools/              # Custom LangChain tools (filesystem, future notebook/image tools)
└── ui/                 # React components, mention utilities
scripts/
├── deepagents-model-test.ts # Manual smoke test for DeepAgents models
└── agent-smoketest.ts       # Runs npm run agent prompts sequentially for smoke coverage
```

## Data/Dependency Flow

1. `cli.tsx` and `agent-cli.ts` both call `loadConfig`, `prepareAgentInput`, and `createAgentRunner`.
2. The router/prompt helpers (`src/agent/router.ts`, `src/agent/prompt.ts`) attach `[Intent]` and `[Mentioned files]` metadata so the agent knows when to converse vs. plan multi-step work.
3. `createAgentRunner` pulls tool definitions from `src/tools/`, which in turn can use helpers from `src/fs/`.
4. Both CLI and TUI consume the shared stream normalizer in `src/agent/events.ts`, which now emits `reasoning_visibility` events and natural-language action summaries (via `describeToolAction`) so trivial turns hide the plan and Actions never show raw JSON.
5. The TUI (`ui/App.tsx`) relies on `commands`, `fs/shortcuts`, and session state modules, and renders file paths via the path-highlighting engine (cyan text for actual paths/extensions).
6. Filesystem shortcuts are shared between CLI/TUI ensuring consistent behavior.
7. `path/resolver.ts` is the single authority for translating any user path (mentions, `/examples`, `~/`, Windows drives) back into the sandbox before the tools or DeepAgents touch the filesystem.

Extend this document whenever new folders or toolchains (e.g., ipynb, image analysis) are added.
