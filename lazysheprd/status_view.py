"""US-07 — lightweight agent status across Herdr workspaces."""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

from .herdr_layout import HerdrLayoutError, ensure_herdr_server, herdr_bin


def _run_json(args: list[str]) -> dict[str, Any]:
    bin_path = herdr_bin()
    proc = subprocess.run(
        [bin_path, *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        raise HerdrLayoutError(f"herdr {' '.join(args)} failed: {err}")
    return json.loads(proc.stdout)


def collect_status() -> dict[str, Any]:
    ensure_herdr_server()
    workspaces = (_run_json(["workspace", "list"]).get("result") or {}).get("workspaces") or []
    agents = (_run_json(["agent", "list"]).get("result") or {}).get("agents") or []
    return {"workspaces": workspaces, "agents": agents}


def print_status(
    *,
    workspace_filter: str | None = None,
    as_json: bool = False,
) -> int:
    try:
        data = collect_status()
    except HerdrLayoutError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if as_json:
        print(json.dumps(data, indent=2))
        return 0

    workspaces = data["workspaces"]
    agents = data["agents"]
    if workspace_filter:
        workspaces = [
            w
            for w in workspaces
            if workspace_filter in (w.get("workspace_id") or "")
            or workspace_filter in (w.get("label") or "")
        ]
        ids = {w.get("workspace_id") for w in workspaces}
        agents = [a for a in agents if a.get("workspace_id") in ids]

    print("Workspaces")
    if not workspaces:
        print("  (none)")
    for w in workspaces:
        focus = "*" if w.get("focused") else " "
        print(
            f"  {focus} {w.get('workspace_id')}  {w.get('label') or ''}  "
            f"tabs={w.get('tab_count')} agents={w.get('agent_status')}"
        )

    print("\nAgents")
    if not agents:
        print("  (none)")
        print("\nTip: this is a light companion view — Herdr sidebar remains source of truth.")
        return 0

    # columns
    rows = []
    for a in agents:
        rows.append(
            {
                "state": a.get("agent_status") or "unknown",
                "name": a.get("name") or a.get("agent") or "-",
                "kind": a.get("agent") or "-",
                "ws": a.get("workspace_id") or "-",
                "pane": a.get("pane_id") or "-",
                "tab": a.get("tab_id") or "-",
                "cwd": a.get("cwd") or a.get("foreground_cwd") or "",
            }
        )

    # group by state priority
    order = {"blocked": 0, "working": 1, "unknown": 2, "idle": 3, "done": 4}
    rows.sort(key=lambda r: (order.get(str(r["state"]), 9), str(r["ws"]), str(r["name"])))

    for r in rows:
        icon = {
            "working": "…",
            "idle": "·",
            "done": "✓",
            "blocked": "!",
            "unknown": "?",
        }.get(str(r["state"]), "?")
        print(
            f"  {icon} {r['state']:<8}  {r['name']:<24}  {r['kind']:<8}  "
            f"{r['ws']}  {r['pane']}  {r['cwd'][:40]}"
        )

    print("\nJump:")
    print("  herdr workspace focus <workspace_id>")
    print("  herdr agent focus <name-or-pane>")
    print("  (Herdr sidebar is still the primary UI)")
    return 0


def focus_target(target: str) -> int:
    """Focus a workspace id (wN) or agent name/pane."""
    try:
        ensure_herdr_server()
        if target.startswith("w") and ":" not in target:
            _run_json(["workspace", "focus", target])
            print(f"focused workspace {target}")
            return 0
        _run_json(["agent", "focus", target])
        print(f"focused agent {target}")
        return 0
    except HerdrLayoutError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
