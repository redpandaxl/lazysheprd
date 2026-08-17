# TASKS — {{PROJECT_NAME}}

Statuses: `todo` | `in-progress` | `blocked` | `review` | `done`

Ops owns this board. Agents update only their own rows. **Herdr messaging required** — see `protocols/herdr-messaging.md`.

## Phase 0 — Foundations

| ID | Task | Owner | Status | Notes |
|----|------|-------|--------|-------|
| T1 | Environments matrix (local/dev/stage/prod) in CONVENTIONS.md | infrastructure | todo | |
| T2 | Access, secrets, and least-privilege notes | infrastructure | todo | |
| T3 | Observability baseline (logs/metrics/alerts intent) | infrastructure | todo | |

## Phase 1 — Delivery path

| ID | Task | Owner | Status | Notes |
|----|------|-------|--------|-------|
| T4 | CI pipeline (lint/test/build) | infrastructure | todo | |
| T5 | Deploy path (even if manual) documented + scripted where safe | infrastructure | todo | |
| T6 | App/service minimal health endpoint or check | developers | todo | |
| T7 | QA: disaster/smoke checklist for deploys | qa | todo | |

## Phase 2 — Guardrails

| ID | Task | Owner | Status | Notes |
|----|------|-------|--------|-------|
| T8 | Backup / rollback notes | infrastructure | todo | |
| T9 | Security pass on secrets + public surfaces | qa | todo | |

## Backlog

| ID | Task | Owner | Status | Notes |
|----|------|-------|--------|-------|
