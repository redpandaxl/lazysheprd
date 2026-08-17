"""US-04 — optional Herdr workspace + tab layout after materialize."""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any


class HerdrLayoutError(Exception):
    """Raised when Herdr layout setup fails (files still succeed)."""


def herdr_bin() -> str:
    path = shutil.which("herdr")
    if not path:
        raise HerdrLayoutError(
            "herdr not found on PATH. Install Herdr, then re-run layout setup."
        )
    return path


def _run_json(args: list[str], *, timeout: float = 60) -> dict[str, Any]:
    bin_path = herdr_bin()
    try:
        proc = subprocess.run(
            [bin_path, *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise HerdrLayoutError(f"herdr timed out: {' '.join(args)}") from exc
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    if proc.returncode != 0:
        raise HerdrLayoutError(
            f"herdr {' '.join(args)} failed (exit {proc.returncode}): {err or out or 'no output'}"
        )
    if not out:
        raise HerdrLayoutError(f"herdr {' '.join(args)} returned empty stdout")
    try:
        return json.loads(out)
    except json.JSONDecodeError as exc:
        raise HerdrLayoutError(
            f"herdr {' '.join(args)} did not return JSON: {out[:200]}"
        ) from exc


def ensure_herdr_server() -> None:
    """Ensure the Herdr server is reachable. Start headless server if needed."""
    bin_path = herdr_bin()
    try:
        proc = subprocess.run(
            [bin_path, "status"],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except subprocess.TimeoutExpired as exc:
        raise HerdrLayoutError("herdr status timed out") from exc

    text = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if "status: running" in text or "compatible: yes" in text:
        return

    # Start headless server (no TUI attach).
    try:
        subprocess.Popen(
            [bin_path, "server"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError as exc:
        raise HerdrLayoutError(f"could not start herdr server: {exc}") from exc

    for _ in range(40):
        time.sleep(0.25)
        proc = subprocess.run(
            [bin_path, "status"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        text = (proc.stdout or "") + "\n" + (proc.stderr or "")
        if "status: running" in text or "compatible: yes" in text:
            return
    raise HerdrLayoutError(
        "Herdr server did not become ready. Start Herdr manually (`herdr`), then retry."
    )


def tab_labels_from_team(team: dict[str, Any]) -> list[str]:
    """Labels for tabs: enabled persona tabs from team.yaml, plus services if missing."""
    labels: list[str] = []
    for tab in (team.get("layout") or {}).get("tabs") or []:
        tid = str(tab.get("id") or tab.get("label") or "").strip()
        if tid and tid not in labels:
            labels.append(tid)
    # US-04 standard set includes services even when no persona prompt ships.
    if "services" not in labels:
        labels.append("services")
    if not labels:
        labels = ["ops", "infra", "dev", "design", "qa", "services"]
    return labels


def setup_herdr_layout(
    *,
    project_name: str,
    project_cwd: Path,
    team: dict[str, Any],
    focus: bool = True,
) -> dict[str, Any]:
    """Create workspace + tabs. Returns layout metadata for team.yaml / next steps."""
    ensure_herdr_server()
    cwd = str(project_cwd.resolve())
    labels = tab_labels_from_team(team)

    create_args = ["workspace", "create", "--cwd", cwd, "--label", project_name]
    create_args.append("--focus" if focus else "--no-focus")
    created = _run_json(create_args)
    result = created.get("result") or {}
    workspace = result.get("workspace") or {}
    first_tab = result.get("tab") or {}
    root_pane = result.get("root_pane") or {}

    workspace_id = workspace.get("workspace_id")
    if not workspace_id:
        raise HerdrLayoutError("workspace create response missing workspace_id")

    first_tab_id = first_tab.get("tab_id")
    first_pane_id = root_pane.get("pane_id")

    tab_records: list[dict[str, str]] = []

    # Rename the default first tab to the first desired label.
    first_label = labels[0]
    if first_tab_id:
        _run_json(["tab", "rename", first_tab_id, first_label])
        tab_records.append(
            {
                "label": first_label,
                "tab_id": first_tab_id,
                "pane_id": first_pane_id or "",
            }
        )

    for label in labels[1:]:
        tab_created = _run_json(
            [
                "tab",
                "create",
                "--workspace",
                workspace_id,
                "--cwd",
                cwd,
                "--label",
                label,
                "--no-focus",
            ]
        )
        tres = tab_created.get("result") or {}
        tab = tres.get("tab") or {}
        pane = tres.get("root_pane") or {}
        tab_records.append(
            {
                "label": label,
                "tab_id": tab.get("tab_id") or "",
                "pane_id": pane.get("pane_id") or "",
            }
        )

    if focus:
        _run_json(["workspace", "focus", workspace_id])
        # Focus first (ops) tab when present.
        if tab_records and tab_records[0].get("tab_id"):
            try:
                _run_json(["tab", "focus", tab_records[0]["tab_id"]])
            except HerdrLayoutError:
                pass

    return {
        "workspace_id": workspace_id,
        "workspace_label": project_name,
        "cwd": cwd,
        "tabs": tab_records,
    }


def merge_herdr_into_team(team: dict[str, Any], layout: dict[str, Any]) -> dict[str, Any]:
    team = dict(team)
    team["herdr"] = {
        "workspace_id": layout["workspace_id"],
        "workspace_label": layout["workspace_label"],
        "tabs": layout["tabs"],
    }
    return team
