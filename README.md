# herdr-agent-team

Scaffold and compose multi-agent projects that run on [Herdr](https://herdr.dev).

Agent prompts here are **generic**. Project-specific facts live in each instance’s `CONVENTIONS.md` and `TASKS.md`. Coordination always goes through **Herdr messaging** (`protocols/herdr-messaging.md`).

Product backlog: [docs/product-stories.md](docs/product-stories.md).

## Quick start

```bash
# Unified CLI
./bin/herd help

# TUI wizard (US-01…US-05 options)
./bin/herd-tui

# Non-interactive create
./bin/herd init --non-interactive --name acme --archetype greenfield-web --git --yes
./bin/herd init --non-interactive --name acme --herdr-layout --seed-panes --yes

# From a saved template (US-06)
./bin/herd template save my-web --archetype greenfield-web --persona qa:claude:-:high
./bin/herd init --non-interactive --name acme --template my-web --yes

# Status (US-07)
./bin/herd status
./bin/herd status --focus w3

# Update existing project (US-08)
./bin/herd update ~/acme --disable design --persona developers:codex:-:high --yes
./bin/herd update ~/acme --force-prompts --yes   # overwrite agents/*.md from pack
```

Legacy shims: `herd-init`, `herd-status`, `herd-update`, `herd-tui`.

## Features by story

| Story | Capability |
|-------|------------|
| US-01 | Project name/dir, roles, models, files, optional git |
| US-02 | Role catalog + enable/disable + kind/model/effort |
| US-03 | Archetypes seed `TASKS.md` |
| US-04 | Optional Herdr workspace + tabs (`--herdr-layout`) |
| US-05 | Optional start agents + inject prompts (`--seed-panes`) |
| US-06 | Save/load user templates (`~/.config/herd-compose/templates/`) |
| US-07 | `herd status` companion overview |
| US-08 | `herd update` merge config; no silent overwrite of customs |

## What gets generated

| Artifact | Purpose |
|----------|---------|
| `CONVENTIONS.md` | Project facts + messaging callout |
| `TASKS.md` | Archetype-seeded board |
| `protocols/*` | coordination + herdr-messaging |
| `agents/*.md` | Role prompts |
| `team.yaml` | Plan + optional `herdr` layout/seed metadata |
| `.git/` | Optional |

## Archetypes

`blank` · `greenfield-web` · `revive-existing` · `infra-heavy` · `bot-api`

## Structure

```
bin/herd                 # init | status | update | template
bin/herd-tui             # curses wizard
bin/herd-init            # → init
composer/                # shared engine
archetypes/ packs/ agents/ protocols/ templates/ schemas/
```

## Agent communication

Mandatory Herdr messaging is baked into protocols, agent prompts, CONVENTIONS, TASKS, and boot prompts. Board updates alone are not enough — use `herdr agent prompt`.
