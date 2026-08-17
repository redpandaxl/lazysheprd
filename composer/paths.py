from __future__ import annotations

from pathlib import Path

# composer/ is inside the template repo root
TEMPLATE_ROOT = Path(__file__).resolve().parent.parent
PACKS_DIR = TEMPLATE_ROOT / "packs"
ARCHETYPES_DIR = TEMPLATE_ROOT / "archetypes"
DEFAULT_PACK = "software-delivery"
OPS_ID = "ops"

# Herdr-supported kinds (from `herdr agent start --kind`) plus explicit aliases.
# Order = pick-list order; first entries are the common defaults users should see.
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

# Short labels for TUI pick lists (id → help text).
KIND_HELP = {
    "grok": "xAI Grok (good default ops / general)",
    "claude": "Anthropic Claude (strong review / QA)",
    "codex": "OpenAI Codex (strong implementation)",
    "cursor": "Cursor agent",
    "gemini": "Google Gemini",
    "copilot": "GitHub Copilot CLI",
    "opencode": "OpenCode",
    "pi": "Pi",
    "amp": "Amp",
    "droid": "Droid",
    "hermes": "Hermes",
    "kilo": "Kilo",
    "other": "Other / custom (set model string if needed)",
}

EFFORTS = ["low", "medium", "high", "max"]
DEFAULT_EFFORT = "medium"

EFFORT_HELP = {
    "low": "Faster, lighter",
    "medium": "Balanced (recommended default)",
    "high": "Deeper reasoning",
    "max": "Maximum effort when available",
}
