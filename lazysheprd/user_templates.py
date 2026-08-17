"""US-06 — save / load local team templates (JSON under user config)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import DEFAULT_PACK


def templates_dir() -> Path:
    """User templates live under ~/.config/lazysheprd/templates.

    Also reads legacy ~/.config/herd-compose/templates if present.
    """
    base = Path.home() / ".config" / "lazysheprd" / "templates"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _legacy_templates_dir() -> Path:
    return Path.home() / ".config" / "herd-compose" / "templates"


def _safe_id(name: str) -> str:
    slug = re.sub(r"[^a-z0-9_-]+", "-", name.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    if not slug:
        raise SystemExit("template name must contain letters or numbers")
    return slug[:64]


def template_path(template_id: str) -> Path:
    return templates_dir() / f"{_safe_id(template_id)}.json"


def list_templates() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    dirs = [templates_dir()]
    legacy = _legacy_templates_dir()
    if legacy.is_dir():
        dirs.append(legacy)
    for directory in dirs:
        for path in sorted(directory.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(data, dict):
                continue
            tid = str(data.get("id") or path.stem)
            if tid in seen:
                continue
            seen.add(tid)
            data.setdefault("id", tid)
            data["_path"] = str(path)
            items.append(data)
    return items


def load_template(template_id: str) -> dict[str, Any]:
    path = template_path(template_id)
    if not path.is_file():
        legacy = _legacy_templates_dir() / f"{_safe_id(template_id)}.json"
        if legacy.is_file():
            path = legacy
        else:
            known = ", ".join(t.get("id", "?") for t in list_templates()) or "(none)"
            raise SystemExit(f"unknown template {template_id!r}; available: {known}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"invalid template file: {path}")
    data.setdefault("id", path.stem)
    return data


def plan_from_template(template: dict[str, Any], *, name: str, target: Path) -> dict[str, Any]:
    """Build a partial plan dict from a saved template (caller fills pack/tasks)."""
    from .archetypes import load_archetype, tasks_markdown_for
    from .packs import apply_defaults, load_pack

    pack_id = template.get("pack_id") or DEFAULT_PACK
    pack = load_pack(pack_id)
    personas = apply_defaults(pack)
    saved = {p["id"]: p for p in (template.get("personas") or []) if isinstance(p, dict)}
    for persona in personas:
        sp = saved.get(persona["id"])
        if not sp:
            continue
        if "enabled" in sp:
            persona["enabled"] = bool(sp["enabled"])
        for key in ("agent_kind", "model", "effort"):
            if key in sp:
                persona[key] = sp[key]
    archetype_id = template.get("archetype_id") or "blank"
    archetype = load_archetype(archetype_id)
    return {
        "name": name,
        "target": target,
        "pack": pack,
        "personas": personas,
        "archetype_id": archetype_id,
        "tasks_markdown": tasks_markdown_for(archetype, name),
        "git_init": bool(template.get("git_init", False)),
        "git_commit": bool(template.get("git_commit", False)),
        "herdr_layout": bool(template.get("herdr_layout", False)),
        "seed_panes": bool(template.get("seed_panes", False)),
        "template_id": template.get("id"),
    }


def save_template_from_plan(
    plan: dict[str, Any],
    *,
    template_id: str,
    title: str | None = None,
    overwrite: bool = False,
) -> Path:
    tid = _safe_id(template_id)
    path = template_path(tid)
    if path.exists() and not overwrite:
        raise SystemExit(f"template {tid!r} exists; pass --force to overwrite")

    pack = plan.get("pack") or {}
    personas_out = []
    for p in plan.get("personas") or []:
        personas_out.append(
            {
                "id": p.get("id"),
                "enabled": bool(p.get("enabled", True)),
                "agent_kind": p.get("agent_kind"),
                "model": p.get("model"),
                "effort": p.get("effort"),
                "tab": p.get("tab"),
                "title": p.get("title"),
            }
        )
    payload = {
        "id": tid,
        "title": title or tid,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pack_id": pack.get("id") or DEFAULT_PACK,
        "archetype_id": plan.get("archetype_id") or "blank",
        "git_init": bool(plan.get("git_init")),
        "git_commit": bool(plan.get("git_commit")),
        "herdr_layout": bool(plan.get("herdr_layout")),
        "seed_panes": bool(plan.get("seed_panes")),
        "personas": personas_out,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def delete_template(template_id: str) -> None:
    path = template_path(template_id)
    if not path.is_file():
        raise SystemExit(f"unknown template {template_id!r}")
    path.unlink()


def print_templates() -> int:
    items = list_templates()
    if not items:
        print(f"(no templates in {templates_dir()})")
        return 0
    width = max(len(str(t.get("id", ""))) for t in items)
    for t in items:
        title = t.get("title") or ""
        arch = t.get("archetype_id") or ""
        print(f"{t.get('id', ''):<{width}}  {title}  archetype={arch}")
    return 0
