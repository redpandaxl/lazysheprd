# herdr-agent-team

Boilerplate for spinning up a new Herdr multi-agent project.

Agent prompts in this repo are **generic**. Project-specific facts belong in the instance's `CONVENTIONS.md` and `TASKS.md` (copied from `templates/` at init). Improving this template later does not change projects already scaffolded.

See [docs/lightweight-composer.md](docs/lightweight-composer.md) for the Phase 2 composer design.

## Structure

```
herdr-agent-team/
├── bin/herd-init             # pack + persona rail; writes team.yaml (no Herdr spawn)
├── bootstrap.sh              # dumb copy of templates + all agent prompts
├── agents/                   # generic role prompts
├── packs/                    # domain packs (software-delivery)
├── schemas/team.v1.schema.json
├── examples/                 # sample team.yaml
├── templates/                # CONVENTIONS.md + TASKS.md copied into instances
├── protocols/coordination.md
├── docs/lightweight-composer.md
├── README.md
└── TASKS.md                  # runtime board for THIS repo only
```

There is no `agents/services.md` by default.

## Ways to start a project

### herd-init (recommended)

Interactive rail: name, target dir, pack, persona kind/model/effort, then write files.

```bash
./bin/herd-init
./bin/herd-init --name acme
./bin/herd-init --non-interactive --name acme --yes
./bin/herd-init --non-interactive --name acme --dir /tmp/acme --yes \
  --persona qa:claude:-:high
./bin/herd-init --list-packs
```

Creates `$HOME/<name>` (or `--dir`) with `CONVENTIONS.md`, `TASKS.md`, `protocols/`, enabled `agents/*.md`, and `team.yaml`. Refuses to clobber a non-empty target.

`team.yaml` records **intent** for `model` and `effort`. Actual CLI flags differ by agent kind (Grok vs Claude, etc.). Do not assume every kind accepts `--model` / `--effort`.

`herd-init` does **not** open Herdr or start agents. After it finishes:

1. `cd` into the project
2. `herdr`
3. Create tabs from `team.yaml` `layout.tabs`
4. Start each agent manually, e.g. `herdr agent start <id> --kind <kind> --pane ...`
5. Use `agents/*.md`; boot each agent with its `boot_prompt` from `team.yaml`

### Agent communication (built into the scaffold)

Every new project includes:

- `protocols/coordination.md` — non-negotiable Herdr-first rules
- `protocols/herdr-messaging.md` — exact `herdr agent prompt` patterns
- Agent prompts with a **Herdr communication (mandatory)** section
- `CONVENTIONS.md` + `TASKS.md` reminders that board updates alone are not enough
- Boot prompts that force reading the messaging protocol before work

Agents must coordinate with `herdr agent prompt` — not by hoping someone watches a pane. You should not need to re-explain this each time if agents follow the scaffold files.

### bootstrap.sh (dumb copy)

```bash
./bootstrap.sh <project-name>
```

Copies templates, protocols, and every `agents/*.md` into `$HOME/<project-name>`. No pack, no `team.yaml`, no persona toggles. Same non-empty-target guard.

## Standard tabs

`ops` · `infra` · `dev` · `design` · `qa` · `services`

`herd-init` layout comes from enabled pack personas (no `services` tab unless you add one). `bootstrap.sh` still mentions a `services` pane if you want one.

## Improving the template

Edit this repo (`agents/`, `packs/`, `templates/`, `protocols/`, `bin/herd-init`, `bootstrap.sh`). Existing instances keep their copies until someone copies changes over on purpose.
