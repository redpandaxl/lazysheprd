# TASKS — herdr-agent-team

Statuses: `todo` | `in-progress` | `blocked` | `review` | `done`

## Done

| Phase | Notes |
|-------|--------|
| Phase 1 | Scaffold + bootstrap |
| Phase 2 | herd-init + team.yaml + packs |
| Phase 2.1 | Mandatory Herdr messaging |
| Phase 3 | US-01/02/03 engine + TUI + archetypes + git (see below) |

## Phase 3 — Core interactive scaffold (US-01 + US-02 + US-03)

| ID | Task | Owner | Status | Notes |
|----|------|-------|--------|-------|
| T20 | Extract `composer/` package | ops | done | yaml, packs, materialize, archetypes, cli, tui |
| T21 | Archetypes seed TASKS.md | ops | done | blank, greenfield-web, revive-existing, infra-heavy, bot-api |
| T22 | Optional git init (+ commit flag) | ops | done | `--git` / `--no-git` / `--git-commit` + TUI |
| T23 | Role catalog descriptions + enable/kind/model/effort | ops | done | pack descriptions; TUI toggles + kind list |
| T24 | `bin/herd-tui` curses wizard with back navigation | ops | done | steps: name→dir→archetype→roles→models→git→confirm |
| T25 | CLI flags for archetype + git | ops | done | |
| T26 | README + product-stories | ops | done | |
| T27 | QA review Phase 3 | claude | done | PASS — see /tmp/qa-t27-rereview.md | PASS (re-review) — TUI directory-default bug fixed and verified live via tmux (accept-default, explicit-back, custom-path all correct). US-01/02/03 all pass. Non-interactive CLI, git flag matrix, archetypes, bootstrap.sh re-smoked, no regressions. Report: `/tmp/qa-t27-rereview.md`. Ready for T28. |
| T28 | Ops commit | ops | done | Phase 3 on main | Phase 3 on main |

## Phase 4 — Herdr integration

| ID | Story | Task | Owner | Status | Notes |
|----|-------|------|-------|--------|-------|
| T30 | US-04 | Optional Herdr workspace + tabs (`composer/herdr_layout.py`) | ops | done | Schema includes optional herdr block; live smoke + QA functional pass |
| T31 | US-05 | Optional seed prompts / agent start per pane | ops | done | `composer/seed_panes.py`; `--seed-panes`; project-scoped names; 5/5 smoke |

## Phase 5 — Power user

| ID | Story | Task | Status |
|----|-------|------|--------|
| T40 | US-06 | Save/load local team templates | todo |
| T41 | US-07 | Lightweight status companion | todo |
| T42 | US-08 | Update existing project merge mode | todo |

## Communication

All agent coordination via Herdr — `protocols/herdr-messaging.md`.
