#!/usr/bin/env bash
# Remove herdr-agent-team symlinks from ~/.local/bin (does not delete the repo)
set -euo pipefail

BIN_DIR="${HERD_BIN_DIR:-$HOME/.local/bin}"
TOOLS=(herd herd-tui herd-init herd-status herd-update)

for name in "${TOOLS[@]}"; do
  target="$BIN_DIR/$name"
  if [[ -L "$target" ]]; then
    rm -f "$target"
    echo "removed $target"
  elif [[ -e "$target" ]]; then
    echo "skip $target (not a symlink — remove manually if you want)"
  fi
done

echo "✅ uninstall done (repo checkout left in place)"
