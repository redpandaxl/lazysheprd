# herdr-agent-team

Scaffold and compose multi-agent projects that run on [Herdr](https://herdr.dev).

Agent prompts here are **generic**. Project-specific facts live in each instance’s `CONVENTIONS.md` and `TASKS.md`. Coordination always goes through **Herdr messaging** (`protocols/herdr-messaging.md`).

| Doc | Link |
|-----|------|
| Product stories | [docs/product-stories.md](docs/product-stories.md) |
| **FAQ** | [docs/faq/](docs/faq/README.md) |

---

## Install

One-liner style: clone, run `install.sh`, use `herd` / `herd-tui` from anywhere.

**Needs:** `git`, `python3` (stdlib only — no pip).  
**Does not install Herdr** — only this agent builder. Herdr is optional later for layout/seed/status.

### Linux

```bash
sudo apt update && sudo apt install -y git python3   # Debian/Ubuntu
# Fedora: sudo dnf install git python3

git clone <YOUR_FORK_OR_REMOTE_URL> herdr-agent-team
cd herdr-agent-team
./install.sh
```

If the script says `~/.local/bin` is not on `PATH`:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

```bash
herd help
herd-tui
```

### macOS

```bash
# git + python3 (CLT or Homebrew)
xcode-select --install    # if needed
# or: brew install git python

git clone <YOUR_FORK_OR_REMOTE_URL> herdr-agent-team
cd herdr-agent-team
./install.sh
```

If needed for zsh:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

```bash
herd help
herd-tui
```

### Windows (WSL)

```powershell
wsl --install
```

Then **inside WSL** (Ubuntu, etc.):

```bash
sudo apt update && sudo apt install -y git python3

# Prefer Linux home, not /mnt/c
mkdir -p ~/src && cd ~/src
git clone <YOUR_FORK_OR_REMOTE_URL> herdr-agent-team
cd herdr-agent-team
./install.sh

echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

herd help
herd-tui
```

### What `install.sh` does

- `chmod +x` on `bin/herd`, `herd-tui`, `herd-init`, `herd-status`, `herd-update`
- Symlinks them into `~/.local/bin` (override with `HERD_BIN_DIR=... ./install.sh`)
- Leaves the git checkout in place (packs/agents load from there)

```bash
./uninstall.sh    # remove the symlinks only
```

Then: [Onboarding](#onboarding) · [FAQ](docs/faq/README.md)

---

## Onboarding

### 1. Prerequisites

- Ran [Install](#install) (`./install.sh`) so `herd` / `herd-tui` work  
- Optional later: [Herdr](https://herdr.dev) for layout/seed/status; agent CLIs for `--seed-panes`

### 2. Where to run what

| Goal | Where to run |
|------|----------------|
| Walk through the **TUI** | **Plain terminal** (iTerm / Terminal / WezTerm) |
| **CLI** create / update / templates | Plain terminal |
| **See** tabs and agents after layout/seed | **Herdr UI** (new workspace named after the project) |
| Day-to-day multi-agent work | Herdr panes + `herdr agent prompt` |

Nested TUI inside a Herdr pane can work but is harder; prefer a normal terminal for `herd-tui`.

### 3. How you invoke the tools

After `./install.sh`, run from **any** directory:

```bash
herd help
herd-tui
herd status
```

(Or still use `./bin/herd` from the repo.) Commands always load packs/agents from the git checkout `install.sh` linked.

### 4. Where the new project is created

**Default is under the directory where you run the command:**

```text
$PWD/<project-name>     # e.g. ./acme if you ran the command in that folder
```

Override with an absolute or other path:

```bash
./bin/herd init --name acme --dir /path/to/acme --yes
./bin/herd init --name acme --dir ~/projects/acme --yes
# TUI: edit “Target directory” (default is $PWD/<name>)
```

### 5. First visual walkthrough (recommended)

**Terminal A — Herdr**  
Start Herdr as you usually do so the server is up.

**Terminal B — plain shell**

```bash
# any directory — project will be created under $PWD by default
cd ~/projects   # or wherever you want the new folder
herd-tui
```

In the wizard:

1. **Project name** — e.g. `visual-test`  
2. **Target directory** — accept `$PWD/visual-test` or set an explicit path  
3. **Archetype** — e.g. `greenfield-web` or `blank`  
4. **Roles / models** — defaults are fine for a first run  
5. **Git** — optional  
6. **Herdr layout** — yes (creates workspace + tabs)  
7. **Seed panes** — optional; turn **off** for a faster first pass  
8. **Create**

Then in **Herdr**: open the workspace named like your project (`visual-test`), check tabs `ops` … `services`.

### 6. Safer progressive tests

```bash
# A) Files only (no Herdr) — creates ./visual-files under $PWD
herd init --non-interactive --name visual-files \
  --archetype greenfield-web --no-git --no-herdr-layout --yes
ls ./visual-files

# B) Layout only (tabs, no agent start)
herd init --non-interactive --name visual-layout \
  --archetype blank --no-git --herdr-layout --no-seed-panes --yes
# → Herdr UI: workspace visual-layout

# C) Full path (layout + start agents + inject prompts)
herd init --non-interactive --name visual-full \
  --archetype blank --no-git --herdr-layout --seed-panes --yes
# → agents named visual-full-ops, visual-full-qa, …
```

### 7. After the project exists

1. `cd` into the project (or open it from Herdr).  
2. Agents coordinate with **`herdr agent prompt`**, not by hoping someone watches a pane — see `protocols/herdr-messaging.md`.  
3. Ops owns `TASKS.md`; mark done only after QA (or an Ops waiver).  
4. Update roles later without a full rescaffold:

   ```bash
   ./bin/herd update ./visual-test --disable design --yes
   ```

### 8. Common gotchas

| Gotcha | Reality |
|--------|---------|
| “It created a folder next to me” | Default is `$PWD/<name>` — use `--dir` for elsewhere |
| “I ran it from the herdr-agent-team repo” | That creates `./my-project` *inside this repo* unless you `--dir` elsewhere |
| “Command not found: herd” | Re-run `./install.sh` and ensure `~/.local/bin` is on `PATH` |
| “Layout failed but folder exists” | Expected — files still succeed; check `herdr` on PATH |
| Agents don’t talk | Must use Herdr messaging; board-only updates are not enough |

More detail: **[docs/faq/](docs/faq/README.md)**.

---

## Quick start (command cheat sheet)

After `./install.sh`:

```bash
herd help
herd-tui

herd init --non-interactive --name acme --archetype greenfield-web --git --yes
herd init --non-interactive --name acme --herdr-layout --seed-panes --yes

herd template save my-web --archetype greenfield-web --persona qa:claude:-:high
herd init --non-interactive --name acme --template my-web --yes

herd status
herd update ./acme --disable design --yes
```

Also available: `herd-init`, `herd-status`, `herd-update`, `herd-tui` (same install).

---

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
install.sh               # → symlink bins into ~/.local/bin
uninstall.sh
bin/herd                 # init | status | update | template
bin/herd-tui             # curses wizard
composer/                # shared engine
archetypes/ packs/ agents/ protocols/ templates/ schemas/
docs/faq/
```

## Agent communication

Mandatory Herdr messaging is baked into protocols, agent prompts, CONVENTIONS, TASKS, and boot prompts. Board updates alone are not enough — use `herdr agent prompt`.

## FAQ

See **[docs/faq/README.md](docs/faq/README.md)** for expanded answers (where to test, paths, bin vs repo, layout/seed, templates, update safety, etc.).
