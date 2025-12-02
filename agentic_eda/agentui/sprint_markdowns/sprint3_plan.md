# AgenTUI Sprint 3 Plan

## Objective
Polish the frontend experience by (a) letting users stage their next prompt while the agent thinks and (b) presenting a Codex-style startup splash with model + cwd info.

## Workstreams & Tasks

### 1. Thinking-State Composer UX
- [ ] Decouple `ComposerInput` focus from `state.status` so typing always works.
- [ ] Gate `sendMessage`/slash dispatcher when status === `thinking`; emit system hint instead of submitting.
- [ ] Ensure slash suggestion UI still opens while busy (but selection/Enter is blocked).
- [ ] Tests: composer reducer snapshot + slash command unit tests covering “busy” state.

### 2. Startup Status Panel
- [ ] Build `StartupSplash` component (ASCII border, dynamic version/model/cwd, `~` shorthand).
- [ ] Hook into `App` so splash renders on mount and hides after first message (or first keystroke?).
- [ ] Handle narrow terminals (truncate or wrap gracefully).
- [ ] Remove the existing top header panel once splash is in place (sidebar already shows model/status).

### 3. Docs & QA
- [ ] Update README / specs with new UX (typing while thinking, splash screenshot).
- [ ] Extend manual QA checklist (busy typing, slash rejection, splash hide conditions).

## Acceptance Criteria
1. User can keep typing + editing text while agent is “Thinking…”; hitting Enter shows a friendly block message until the agent finishes.
2. Slash commands honor the busy state (no `/model` mid-run) yet suggestions still appear when typing `/`.
3. ASCII splash appears on startup with correct data and disappears once conversation begins.
4. Docs/specs updated; tests cover regression scenarios.
