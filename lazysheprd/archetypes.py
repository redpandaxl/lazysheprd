from __future__ import annotations

from pathlib import Path
from typing import Any

from .paths import ARCHETYPES_DIR
from .yamlutil import load_yaml


def iter_archetypes() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if not ARCHETYPES_DIR.is_dir():
        return items
    for path in sorted(ARCHETYPES_DIR.glob("*.yaml")):
        data = load_yaml(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "id" not in data:
            raise SystemExit(f"invalid archetype: {path}")
        data["_path"] = str(path)
        items.append(data)
    return items


def load_archetype(archetype_id: str) -> dict[str, Any]:
    path = ARCHETYPES_DIR / f"{archetype_id}.yaml"
    if not path.is_file():
        known = ", ".join(a["id"] for a in iter_archetypes()) or "(none)"
        raise SystemExit(f"unknown archetype {archetype_id!r}; available: {known}")
    data = load_yaml(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"invalid archetype: {path}")
    return data


def tasks_markdown_for(archetype: dict[str, Any], project_name: str) -> str:
    """Return TASKS.md body. Prefer external file, else inline tasks_markdown."""
    tasks_file = archetype.get("tasks_file")
    if tasks_file:
        path = Path(tasks_file)
        if not path.is_absolute():
            path = ARCHETYPES_DIR / path
        text = path.read_text(encoding="utf-8")
    else:
        text = archetype.get("tasks_markdown") or ""
        if not text:
            # fall back to blank template later in materialize
            return ""
    return text.replace("{{PROJECT_NAME}}", project_name)
