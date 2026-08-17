# herdr-agent-team

Boilerplate for spinning up a new Herdr multi-agent project.

Agent prompts in this repo are **generic**. Project-specific facts belong in the instance's `CONVENTIONS.md` and `TASKS.md` (copied from `templates/` at bootstrap). Improving this template later does not change projects already scaffolded.

## Structure

```
herdr-agent-team/
├── bootstrap.sh              # copy templates into ~/project-name
├── agents/                   # generic role prompts (paste into Herdr panes)
│   ├── ops.md
│   ├── infrastructure.md
│   ├── developers.md
│   ├── design.md
│   └── qa.md
├── templates/                # files copied into new instances
│   ├── CONVENTIONS.md
│   └── TASKS.md
├── protocols/
│   └── coordination.md       # communication, board, DoD, git, escalation
├── README.md
└── TASKS.md                  # runtime board for THIS repo only
```

There is no `agents/services.md` by default. The standard Herdr tabs still include a `services` pane if you want one.

## Bootstrap

From this repo:

```bash
./bootstrap.sh <project-name>
```

Creates `$HOME/<project-name>` with `CONVENTIONS.md`, `TASKS.md`, `protocols/`, and `agents/*.md`. Refuses to clobber a non-empty target.

## Standard tabs

After `cd` into the new project and running `herdr`, create:

`ops` · `infra` · `dev` · `design` · `qa` · `services`

Paste the matching `agents/*.md` into each pane (skip `services` until you add a prompt). Tell Ops:

> Read CONVENTIONS.md, TASKS.md and protocols/coordination.md. Begin.

## Improving the template

Edit this repo (`agents/`, `templates/`, `protocols/`, `bootstrap.sh`). Existing instances keep their copies until someone copies changes over on purpose.
