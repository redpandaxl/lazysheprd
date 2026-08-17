# TASKS — LazySheprd

Statuses: `todo` | `in-progress` | `blocked` | `review` | `done`

## Done

| Phase | Notes |
|-------|--------|
| Phase 1 | Scaffold + bootstrap |
| Phase 2 | lazysheprd-init + team.yaml + packs + messaging |
| Phase 3 | US-01/02/03 TUI + archetypes + git |
| Phase 4 | US-04 layout + US-05 seed panes |
| Phase 5 | US-06 templates + US-07 status + US-08 update |

## Phase 5 — Power user (US-06 / 07 / 08)

| ID | Story | Task | Owner | Status | Notes |
|----|-------|------|-------|--------|-------|
| T40 | US-06 | User templates JSON under `~/.config/lazysheprd/templates/` | ops | done | `lazysheprd template *`, `--template`, `--save-template` |
| T41 | US-07 | `lazysheprd status` companion | ops | done | `lazysheprd/status_view.py`; `--focus` |
| T42 | US-08 | `lazysheprd update` existing projects | ops | done | preserve CONVENTIONS; skip prompts unless `--force-prompts` |
| T43 | — | Unified `bin/lazysheprd` entry + docs | ops | done | |

## Communication

All agent coordination via Herdr — `protocols/herdr-messaging.md`.
