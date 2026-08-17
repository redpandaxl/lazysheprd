from __future__ import annotations

from pathlib import Path

# composer/ is inside the template repo root
TEMPLATE_ROOT = Path(__file__).resolve().parent.parent
PACKS_DIR = TEMPLATE_ROOT / "packs"
ARCHETYPES_DIR = TEMPLATE_ROOT / "archetypes"
DEFAULT_PACK = "software-delivery"
OPS_ID = "ops"

# Herdr-supported kinds (from `herdr agent start --kind`) plus explicit aliases.
KNOWN_KINDS = [
    "grok",
    "claude",
    "codex",
    "cursor",
    "gemini",
    "copilot",
    "opencode",
    "pi",
    "amp",
    "droid",
    "hermes",
    "kilo",
    "other",
]

EFFORTS = ["low", "medium", "high", "max"]
