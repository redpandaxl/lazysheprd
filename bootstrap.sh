#!/usr/bin/env bash
set -euo pipefail

TEMPLATE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PROJECT_NAME=${1:-}
if [[ -z "$PROJECT_NAME" ]]; then
  echo "Usage: ./bootstrap.sh <project-name>" >&2
  exit 1
fi

TARGET="${PWD}/$PROJECT_NAME"

if [[ -e "$TARGET" ]] && [[ -n "$(ls -A "$TARGET" 2>/dev/null)" ]]; then
  echo "Error: $TARGET exists and is not empty" >&2
  exit 1
fi

mkdir -p "$TARGET"

cp "$TEMPLATE_ROOT/templates/CONVENTIONS.md" "$TARGET/CONVENTIONS.md"
cp "$TEMPLATE_ROOT/templates/TASKS.md" "$TARGET/TASKS.md"
cp -r "$TEMPLATE_ROOT/protocols" "$TARGET/"
mkdir -p "$TARGET/agents"
cp "$TEMPLATE_ROOT/agents/"*.md "$TARGET/agents/"

echo "✅ Project scaffolded at $TARGET"
echo ""
echo "Next steps:"
echo "1. cd $TARGET"
echo "2. herdr"
echo "3. Create the standard tabs: ops, infra, dev, design, qa, services"
echo "4. Paste the contents of agents/*.md into each corresponding pane"
echo "5. Agents MUST coordinate via Herdr messaging (see protocols/herdr-messaging.md)."
echo "   Board updates alone are not enough — use: herdr agent prompt <name> \"...\""
echo "6. Boot Ops with:"
echo "   Read CONVENTIONS.md, TASKS.md, protocols/coordination.md, and"
echo "   protocols/herdr-messaging.md. Assign and hand off only via herdr agent prompt."
echo "   Never assume pane watching. Begin."
