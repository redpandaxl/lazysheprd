# Lightweight composer (Phase 2)

## Goal

CLI-only team composer: pick a pack, tune personas (kind/model/effort), write project files. **No TUI. No Herdr auto-spawn.**

## Deliverables

1. `schemas/team.v1.schema.json` — JSON Schema for `team.yaml`
2. `packs/software-delivery/pack.yaml` — default personas pointing at repo `agents/*.md`
3. `bin/lazysheprd-init` — interactive rail (Python 3 stdlib only)
4. Materialize into `$PWD/<project>` (or `--dir`):
   - `CONVENTIONS.md`, `TASKS.md` from `templates/`
   - `protocols/`
   - `agents/*.md` for enabled personas
   - `team.yaml` (instance plan)
5. README section for `lazysheprd-init`
6. Smoke: non-interactive flags for CI/dry-run

## Out of scope

- Herdr tab/pane/agent start
- Extra packs (gtm, sales, …)
- Custom TUI / right-rail co-pilot
- Guaranteeing model/effort flags work on every agent CLI (store intent; document adapters)

## Rail steps

1. Project name (+ optional target dir)
2. Domain pack (only `software-delivery` for now)
3. Persona review (enable/disable, agent_kind, model, effort)
4. Confirm → write files → print next steps (open herdr, create tabs, start agents manually)

## team.yaml shape (v1)

See `schemas/team.v1.schema.json` and example after first materialize.
