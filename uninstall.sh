#!/usr/bin/env bash
# Remove LazySheprd symlinks from ~/.local/bin (does not delete the repo)
set -euo pipefail

BIN_DIR="${LAZYSHEPRD_BIN_DIR:-$HOME/.local/bin}"
TOOLS=(
  lazysheprd
  lazysheprd-tui
  lazysheprd-init
  lazysheprd-status
  lazysheprd-update
  # legacy names from pre-rebrand installs
  herd
  herd-tui
  herd-init
  herd-status
  herd-update
)

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
