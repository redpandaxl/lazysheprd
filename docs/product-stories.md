# Product stories → current state

Source backlog: US-01 … US-08 (TUI composer).

## Gap map

| Story | Status | Today | Gap |
|-------|--------|-------|-----|
| **US-01** Create project | **Partial** | `herd-init` CLI: name, dir, pack, roles, models, files | No TUI; no optional `git init` |
| **US-02** Role & model config | **Partial** | Disable non-ops; kind/model/effort; defaults | Weak role descriptions; no free add of roles; no multi-step Back; OpenRouter not explicit |
| **US-03** Archetype / phase | **Missing** | Blank `templates/TASKS.md` only | Archetype catalog + seeded TASKS |
| **US-04** Herdr layout | **Done** | `--herdr-layout` / TUI option → workspace + tabs + focus; ids in `team.yaml` | Server auto-start if needed |
| **US-05** Seed panes | **Done** | `--seed-panes` / TUI: start agents + inject role+boot; report + team.yaml seed | Project-scoped agent names |
| **US-06** Saved templates | **Missing** | Packs only | Local JSON/TOML user templates |
| **US-07** Status overview | **Missing** | Use `herdr agent list` raw | Companion view |
| **US-08** Update existing | **Missing** | Refuse non-empty target | Merge mode + confirm overwrites |

## Build order (locked)

1. **P0 — Core engine (shared)** — extract materialize/plan from `herd-init`; archetypes (US-03); git init (US-01); richer role catalog (US-02)
2. **P1 — Interactive surface** — TUI wizard for US-01+02+03 over the engine; CLI remains thin wrapper
3. **P2 — US-04** Herdr layout auto ✅
4. **P3 — US-05** Seed panes ✅
5. **P4 — US-06** User templates
6. Later: US-07, US-08

## Architecture

```
composer/           # shared Python package (stdlib + optional textual)
  engine.py         # plan + materialize + git
  packs / archetypes loaders
  herdr_layout.py   # US-04/05 later
bin/herd-init       # CLI rail (non-interactive + interactive)
bin/herd-tui        # TUI entry (US-01 surface)
archetypes/*.yaml   # TASKS seeds
packs/...           # roles + defaults
```

One materialize path; CLI and TUI only collect a `Plan`.
