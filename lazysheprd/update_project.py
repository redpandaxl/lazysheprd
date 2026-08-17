"""US-08 — update an existing project agent config without clobbering customs."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .packs import OPS_ID, apply_defaults, apply_overrides, load_pack
from .paths import DEFAULT_PACK, TEMPLATE_ROOT
from .yamlutil import dump_yaml, load_yaml


def is_project_dir(path: Path) -> bool:
    return (path / "CONVENTIONS.md").is_file() or (path / "agents").is_dir() or (
        path / "team.yaml"
    ).is_file()


def load_existing_team(path: Path) -> dict[str, Any] | None:
    team_path = path / "team.yaml"
    if not team_path.is_file():
        return None
    data = load_yaml(team_path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else None


def detect_agent_files(path: Path) -> list[str]:
    agents = path / "agents"
    if not agents.is_dir():
        return []
    return sorted(p.stem for p in agents.glob("*.md"))


def build_update_plan(
    project_dir: Path,
    *,
    pack_id: str = DEFAULT_PACK,
    persona_specs: list[str] | None = None,
    enable: list[str] | None = None,
    disable: list[str] | None = None,
) -> dict[str, Any]:
    """Merge pack personas with existing team.yaml / agents/."""
    pack = load_pack(pack_id)
    personas = apply_defaults(pack)
    existing = load_existing_team(project_dir)
    existing_by_id: dict[str, Any] = {}
    if existing:
        for p in existing.get("personas") or []:
            if isinstance(p, dict) and p.get("id"):
                existing_by_id[str(p["id"])] = p

    on_disk = set(detect_agent_files(project_dir))

    for persona in personas:
        pid = persona["id"]
        prev = existing_by_id.get(pid)
        if prev:
            persona["enabled"] = bool(prev.get("enabled", True))
            for key in ("agent_kind", "model", "effort", "boot_prompt"):
                if key in prev and prev[key] is not None:
                    persona[key] = prev[key]
        elif pid in on_disk:
            persona["enabled"] = True
        else:
            # New pack role not in project yet — off until explicitly enabled
            # except ops
            persona["enabled"] = pid == OPS_ID

    if persona_specs:
        apply_overrides(personas, persona_specs)

    enable_set = set(enable or [])
    disable_set = set(disable or [])
    for persona in personas:
        if persona["id"] in enable_set:
            persona["enabled"] = True
        if persona["id"] in disable_set:
            if persona["id"] == OPS_ID:
                continue
            persona["enabled"] = False

    return {
        "project_dir": project_dir,
        "pack": pack,
        "personas": personas,
        "existing_team": existing,
        "on_disk_agents": sorted(on_disk),
    }


def apply_update(
    plan: dict[str, Any],
    *,
    force_prompts: bool = False,
    force_protocols: bool = False,
    write_team: bool = True,
) -> dict[str, Any]:
    """Apply update. Returns a change report."""
    project_dir: Path = plan["project_dir"]
    pack = plan["pack"]
    personas: list[dict[str, Any]] = plan["personas"]
    existing = plan.get("existing_team")

    if not is_project_dir(project_dir):
        raise SystemExit(
            f"{project_dir} does not look like a LazySheprd project "
            "(need CONVENTIONS.md, agents/, or team.yaml)"
        )

    agents_dir = project_dir / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    report: dict[str, Any] = {
        "added_prompts": [],
        "skipped_prompts": [],
        "updated_prompts": [],
        "disabled": [],
        "enabled": [],
        "protocols": None,
        "team_yaml": None,
    }

    for persona in personas:
        pid = persona["id"]
        if not persona.get("enabled"):
            report["disabled"].append(pid)
            continue
        report["enabled"].append(pid)
        src = TEMPLATE_ROOT / persona["prompt_source"]
        dest = agents_dir / Path(persona["prompt_source"]).name
        if not src.is_file():
            continue
        existed = dest.exists()
        if existed and not force_prompts:
            report["skipped_prompts"].append(dest.name)
            continue
        shutil.copy(src, dest)
        if existed:
            report["updated_prompts"].append(dest.name)
        else:
            report["added_prompts"].append(dest.name)

    if force_protocols:
        proto_src = TEMPLATE_ROOT / "protocols"
        proto_dst = project_dir / "protocols"
        if proto_src.is_dir():
            if proto_dst.exists():
                shutil.rmtree(proto_dst)
            shutil.copytree(proto_src, proto_dst)
            report["protocols"] = "replaced"
    else:
        # ensure messaging file exists if protocols dir present
        proto_dst = project_dir / "protocols"
        msg_src = TEMPLATE_ROOT / "protocols" / "herdr-messaging.md"
        msg_dst = proto_dst / "herdr-messaging.md"
        if proto_dst.is_dir() and msg_src.is_file() and not msg_dst.exists():
            shutil.copy(msg_src, msg_dst)
            report["protocols"] = "added herdr-messaging.md"

    if write_team:
        name = project_dir.name
        domain = "software"
        cwd = str(project_dir.resolve())
        if existing:
            proj = existing.get("project") or {}
            name = proj.get("name") or name
            domain = proj.get("domain") or domain
            cwd = proj.get("cwd") or cwd

        enabled = [p for p in personas if p.get("enabled")]
        team_personas = []
        for p in personas:
            basename = Path(p["prompt_source"]).name
            team_personas.append(
                {
                    "id": p["id"],
                    "role": p.get("role") or p["id"],
                    "title": p.get("title") or p["id"],
                    "enabled": bool(p.get("enabled")),
                    "tab": p.get("tab") or p["id"],
                    "agent_kind": p.get("agent_kind"),
                    "model": p.get("model"),
                    "effort": p.get("effort"),
                    "prompt_file": f"agents/{basename}",
                    "boot_prompt": p.get("boot_prompt") or "",
                }
            )
        defaults = pack.get("defaults") or {}
        team: dict[str, Any] = {
            "version": 1,
            "project": {"name": name, "domain": domain, "cwd": cwd},
            "defaults": {
                "agent_kind": defaults.get("agent_kind") or "grok",
                "model": defaults.get("model"),
                "effort": defaults.get("effort"),
            },
            "layout": {
                "strategy": "tab_per_persona",
                "tabs": [{"id": p["tab"], "label": p["title"]} for p in enabled],
            },
            "personas": team_personas,
        }
        # preserve herdr block if present
        if existing and existing.get("herdr"):
            team["herdr"] = existing["herdr"]
        if existing and (existing.get("project") or {}).get("archetype"):
            team["project"]["archetype"] = existing["project"]["archetype"]

        (project_dir / "team.yaml").write_text(dump_yaml(team), encoding="utf-8")
        report["team_yaml"] = "written"

    # never touch CONVENTIONS.md here
    report["conventions"] = "preserved"

    return report


def print_update_report(report: dict[str, Any]) -> None:
    print("Update complete")
    print(f"  enabled:  {', '.join(report.get('enabled') or []) or '(none)'}")
    print(f"  disabled: {', '.join(report.get('disabled') or []) or '(none)'}")
    print(f"  prompts added:   {', '.join(report.get('added_prompts') or []) or '(none)'}")
    print(f"  prompts updated: {', '.join(report.get('updated_prompts') or []) or '(none)'}")
    print(f"  prompts skipped: {', '.join(report.get('skipped_prompts') or []) or '(none)'} (use --force-prompts)")
    print(f"  protocols: {report.get('protocols') or 'unchanged'}")
    print(f"  team.yaml: {report.get('team_yaml') or 'unchanged'}")
    print(f"  CONVENTIONS.md: {report.get('conventions')}")
