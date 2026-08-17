# TASKS — herdr-agent-team (template repo)

Statuses: `todo` | `in-progress` | `blocked` | `review` | `done`

## Phase 1 — Scaffold (complete)

| ID | Task | Owner | Status | Notes |
|----|------|-------|--------|-------|
| T1–T8 | Recommended structure + bootstrap + QA + initial commit | dev/claude/ops | done | On `main`. |

## Phase 2 — Lightweight composer (complete)

| ID | Task | Owner | Status | Notes |
|----|------|-------|--------|-------|
| T10 | Schema + example team.yaml | dev | done | QA PASS |
| T11 | packs/software-delivery | dev | done | QA PASS |
| T12 | bin/herd-init CLI rail | dev | done | QA PASS after interactive parse + name safety fixes |
| T13 | Materialize files + team.yaml | dev | done | QA PASS |
| T14 | README | dev | done | QA PASS |
| T15 | Smoke | dev | done | QA PASS |
| T16 | QA review Phase 2 | claude | done | PASS — `/tmp/qa-t16-rereview.md` |
| T17 | Ops commit | ops | done | Phase 2 commit on main; no remote push |

## Design note

See `docs/lightweight-composer.md`.

## Follow-ups (not started)

- Non-interactive disable persona
- Extra packs (gtm, analytics, …)
- Herdr tab/agent auto-spawn from team.yaml
- TUI / right-rail co-pilot

## Phase 2.1 — Herdr messaging in scaffold

| ID | Task | Owner | Status | Notes |
|----|------|-------|--------|-------|
| T18 | Bake mandatory Herdr messaging into protocols, agents, templates, boot prompts, next steps | ops | done | protocols/herdr-messaging.md; all agent prompts; CONVENTIONS/TASKS; pack boot prompts; bootstrap + herd-init next steps |
