# FAQ

Common questions about using **herdr-agent-team** (the composer) with [Herdr](https://herdr.dev).

---

## Where should I run this for a visual test?

| What you’re testing | Best place | Why |
|---------------------|------------|-----|
| **TUI wizard** (`./bin/herd-tui`) | **Plain terminal** (iTerm, Terminal.app, WezTerm, …) | Full-screen curses works more cleanly outside Herdr’s chrome |
| **CLI** (`./bin/herd init …`) | Plain terminal | No UI needed |
| **Layout + seed** (`--herdr-layout --seed-panes`) | Start from a plain terminal with Herdr available | Creates a **new workspace**; open Herdr afterward to see tabs/agents |
| **`herd status`** | Either | Talks to the live Herdr server |

**Recommended first visual walkthrough**

1. Start Herdr as you usually do (server running).
2. In a **normal** terminal (not required to be a Herdr pane):

   ```bash
   cd /path/to/herdr-agent-team
   ./bin/herd-tui
   ```

3. Complete the wizard (see [Onboarding](../../README.md#onboarding) in the root README).
4. In the **Herdr UI**, open the new workspace named after your project.

You *can* run the TUI inside a Herdr pane; nested full-screen UIs are just harder to use.

---

## Does it create the project in my current directory?

**Yes, by default** — under the directory where you run the command:

```text
$PWD/<project-name>
```

Example: you `cd ~/work` and run init with name `acme` → `~/work/acme`.

Override with `--dir` (or the TUI target step):

```bash
# CLI
./bin/herd init --name acme --dir /path/to/acme --yes
./bin/herd init --non-interactive --name acme --dir ~/projects/acme --yes

# TUI
# On the “Target directory” step, edit the default ($PWD/<name>)
```

**Tip:** if you run `./bin/herd-tui` from inside `herdr-agent-team`, the default project folder is created *inside that repo* unless you change the path.

---

## Do I have to run this from the herdr-agent-team repo?

**No — after `./install.sh`.**

```bash
cd herdr-agent-team && ./install.sh
# then from anywhere:
herd help
herd-tui
```

- Install symlinks `herd` / `herd-tui` / … into `~/.local/bin` (pointing at this checkout).
- Packs and agents still load from the **git checkout** the symlinks target.
- Your **cwd** only matters for the default project path (`$PWD/<name>`).

---

## Plain terminal vs Herdr — what runs where?

| Step | Where |
|------|--------|
| Run wizard / `herd init` | Plain terminal (recommended) |
| Inspect files | Anywhere (`ls ./my-project` or your `--dir`) |
| See tabs / agents after layout+seed | **Herdr** UI → workspace = project name |
| Day-to-day multi-agent work | Herdr panes; coordinate with `herdr agent prompt` |

---

## What’s the difference between bootstrap, init, and the TUI?

| Entry | Use when |
|-------|----------|
| `./bin/herd-tui` | Guided visual setup (roles, archetype, git, layout, seed) |
| `./bin/herd init …` | Scriptable / non-interactive create |
| `./bootstrap.sh <name>` | Dumb copy of all agent files — no `team.yaml`, no archetypes, no layout |

Prefer **`herd-tui`** or **`herd init`**. Keep `bootstrap.sh` as the minimal fallback.

---

## What do layout and seed actually do?

- **`--herdr-layout`**: create a Herdr workspace named like the project, tabs (ops/infra/dev/design/qa/services), focus it; write pane ids into `team.yaml`.
- **`--seed-panes`**: requires layout; starts each enabled agent in its pane and injects `agents/*.md` + boot prompt. Agents are named `{project}-{role}` (e.g. `acme-ops`) so they don’t clash with other live agents named `ops`.

Safer first runs:

```bash
# Files only
./bin/herd init --non-interactive --name visual-files \
  --archetype greenfield-web --no-git --no-herdr-layout --yes

# Layout, no agents yet
./bin/herd init --non-interactive --name visual-layout \
  --archetype blank --no-git --herdr-layout --no-seed-panes --yes
```

---

## Where are saved templates stored?

User templates (US-06):

```text
~/.config/herd-compose/templates/*.json
```

```bash
./bin/herd template list
./bin/herd template dir
./bin/herd template save my-web --archetype greenfield-web
./bin/herd init --non-interactive --name acme --template my-web --yes
```

---

## How do I update an existing project without destroying custom prompts?

```bash
./bin/herd update ~/acme --disable design --yes
# CONVENTIONS.md is never overwritten by update
# agents/*.md are skipped unless you force:
./bin/herd update ~/acme --force-prompts --yes
```

---

## Agents ignore each other — what did we forget?

Coordination is **not** “watch my pane.” Every scaffold includes:

- `protocols/herdr-messaging.md`
- rules in `protocols/coordination.md`
- agent prompt sections + boot prompts

Status and handoffs go through:

```bash
herdr agent prompt <name-or-pane> "..."
```

Board updates (`TASKS.md`) alone are not enough.

---

## Herdr layout failed but files were created — is that OK?

Yes. Layout/seed failures are non-fatal: the project directory is still written. Fix Herdr install/PATH/server, then create layout manually or re-run a fresh project with `--herdr-layout` (update path does not auto-layout yet).

---

## Can I convert the TUI from Python curses to Charm/Bubble Tea later?

Yes. The product logic lives in `composer/` (plan + materialize + layout + seed). The TUI is a thin skin (`composer/tui.py`). A Go/Charm or Rust/Ratatui front end can call the same flows later without rewriting packs/archetypes.

---

## More docs

- [Root README — Onboarding](../../README.md#onboarding)
- [Product stories](../product-stories.md)
- [Lightweight composer notes](../lightweight-composer.md)
