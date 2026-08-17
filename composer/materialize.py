from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from .packs import OPS_ID, ensure_ops_enabled
from .paths import TEMPLATE_ROOT
from .yamlutil import dump_yaml


def target_nonempty(path: Path) -> bool:
    return path.exists() and any(path.iterdir())


def build_team(
    *,
    name: str,
    target: Path,
    pack: dict[str, Any],
    personas: list[dict[str, Any]],
    archetype_id: str | None = None,
) -> dict[str, Any]:
    ensure_ops_enabled(personas)
    defaults = pack.get("defaults") or {}
    enabled = [p for p in personas if p["enabled"]]
    domain = pack.get("domain") or (
        "software" if pack.get("id") == "software-delivery" else pack.get("id") or "software"
    )
    team_personas = []
    for p in personas:
        basename = Path(p["prompt_source"]).name
        team_personas.append(
            {
                "id": p["id"],
                "role": p["role"],
                "title": p["title"],
                "enabled": bool(p["enabled"]),
                "tab": p["tab"],
                "agent_kind": p["agent_kind"],
                "model": p["model"],
                "effort": p["effort"],
                "prompt_file": f"agents/{basename}",
                "boot_prompt": p["boot_prompt"],
            }
        )
    team: dict[str, Any] = {
        "version": 1,
        "project": {
            "name": name,
            "domain": domain,
            "cwd": str(target),
        },
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
    if archetype_id:
        team["project"]["archetype"] = archetype_id
    return team


def materialize(
    *,
    name: str,
    target: Path,
    pack: dict[str, Any],
    personas: list[dict[str, Any]],
    tasks_markdown: str | None = None,
    git_init: bool = False,
    git_commit: bool = False,
    archetype_id: str | None = None,
) -> Path:
    if target_nonempty(target):
        raise SystemExit(f"Error: {target} exists and is not empty")

    templates = TEMPLATE_ROOT / "templates"
    protocols = TEMPLATE_ROOT / "protocols"
    conventions = templates / "CONVENTIONS.md"
    tasks_default = templates / "TASKS.md"
    for required in (conventions, tasks_default, protocols):
        if not required.exists():
            raise SystemExit(f"missing template file: {required}")

    target.mkdir(parents=True, exist_ok=True)
    shutil.copy(conventions, target / "CONVENTIONS.md")

    if tasks_markdown and tasks_markdown.strip():
        (target / "TASKS.md").write_text(tasks_markdown, encoding="utf-8")
    else:
        shutil.copy(tasks_default, target / "TASKS.md")

    shutil.copytree(protocols, target / "protocols")
    agents_dir = target / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    for persona in personas:
        if not persona["enabled"]:
            continue
        src = TEMPLATE_ROOT / persona["prompt_source"]
        if not src.is_file():
            raise SystemExit(f"missing prompt_source: {src}")
        shutil.copy(src, agents_dir / src.name)

    team = build_team(
        name=name,
        target=target,
        pack=pack,
        personas=personas,
        archetype_id=archetype_id,
    )
    (target / "team.yaml").write_text(dump_yaml(team), encoding="utf-8")

    if git_init:
        _git_init(target, commit=git_commit, name=name)

    return target


def _git_init(target: Path, *, commit: bool, name: str) -> None:
    try:
        subprocess.run(
            ["git", "init"],
            cwd=target,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"git init failed: {exc}") from exc
    if not commit:
        return
    subprocess.run(["git", "add", "-A"], cwd=target, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"Initial scaffold for {name}"],
        cwd=target,
        check=True,
        capture_output=True,
    )


def print_next_steps(
    target: Path,
    team: dict[str, Any],
    *,
    herdr_layout: dict[str, Any] | None = None,
    herdr_layout_error: str | None = None,
    seed_report: dict[str, Any] | None = None,
    seed_error: str | None = None,
) -> None:
    print(f"✅ Project scaffolded at {target}")
    print()
    print("Next steps:")
    n = 1
    print(f"{n}. cd {target}")
    n += 1

    if herdr_layout:
        print(
            f"{n}. Herdr layout ready: workspace "
            f"{herdr_layout.get('workspace_label')} "
            f"({herdr_layout.get('workspace_id')})"
        )
        n += 1
        tabs = ", ".join(t.get("label", "") for t in herdr_layout.get("tabs") or [])
        print(f"{n}. Tabs: {tabs}")
        n += 1
        print(f"{n}. Focused on that workspace (open/attach Herdr client if needed).")
        n += 1
    elif herdr_layout_error:
        print(f"{n}. Herdr layout skipped/failed: {herdr_layout_error}")
        n += 1
        print(f"{n}. herdr  # then create tabs manually")
        n += 1
        tabs = ", ".join(t["id"] for t in team["layout"]["tabs"])
        print(f"{n}. Create tabs: {tabs} (+ services if desired)")
        n += 1
    else:
        print(f"{n}. herdr")
        n += 1
        tabs = ", ".join(t["id"] for t in team["layout"]["tabs"])
        print(f"{n}. Create tabs from team.yaml layout: {tabs}")
        n += 1

    if seed_report and seed_report.get("seeded_count", 0) > 0:
        print(f"{n}. Agents seeded — use Herdr sidebar to jump between panes.")
        n += 1
        print(f"{n}. Tell Ops (or focus ops pane) to begin from TASKS.md.")
        n += 1
    else:
        if seed_error:
            print(f"{n}. Seed note: {seed_error}")
            n += 1
        print(f"{n}. Start each enabled agent (manual):")
        n += 1
        herdr_tabs = {
            t.get("label"): t
            for t in (herdr_layout or {}).get("tabs") or []
            if t.get("label")
        }
        for p in team["personas"]:
            if not p["enabled"]:
                continue
            extra = ""
            if p.get("model"):
                extra += f" --model {p['model']}"
            if p.get("effort"):
                extra += f" --effort {p['effort']}"
            pane_hint = f"<tab:{p['tab']}>"
            rec = herdr_tabs.get(p["tab"]) or herdr_tabs.get(p["id"])
            if rec and rec.get("pane_id"):
                pane_hint = rec["pane_id"]
            print(
                f"   herdr agent start {p['id']} --kind {p['agent_kind']} "
                f"--pane {pane_hint}{extra}"
            )
            print("   (model/effort are stored intent; flags vary by agent kind)")
        print(f"{n}. Paste/use agents/*.md; boot with team.yaml boot_prompt.")
        n += 1
    print(f"{n}. Communication is MANDATORY via Herdr (not pane-watching):")
    print("   - Read protocols/herdr-messaging.md + protocols/coordination.md")
    print("   - Assign/unblock/review with: herdr agent prompt <name> \"...\"")
    print("   - TASKS.md updates alone are not enough — always message agents")
    n += 1
    ops = next(p for p in team["personas"] if p["id"] == OPS_ID)
    print(f"{n}. Ops boot line (if not already seeded):")
    print(f"   {ops['boot_prompt']}")
