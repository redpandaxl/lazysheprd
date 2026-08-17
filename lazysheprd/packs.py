from __future__ import annotations

from typing import Any

from .paths import DEFAULT_PACK, OPS_ID, PACKS_DIR
from .yamlutil import load_yaml


def iter_packs() -> list[dict[str, Any]]:
    packs: list[dict[str, Any]] = []
    if not PACKS_DIR.is_dir():
        return packs
    for path in sorted(PACKS_DIR.iterdir()):
        pack_file = path / "pack.yaml"
        if path.is_dir() and pack_file.is_file():
            data = load_yaml(pack_file.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or "id" not in data:
                raise SystemExit(f"invalid pack: {pack_file}")
            packs.append(data)
    return packs


def load_pack(pack_id: str) -> dict[str, Any]:
    pack_file = PACKS_DIR / pack_id / "pack.yaml"
    if not pack_file.is_file():
        known = ", ".join(p["id"] for p in iter_packs()) or "(none)"
        raise SystemExit(f"unknown pack {pack_id!r}; available: {known}")
    data = load_yaml(pack_file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"invalid pack: {pack_file}")
    return data


def apply_defaults(pack: dict[str, Any]) -> list[dict[str, Any]]:
    defaults = pack.get("defaults") or {}
    personas: list[dict[str, Any]] = []
    for raw in pack.get("personas") or []:
        if not isinstance(raw, dict):
            raise SystemExit("pack persona must be a map")
        persona = {
            "id": raw["id"],
            "role": raw.get("role") or raw["id"],
            "title": raw.get("title") or raw["id"],
            "description": raw.get("description") or "",
            "enabled": True,
            "tab": raw.get("tab") or raw["id"],
            "agent_kind": raw.get("agent_kind")
            if raw.get("agent_kind") is not None
            else defaults.get("agent_kind"),
            "model": raw["model"] if "model" in raw else defaults.get("model"),
            "effort": raw["effort"] if "effort" in raw else defaults.get("effort"),
            "prompt_source": raw["prompt_source"],
            "boot_prompt": raw.get("boot_prompt") or "",
        }
        if not persona["agent_kind"]:
            raise SystemExit(f"persona {persona['id']} missing agent_kind")
        personas.append(persona)
    return personas


def _field_slot(parts: list[str], idx: int) -> tuple[bool, Any]:
    if len(parts) <= idx:
        return False, None
    raw = parts[idx]
    if raw in ("", "-"):
        return True, None
    return True, raw


def parse_persona_fields(reply: str) -> tuple[str | None, tuple[bool, Any], tuple[bool, Any]]:
    reply = reply.strip()
    if not reply:
        raise SystemExit("invalid persona fields: empty")
    parts = reply.split(":", 2)
    kind = parts[0] if parts[0] != "" else None
    return kind, _field_slot(parts, 1), _field_slot(parts, 2)


def parse_persona_override(spec: str) -> tuple[str, str | None, tuple[bool, Any], tuple[bool, Any]]:
    parts = spec.split(":", 3)
    if not parts or not parts[0]:
        raise SystemExit(f"invalid --persona {spec!r}; expected id:kind:model:effort")
    pid = parts[0]
    kind = parts[1] if len(parts) > 1 and parts[1] != "" else None
    return pid, kind, _field_slot(parts, 2), _field_slot(parts, 3)


def apply_persona_fields(
    persona: dict[str, Any],
    kind: str | None,
    model_slot: tuple[bool, Any],
    effort_slot: tuple[bool, Any],
) -> None:
    if kind:
        persona["agent_kind"] = kind
    model_set, model = model_slot
    effort_set, effort = effort_slot
    if model_set:
        persona["model"] = model
    if effort_set:
        persona["effort"] = effort


def apply_overrides(personas: list[dict[str, Any]], specs: list[str]) -> None:
    by_id = {p["id"]: p for p in personas}
    for spec in specs:
        pid, kind, model_slot, effort_slot = parse_persona_override(spec)
        if pid not in by_id:
            known = ", ".join(by_id)
            raise SystemExit(f"unknown persona {pid!r} in --persona; known: {known}")
        apply_persona_fields(by_id[pid], kind, model_slot, effort_slot)


def validate_project_name(name: str) -> str:
    import os
    from pathlib import Path

    if name is None or not str(name).strip():
        raise SystemExit("Error: project name is required")
    name = str(name).strip()
    seps = {os.sep, os.altsep, "/", "\\"} - {None}
    if any(sep in name for sep in seps):
        raise SystemExit(
            f"Error: project name {name!r} must be a single path segment "
            f"(no slashes). Use --dir for a custom location."
        )
    if Path(name).is_absolute():
        raise SystemExit(
            f"Error: project name {name!r} must not be an absolute path. "
            f"Use --dir for a custom location."
        )
    parts = Path(name).parts
    if name in (".", "..") or any(part in (".", "..") for part in parts):
        raise SystemExit(
            f"Error: project name {name!r} must not be '.' or '..' "
            f"or contain '..' segments. Use --dir for a custom location."
        )
    return name


def ensure_ops_enabled(personas: list[dict[str, Any]]) -> None:
    if not any(p["id"] == OPS_ID and p.get("enabled") for p in personas):
        raise SystemExit("ops must stay enabled")
