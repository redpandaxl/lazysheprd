from __future__ import annotations

from pathlib import Path

# composer/ is inside the template repo root
TEMPLATE_ROOT = Path(__file__).resolve().parent.parent
PACKS_DIR = TEMPLATE_ROOT / "packs"
ARCHETYPES_DIR = TEMPLATE_ROOT / "archetypes"
DEFAULT_PACK = "software-delivery"
OPS_ID = "ops"


def default_project_dir(name: str, *, explicit: Path | None = None) -> Path:
    """Default scaffold path: $PWD/<name>, unless cwd is already <name>.

    Avoids nested team_test/team_test when the user is already in a folder
    named like the project.
    """
    if explicit is not None:
        return explicit.expanduser().resolve()
    cwd = Path.cwd().resolve()
    if cwd.name == name:
        return cwd
    return (cwd / name).resolve()

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
