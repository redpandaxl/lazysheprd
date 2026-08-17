# TASKS — {{PROJECT_NAME}}

Statuses: `todo` | `in-progress` | `blocked` | `review` | `done`

Ops owns this board. Agents update only their own rows. **Herdr messaging required** — see `protocols/herdr-messaging.md`.

## Phase 0 — Align

| ID | Task | Owner | Status | Notes |
|----|------|-------|--------|-------|
| T1 | Fill CONVENTIONS.md: product goal, users, non-goals | ops | todo | Escalate product questions to human |
| T2 | Propose stack + commands table in CONVENTIONS.md | infrastructure | todo | |
| T3 | Capture IA / primary user flows (thin) | design | todo | Spec only |

## Phase 1 — Skeleton

| ID | Task | Owner | Status | Notes |
|----|------|-------|--------|-------|
| T4 | Scaffold app (repo layout, lint/test/run scripts) | developers | todo | After T2 |
| T5 | Dev environment + secrets pattern documented | infrastructure | todo | |
| T6 | CI: lint + test on PR | infrastructure | todo | |

## Phase 2 — First vertical slice

| ID | Task | Owner | Status | Notes |
|----|------|-------|--------|-------|
| T7 | Implement happy-path feature end-to-end | developers | todo | |
| T8 | Basic UI for slice | design / developers | todo | Design specs → dev |
| T9 | QA review of slice + smoke path | qa | todo | |

## Backlog

| ID | Task | Owner | Status | Notes |
|----|------|-------|--------|-------|
| B1 | Auth | — | todo | |
| B2 | Deploy pipeline | — | todo | |
