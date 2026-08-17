# TASKS

Statuses: `todo` | `in-progress` | `blocked` | `review` | `done`

Ops owns this board. Each agent updates **only their own** rows (status + notes).

A task may be marked `done` only after QA has reviewed it (or Ops explicitly waives QA).

**Herdr messaging required:** board updates do not replace agent-to-agent communication.
On assign / block / review / done, Ops and agents must `herdr agent prompt` the relevant people.
See `protocols/herdr-messaging.md`.

## Phase 1 — `[PHASE_NAME]`

| ID | Task | Owner | Status | Notes |
|----|------|-------|--------|-------|
| T1 | `[TASK_DESCRIPTION]` | `[OWNER]` | todo | |

## Backlog

| ID | Task | Owner | Status | Notes |
|----|------|-------|--------|-------|
