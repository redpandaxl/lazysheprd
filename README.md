# herdr-agent-team

Scaffold and compose multi-agent projects that run on [Herdr](https://herdr.dev).

Agent prompts here are **generic**. Project-specific facts live in each instance’s `CONVENTIONS.md` and `TASKS.md`. Coordination always goes through **Herdr messaging** (see `protocols/herdr-messaging.md`).

Product backlog: [docs/product-stories.md](docs/product-stories.md).

## Quick start

```bash
# TUI wizard (US-01 + US-02 + US-03) — recommended
./bin/herd-tui

# CLI rail
./bin/herd-init
./bin/herd-init --non-interactive --name acme --archetype greenfield-web --git --yes
./bin/herd-init --list-archetypes
./bin/herd-init --list-packs
```

## What gets generated

| Artifact | Purpose |
|----------|---------|
| `CONVENTIONS.md` | Project facts + mandatory Herdr messaging callout |
| `TASKS.md` | Seeded from **archetype** (or blank) |
| `protocols/coordination.md` | Team rules |
| `protocols/herdr-messaging.md` | How agents must `herdr agent prompt` each other |
| `agents/*.md` | Role prompts for enabled personas |
| `team.yaml` | Roles, kinds, models, effort, boot prompts, layout tabs |
| `.git/` | Optional (`--git` / TUI toggle) |

## Archetypes (US-03)

| Id | Use when |
|----|----------|
| `blank` | Full manual TASKS control |
| `greenfield-web` | New web product |
| `revive-existing` | Existing codebase under ops |
| `infra-heavy` | Platform / CI / envs first |
| `bot-api` | Bot + API service |

You can edit `TASKS.md` after generation.

## Roles & models (US-02)

Default pack `software-delivery`: **Ops**, **Infrastructure**, **Developers**, **Design**, **QA** (each with a short description).

- Toggle roles on/off (Ops always on)
- Assign kind/tool: `grok`, `claude`, `codex`, `cursor`, `gemini`, …, `other`
- Optional model string + effort (`low`/`medium`/`high`/`max`)
- Stored as **intent** in `team.yaml` (CLI flags differ by agent)

## Structure

```
herdr-agent-team/
├── bin/herd-tui              # curses TUI wizard
├── bin/herd-init             # CLI (interactive + --non-interactive)
├── composer/                 # shared plan + materialize engine
├── archetypes/               # TASKS seeds
├── agents/                   # generic role prompts
├── packs/software-delivery/  # default role pack
├── protocols/                # coordination + herdr-messaging
├── templates/                # CONVENTIONS + blank TASKS fallback
├── schemas/team.v1.schema.json
└── bootstrap.sh              # dumb full copy (no team.yaml / archetypes)
```

## After scaffold (still manual for now)

US-04/05 (auto Herdr layout + seed panes) are **not** built yet.

1. `cd` into the project  
2. `herdr`  
3. Create tabs from `team.yaml` `layout.tabs`  
4. `herdr agent start <id> --kind <kind> --pane ...`  
5. Boot with each persona’s `boot_prompt`  

## Agent communication (built in)

Every project includes mandatory Herdr-first protocols and agent prompt sections. Board updates alone are **not** coordination — use `herdr agent prompt`.

## Roadmap (stories)

| Priority | Stories | Status |
|----------|---------|--------|
| P0 | US-01, US-02, US-03 (scaffold + TUI) | **This phase** |
| P1 | US-04 Herdr layout auto | Planned |
| P2 | US-05 Seed panes | Planned |
| P3 | US-06 Templates | Planned |
| Later | US-07 status, US-08 update existing | Planned |
