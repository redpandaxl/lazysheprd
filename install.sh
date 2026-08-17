#!/usr/bin/env bash
# Install herdr-agent-team (agent builder) onto your PATH via ~/.local/bin
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HERD_BIN_DIR:-$HOME/.local/bin}"

need_python() {
  if ! command -v python3 >/dev/null 2>&1; then
    echo "error: python3 not found. Install Python 3 and re-run." >&2
    exit 1
  fi
}

need_python

mkdir -p "$BIN_DIR"

TOOLS=(herd herd-tui herd-init herd-status herd-update)
for name in "${TOOLS[@]}"; do
  src="$ROOT/bin/$name"
  if [[ ! -f "$src" ]]; then
    echo "error: missing $src" >&2
    exit 1
  fi
  chmod +x "$src"
  ln -sfn "$src" "$BIN_DIR/$name"
  echo "linked  $BIN_DIR/$name  →  $src"
done

# Ensure wrappers still resolve the repo (they already use path relative to bin/)
echo
echo "✅ herdr-agent-team installed"
echo "   repo: $ROOT"
echo "   bins: $BIN_DIR"
echo

if ! echo ":$PATH:" | grep -q ":$BIN_DIR:"; then
  echo "Add this to your shell config (~/.bashrc / ~/.zshrc), then open a new terminal:"
  echo
  echo "  export PATH=\"$BIN_DIR:\$PATH\""
  echo
else
  echo "PATH already includes $BIN_DIR — try:"
  echo
  echo "  herd help"
  echo "  herd-tui"
  echo
fi

echo "Uninstall:  ./uninstall.sh"
echo "Projects default to \$PWD/<name> when you run herd init / herd-tui."
