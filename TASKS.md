# TASKS — herdr-agent-team

Statuses: `todo` | `in-progress` | `blocked` | `review` | `done`

## Done

| Phase | Notes |
|-------|--------|
| Phase 1 | Scaffold + bootstrap |
| Phase 2 | herd-init + team.yaml + packs + messaging |
| Phase 3 | US-01/02/03 TUI + archetypes + git |
| Phase 4 | US-04 layout + US-05 seed panes |
| Phase 5 | US-06 templates + US-07 status + US-08 update |

## Phase 5 — Power user (US-06 / 07 / 08)

| ID | Story | Task | Owner | Status | Notes |
|----|-------|------|-------|--------|-------|
| T40 | US-06 | User templates JSON under `~/.config/herd-compose/templates/` | ops | done | `herd template *`, `--template`, `--save-template` |
| T41 | US-07 | `herd status` companion | ops | done | `composer/status_view.py`; `--focus` |
| T42 | US-08 | `herd update` existing projects | ops | done | preserve CONVENTIONS; skip prompts unless `--force-prompts` |
| T43 | — | Unified `bin/herd` entry + docs | ops | done | |

## Communication

All agent coordination via Herdr — `protocols/herdr-messaging.md`.
