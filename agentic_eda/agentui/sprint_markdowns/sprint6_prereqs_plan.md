# Sprint 6 Prereqs – Plan

## Phase A – Path Resolver Foundation
- [x] Design `src/path/resolver.ts` API covering normalization, validation, and friendly errors (include trailing-slash + Windows drive coverage).
- [x] Implement resolver + memoized helpers (detect mentions, convert `/examples/...` to absolute workspace paths, capture canonical + display paths).
- [x] Add Vitest coverage for resolver (success/failure cases, serialized metadata, notebook integration rewrite helper).
- [x] Wire resolver into DeepAgents tool adapters + CLI filesystem shortcuts so no raw user string reaches the backend.

## Phase B – Shell Command Capability
- [x] Catalog every file operation supported by Codex/Gemini (cp, mv, rm, mkdir, list, diff, grep, patch, etc.) and map them to AgenTUI tools.
- [x] Implement/upgrade DeepAgents tools so each operation can be triggered reliably (including safe wrappers for destructive commands).
- [x] Document tool schemas so the agent can choose the right command from natural-language prompts.
- [x] Surface live reasoning/actions UI via LangGraph streaming so multi-step progress is visible (Reasoning/Actions/Answer sections).
- [ ] Provide helper scripts/utilities (`npm run agent -- "copy ..."`, etc.) for each verb.

## Phase C – Testing & Documentation
- [ ] Create scripted smoke tests invoking resolver + commands via `npm run agent -- "..."` (list/copy/move/delete/read/search/open/diff).
- [ ] Extend README + ARCHITECTURE docs with resolver overview, shell-command matrix, and testing instructions.
- [ ] Re-run `npm run typecheck`, `npm run test`, `npm run notebook:test`, and new smoke tests.
- [ ] Gather sign-off, then resume main Sprint 6 tasks.
