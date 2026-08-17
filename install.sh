#!/usr/bin/env bash
# Install LazySheprd (lazysheprd) onto your PATH via ~/.local/bin
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${LAZYSHEPRD_BIN_DIR:-$HOME/.local/bin}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 not found. Install Python 3 and re-run." >&2
  exit 1
fi

mkdir -p "$BIN_DIR"

TOOLS=(lazysheprd lazysheprd-tui lazysheprd-init lazysheprd-status lazysheprd-update)
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

# Remove legacy herd* shims from pre-rebrand installs of this project
LEGACY=(herd herd-tui herd-init herd-status herd-update)
for old in "${LEGACY[@]}"; do
  target="$BIN_DIR/$old"
  if [[ -L "$target" ]]; then
    link="$(readlink "$target" || true)"
    case "$link" in
      "$ROOT/bin/"*|*/herdr-agent-team/bin/*|*/lazysheprd/bin/*)
        rm -f "$target"
        echo "removed old shim  $target"
        ;;
    esac
  fi
done

echo
echo "✅ LazySheprd installed"
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
  echo "  lazysheprd help"
  echo "  lazysheprd-tui"
  echo
fi

echo "Uninstall:  ./uninstall.sh"
echo "Projects default to \$PWD/<name> when you run lazysheprd init / lazysheprd-tui."
