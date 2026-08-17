# herdr-agent-team

Scaffold and compose multi-agent projects that run on [Herdr](https://herdr.dev).

Agent prompts here are **generic**. Project-specific facts live in each instance’s `CONVENTIONS.md` and `TASKS.md`. Coordination always goes through **Herdr messaging** (`protocols/herdr-messaging.md`).

| Doc | Link |
|-----|------|
| Product stories | [docs/product-stories.md](docs/product-stories.md) |
| **FAQ** | [docs/faq/](docs/faq/README.md) |

---

## Install

This repo is the **composer** (scaffold + TUI/CLI). You need:

1. **Python 3** (3.10+ recommended; stdlib only — no `pip install` for the composer)  
2. This **git checkout** (bins load packs/agents from the repo root)  
3. **[Herdr](https://herdr.dev)** on `PATH` for layout/seed/status (optional for files-only init)  
4. Optional: agent CLIs you want to seed (`grok`, `claude`, `codex`, …)

Official Herdr install reference: [herdr.dev/docs/install](https://herdr.dev/docs/install/).

### Linux

```bash
# Python
sudo apt update && sudo apt install -y git python3   # Debian/Ubuntu
# or: sudo dnf install git python3                   # Fedora

# Herdr (install script) — or: brew install herdr if you use Linuxbrew
curl -fsSL https://herdr.dev/install.sh | sh
# ensure the install dir is on PATH (script usually prints the path)
hash -r
herdr --version

# This repo
git clone <YOUR_FORK_OR_REMOTE_URL> herdr-agent-team
cd herdr-agent-team
chmod +x bin/herd bin/herd-tui bin/herd-init bin/herd-status bin/herd-update

# Optional: put herd on PATH (still points at this checkout)
mkdir -p "$HOME/.local/bin"
ln -sf "$(pwd)/bin/herd" "$HOME/.local/bin/herd"
ln -sf "$(pwd)/bin/herd-tui" "$HOME/.local/bin/herd-tui"
# ensure ~/.local/bin is on PATH in your shell rc

# Verify
./bin/herd help
./bin/herd-init --list-archetypes
herdr --version
```

### macOS

```bash
# Python + git (Xcode CLT or Homebrew)
xcode-select --install   # if needed
# or: brew install python git

# Herdr — Homebrew is the usual path on Mac
brew install herdr
# alternative: curl -fsSL https://herdr.dev/install.sh | sh
herdr --version

# This repo
git clone <YOUR_FORK_OR_REMOTE_URL> herdr-agent-team
cd herdr-agent-team
chmod +x bin/herd bin/herd-tui bin/herd-init bin/herd-status bin/herd-update

# Optional: PATH shims
mkdir -p "$HOME/.local/bin"
ln -sf "$(pwd)/bin/herd" "$HOME/.local/bin/herd"
ln -sf "$(pwd)/bin/herd-tui" "$HOME/.local/bin/herd-tui"
# add to ~/.zshrc if needed:
# export PATH="$HOME/.local/bin:$PATH"

# Verify
./bin/herd help
./bin/herd-init --list-archetypes
herdr --version
```

### Windows (WSL)

Native Windows Herdr is preview-only; **use WSL2** (Ubuntu recommended) for this toolchain.

```powershell
# From Windows: install WSL if needed
wsl --install
# reboot if prompted, then open Ubuntu (or your distro)
```

Inside **WSL**:

```bash
# Python + git
sudo apt update && sudo apt install -y git python3 curl ca-certificates

# Herdr (Linux binary inside WSL)
curl -fsSL https://herdr.dev/install.sh | sh
hash -r
herdr --version

# This repo (clone into the Linux filesystem, e.g. ~/src — not under /mnt/c if you can avoid it)
mkdir -p ~/src && cd ~/src
git clone <YOUR_FORK_OR_REMOTE_URL> herdr-agent-team
cd herdr-agent-team
chmod +x bin/herd bin/herd-tui bin/herd-init bin/herd-status bin/herd-update

# Optional: PATH shims
mkdir -p "$HOME/.local/bin"
ln -sf "$(pwd)/bin/herd" "$HOME/.local/bin/herd"
ln -sf "$(pwd)/bin/herd-tui" "$HOME/.local/bin/herd-tui"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify
./bin/herd help
./bin/herd-init --list-archetypes
herdr --version
```

**WSL tips**

- Run the TUI and Herdr **inside WSL**, not from PowerShell/cmd.  
- Prefer cloning under `~/…` in the Linux FS for performance.  
- Agent CLIs (`grok`, `claude`, …) must also be installed **in WSL** if you use `--seed-panes`.

### After install

Continue with [Onboarding](#onboarding) below (where to run, default `$PWD/<name>`, first walkthrough).  
Troubleshooting: [docs/faq/](docs/faq/README.md).

---

## Onboarding

### 1. Prerequisites

Already covered in [Install](#install). Short list:

- This repo checked out locally  
- Python 3 (stdlib only for the composer)  
- [Herdr](https://herdr.dev) on `PATH` if you want layout/seed/status  
- Agent CLIs you plan to seed if using `--seed-panes`

### 2. Where to run what

| Goal | Where to run |
|------|----------------|
| Walk through the **TUI** | **Plain terminal** (iTerm / Terminal / WezTerm) |
| **CLI** create / update / templates | Plain terminal |
| **See** tabs and agents after layout/seed | **Herdr UI** (new workspace named after the project) |
| Day-to-day multi-agent work | Herdr panes + `herdr agent prompt` |

Nested TUI inside a Herdr pane can work but is harder; prefer a normal terminal for `./bin/herd-tui`.

### 3. How you invoke the tools

Bins live in **this repo**. They are not a global install by default. They always load packs/agents from **this checkout**, regardless of your shell cwd:

```bash
cd /path/to/herdr-agent-team

./bin/herd help
./bin/herd-tui
./bin/herd status
```

From elsewhere:

```bash
/path/to/herdr-agent-team/bin/herd-tui
```

Optional: symlink `bin/herd` onto your `PATH` (still points at this checkout).

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
cd /path/to/herdr-agent-team
./bin/herd-tui
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
./bin/herd init --non-interactive --name visual-files \
  --archetype greenfield-web --no-git --no-herdr-layout --yes
ls ./visual-files

# B) Layout only (tabs, no agent start)
./bin/herd init --non-interactive --name visual-layout \
  --archetype blank --no-git --herdr-layout --no-seed-panes --yes
# → Herdr UI: workspace visual-layout

# C) Full path (layout + start agents + inject prompts)
./bin/herd init --non-interactive --name visual-full \
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
| “Command not found: herd” | Use `./bin/herd` from this repo (or absolute path / symlink) |
| “Layout failed but folder exists” | Expected — files still succeed; check `herdr` on PATH |
| Agents don’t talk | Must use Herdr messaging; board-only updates are not enough |

More detail: **[docs/faq/](docs/faq/README.md)**.

---

## Quick start (command cheat sheet)

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
bin/herd                 # init | status | update | template
bin/herd-tui             # curses wizard
bin/herd-init            # → init
composer/                # shared engine
archetypes/ packs/ agents/ protocols/ templates/ schemas/
docs/faq/                # FAQ (linked from this README)
```

## Agent communication

Mandatory Herdr messaging is baked into protocols, agent prompts, CONVENTIONS, TASKS, and boot prompts. Board updates alone are not enough — use `herdr agent prompt`.

## FAQ

See **[docs/faq/README.md](docs/faq/README.md)** for expanded answers (where to test, paths, bin vs repo, layout/seed, templates, update safety, etc.).
