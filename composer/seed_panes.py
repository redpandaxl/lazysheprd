"""US-05 — start agents in layout panes and inject role prompts."""

from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any

from .herdr_layout import HerdrLayoutError, herdr_bin


class SeedError(Exception):
    """Raised when overall seeding cannot run (missing layout, etc.)."""


def _run(
    args: list[str],
    *,
    timeout: float = 120,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
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
    if check and proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "no output").strip()
        raise HerdrLayoutError(
            f"herdr {' '.join(args)} failed (exit {proc.returncode}): {err}"
        )
    return proc


def _run_json(args: list[str], *, timeout: float = 120) -> dict[str, Any]:
    proc = _run(args, timeout=timeout, check=True)
    out = (proc.stdout or "").strip()
    if not out:
        raise HerdrLayoutError(f"herdr {' '.join(args)} returned empty stdout")
    try:
        return json.loads(out)
    except json.JSONDecodeError as exc:
        raise HerdrLayoutError(
            f"herdr {' '.join(args)} did not return JSON: {out[:200]}"
        ) from exc


def agent_instance_name(project_name: str, persona_id: str) -> str:
    """Unique Herdr agent name: [a-z][a-z0-9_-]{0,31}, scoped per project.

    Avoids collisions with live agents named ops/dev in other workspaces.
    """
    slug = re.sub(r"[^a-z0-9_-]+", "-", project_name.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    if not slug:
        slug = "proj"
    if not slug[0].isalpha():
        slug = "p" + slug
    # Leave room for "-{persona_id}"
    pid = re.sub(r"[^a-z0-9_-]+", "-", persona_id.lower()).strip("-") or "agent"
    max_slug = max(1, 31 - len(pid) - 1)
    slug = slug[:max_slug].rstrip("-") or "p"
    name = f"{slug}-{pid}"
    return name[:32]


def _tab_index(layout: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Map tab label -> {tab_id, pane_id}."""
    out: dict[str, dict[str, str]] = {}
    for tab in layout.get("tabs") or []:
        label = str(tab.get("label") or "").strip()
        if not label:
            continue
        out[label] = {
            "tab_id": str(tab.get("tab_id") or ""),
            "pane_id": str(tab.get("pane_id") or ""),
        }
    return out


def build_seed_prompt(
    *,
    project_cwd: Path,
    persona: dict[str, Any],
    agent_name: str | None = None,
) -> str:
    """Combine role identity + prompt file + boot into one first message.

    Leads with an unmistakable role block so coding agents (Claude/Grok/etc.)
    lock identity immediately — a bare paste of agents/*.md is easy to miss
    as a normal chat turn after CLI startup.
    """
    title = str(persona.get("title") or persona.get("id") or "Agent")
    role = str(persona.get("role") or persona.get("id") or title)
    tab = str(persona.get("tab") or role)
    aname = agent_name or str(persona.get("id") or "agent")

    # Explicit identity first (most important for models that treat this as a user turn)
    identity = (
        f"# ROLE ASSIGNMENT — READ FIRST\n\n"
        f"**You are: {title}** (role id: `{role}`)\n"
        f"**Herdr agent name:** `{aname}` (use this when others message you)\n"
        f"**Your tab:** `{tab}`\n"
        f"**Project directory:** `{project_cwd}`\n\n"
        f"You are **only** {title}. You are **not** Ops, Developers, Design, or QA "
        f"unless that is your title above.\n"
        f"Do not take on another role's duties.\n"
    )

    parts: list[str] = [identity]

    prompt_file = persona.get("prompt_file") or ""
    if prompt_file:
        path = project_cwd / prompt_file
        if path.is_file():
            body = path.read_text(encoding="utf-8").strip()
            if body:
                parts.append("# Role playbook\n\n" + body)
        else:
            parts.append(
                f"(Role prompt file missing at {prompt_file}; use boot instructions only.)"
            )

    boot = (persona.get("boot_prompt") or "").strip()
    if boot:
        parts.append("# Boot instructions\n\n" + boot)

    parts.append(
        "# Session rules\n\n"
        f"- Working directory: `{project_cwd}`\n"
        "- Multi-agent workspace on Herdr: coordinate with "
        "`herdr agent prompt <name> \"...\"` — never assume pane watching.\n"
        "- Read `protocols/herdr-messaging.md` and `protocols/coordination.md`.\n"
        f"- Confirm identity: reply with exactly "
        f"`READY: {title} ({aname})` then wait for Ops."
    )
    return "\n\n".join(parts)


def _start_args(agent_name: str, persona: dict[str, Any], pane_id: str) -> list[str]:
    kind = str(persona.get("agent_kind") or "grok")
    if kind == "other":
        raise HerdrLayoutError(
            f"persona {persona.get('id')}: agent_kind 'other' cannot be auto-started; "
            "set a real Herdr kind"
        )
    # Do not pass model/effort after -- : many CLIs treat unknown flags as errors
    # and leave the pane in a non-shell state (agent_pane_busy on retry).
    return [
        "agent",
        "start",
        agent_name,
        "--kind",
        kind,
        "--pane",
        pane_id,
        "--timeout",
        "90000",
    ]


def seed_panes(
    *,
    project_name: str,
    project_cwd: Path,
    team: dict[str, Any],
    layout: dict[str, Any],
    wait_ready: bool = False,
    prompt_timeout_ms: int = 15000,
) -> dict[str, Any]:
    """Start enabled personas in layout panes and inject role prompts.

    Returns a report dict with per-persona status. Does not raise on per-pane
    failures; raises SeedError only when layout is unusable.
    """
    if not layout or not layout.get("tabs"):
        raise SeedError("no Herdr layout metadata; create layout before seeding panes")

    by_label = _tab_index(layout)
    personas = [p for p in (team.get("personas") or []) if p.get("enabled")]
    if not personas:
        raise SeedError("no enabled personas to seed")

    results: list[dict[str, Any]] = []

    # Let newly created tab shells finish login/prompt.
    time.sleep(2.0)

    for persona in personas:
        pid = str(persona.get("id") or "")
        tab_key = str(persona.get("tab") or pid)
        title = str(persona.get("title") or pid)
        agent_name = agent_instance_name(project_name, pid)
        rec = by_label.get(tab_key) or by_label.get(pid)
        entry: dict[str, Any] = {
            "id": pid,
            "agent_name": agent_name,
            "title": title,
            "tab": tab_key,
            "kind": persona.get("agent_kind"),
            "status": "pending",
            "pane_id": None,
            "detail": "",
        }
        if not rec or not rec.get("pane_id"):
            entry["status"] = "skipped"
            entry["detail"] = f"no pane for tab {tab_key!r} (e.g. services-only)"
            results.append(entry)
            continue

        pane_id = rec["pane_id"]
        entry["pane_id"] = pane_id
        entry["tab_id"] = rec.get("tab_id")

        start_err: Exception | None = None
        for attempt in range(1, 6):
            try:
                _run_json(_start_args(agent_name, persona, pane_id), timeout=120)
                entry["status"] = "started"
                start_err = None
                break
            except (HerdrLayoutError, Exception) as exc:
                start_err = exc
                msg = str(exc)
                # New tabs sometimes need a moment before they are "available shells".
                if "agent_pane_busy" in msg or "not an available shell" in msg:
                    time.sleep(1.0 * attempt)
                    continue
                break
        if start_err is not None and entry["status"] != "started":
            entry["status"] = "failed"
            entry["detail"] = f"agent start: {start_err}"
            results.append(entry)
            time.sleep(0.5)
            continue

        # Let CLI finish splash/UI before identity prompt (esp. Claude Code).
        time.sleep(1.5)
        try:
            _run(
                ["agent", "wait", agent_name, "--until", "idle", "--timeout", "45000"],
                timeout=50,
                check=False,
            )
        except Exception:
            pass

        seed_text = build_seed_prompt(
            project_cwd=project_cwd,
            persona=persona,
            agent_name=agent_name,
        )
        try:
            # Always wait a bit so the model starts consuming the role block.
            wait_ms = max(prompt_timeout_ms, 45000) if wait_ready else 45000
            prompt_args = [
                "agent",
                "prompt",
                agent_name,
                seed_text,
                "--wait",
                "--timeout",
                str(wait_ms),
            ]
            _run(prompt_args, timeout=(wait_ms / 1000) + 30, check=True)
            entry["status"] = "seeded"
            entry["detail"] = (
                f"role prompt injected as {agent_name!r} "
                f"(identity: {title})"
            )
        except (HerdrLayoutError, Exception) as exc:
            try:
                _run(
                    ["agent", "prompt", agent_name, seed_text],
                    timeout=30,
                    check=True,
                )
                entry["status"] = "seeded"
                entry["detail"] = (
                    f"role prompt injected as {agent_name!r} (no wait); "
                    f"identity: {title}"
                )
            except (HerdrLayoutError, Exception) as exc2:
                entry["status"] = "started_not_seeded"
                entry["detail"] = (
                    f"agent {agent_name!r} running but prompt failed: {exc2} "
                    f"(first error: {exc})"
                )

        results.append(entry)
        time.sleep(0.4)

    seeded = sum(1 for r in results if r["status"] == "seeded")
    started = sum(1 for r in results if r["status"] in ("seeded", "started_not_seeded", "started"))
    failed = sum(1 for r in results if r["status"] == "failed")
    return {
        "seeded_count": seeded,
        "started_count": started,
        "failed_count": failed,
        "results": results,
    }


def merge_seed_into_team(team: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    team = dict(team)
    herdr = dict(team.get("herdr") or {})
    herdr["seed"] = {
        "seeded_count": report.get("seeded_count"),
        "failed_count": report.get("failed_count"),
        "panes": [
            {
                "id": r["id"],
                "agent_name": r.get("agent_name") or "",
                "status": r["status"],
                "pane_id": r.get("pane_id") or "",
                "detail": r.get("detail") or "",
            }
            for r in report.get("results") or []
        ],
    }
    team["herdr"] = herdr
    return team


def print_seed_report(report: dict[str, Any]) -> None:
    print(
        f"✅ Pane seed: {report.get('seeded_count', 0)} seeded, "
        f"{report.get('started_count', 0)} agents up, "
        f"{report.get('failed_count', 0)} failed"
    )
    for r in report.get("results") or []:
        pane = r.get("pane_id") or "-"
        aname = r.get("agent_name") or r.get("id")
        detail = r.get("detail") or ""
        extra = f" — {detail}" if detail else ""
        print(
            f"   [{r['status']}] {r['id']} as {aname} ({r.get('kind')}) "
            f"pane={pane}{extra}"
        )
