"""Unified CLI: init | status | update | template (US-01…US-08)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from . import cli as init_cli
from .status_view import focus_target, print_status
from .update_project import apply_update, build_update_plan, print_update_report
from .user_templates import (
    delete_template,
    list_templates,
    load_template,
    plan_from_template,
    print_templates,
    save_template_from_plan,
    templates_dir,
)
from .paths import DEFAULT_PACK
from .packs import validate_project_name


def _cmd_init(argv: list[str]) -> int:
    return init_cli.main(argv)


def _cmd_status(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="lazysheprd status", description="US-07 agent status overview")
    p.add_argument("--workspace", "-w", help="Filter by workspace id or label substring")
    p.add_argument("--json", action="store_true", help="Machine-readable output")
    p.add_argument("--focus", metavar="TARGET", help="Focus workspace id or agent name/pane")
    args = p.parse_args(argv)
    if args.focus:
        return focus_target(args.focus)
    return print_status(workspace_filter=args.workspace, as_json=args.json)


def _cmd_update(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        prog="lazysheprd update",
        description="US-08 update existing project agent config without clobbering customs",
    )
    p.add_argument("project", type=Path, help="Path to existing project")
    p.add_argument("--pack", default=DEFAULT_PACK)
    p.add_argument("--persona", action="append", default=[], metavar="id:kind:model:effort")
    p.add_argument("--enable", action="append", default=[], help="Enable role id (repeatable)")
    p.add_argument("--disable", action="append", default=[], help="Disable role id (repeatable)")
    p.add_argument(
        "--force-prompts",
        action="store_true",
        help="Overwrite existing agents/*.md from template pack",
    )
    p.add_argument(
        "--force-protocols",
        action="store_true",
        help="Replace protocols/ from template (destructive)",
    )
    p.add_argument("--yes", action="store_true", help="Skip confirm")
    args = p.parse_args(argv)

    project = args.project.expanduser().resolve()
    plan = build_update_plan(
        project,
        pack_id=args.pack,
        persona_specs=args.persona,
        enable=args.enable,
        disable=args.disable,
    )
    print(f"Project: {project}")
    print("Planned personas:")
    for persona in plan["personas"]:
        flag = "on " if persona["enabled"] else "off"
        print(
            f"  [{flag}] {persona['id']}: {persona['agent_kind']} / "
            f"{persona.get('model') or '-'} / {persona.get('effort') or '-'}"
        )
    if not args.yes:
        try:
            ans = input("Apply update? [y/N]: ").strip().lower()
        except EOFError:
            ans = "n"
        if ans not in ("y", "yes"):
            print("aborted")
            return 1

    report = apply_update(
        plan,
        force_prompts=args.force_prompts,
        force_protocols=args.force_protocols,
    )
    print_update_report(report)
    return 0


def _cmd_template(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="lazysheprd template", description="US-06 user templates")
    sub = p.add_subparsers(dest="action", required=True)

    sub.add_parser("list", help="List saved templates")
    sub.add_parser("dir", help="Print templates directory")

    show_p = sub.add_parser("show", help="Show a template JSON path / summary")
    show_p.add_argument("name")

    del_p = sub.add_parser("delete", help="Delete a template")
    del_p.add_argument("name")

    save_p = sub.add_parser(
        "save",
        help="Save a template from flags (roles from pack + overrides)",
    )
    save_p.add_argument("name", help="Template id")
    save_p.add_argument("--title")
    save_p.add_argument("--pack", default=DEFAULT_PACK)
    save_p.add_argument("--archetype", default="greenfield-web")
    save_p.add_argument("--persona", action="append", default=[])
    save_p.add_argument("--git", action="store_true")
    save_p.add_argument("--herdr-layout", action="store_true")
    save_p.add_argument("--seed-panes", action="store_true")
    save_p.add_argument("--force", action="store_true")

    args = p.parse_args(argv)

    if args.action == "list":
        return print_templates()
    if args.action == "dir":
        print(templates_dir())
        return 0
    if args.action == "show":
        t = load_template(args.name)
        import json

        print(json.dumps({k: v for k, v in t.items() if not str(k).startswith("_")}, indent=2))
        return 0
    if args.action == "delete":
        delete_template(args.name)
        print(f"deleted template {args.name}")
        return 0
    if args.action == "save":
        from .archetypes import load_archetype, tasks_markdown_for
        from .packs import apply_defaults, apply_overrides, load_pack

        pack = load_pack(args.pack)
        personas = apply_defaults(pack)
        apply_overrides(personas, args.persona)
        arch = load_archetype(args.archetype)
        plan: dict[str, Any] = {
            "pack": pack,
            "personas": personas,
            "archetype_id": args.archetype,
            "tasks_markdown": tasks_markdown_for(arch, "template"),
            "git_init": args.git,
            "git_commit": False,
            "herdr_layout": args.herdr_layout,
            "seed_panes": args.seed_panes,
        }
        path = save_template_from_plan(
            plan, template_id=args.name, title=args.title, overwrite=args.force
        )
        print(f"saved template {args.name} → {path}")
        return 0
    return 1


def main(argv: list[str] | None = None) -> int:
    argv = list(argv if argv is not None else sys.argv[1:])

    # No subcommand → treat as init
    if not argv or argv[0].startswith("-"):
        return _cmd_init(argv)

    cmd = argv[0]
    rest = argv[1:]
    if cmd in ("init", "create"):
        return _cmd_init(rest)
    if cmd in ("status", "st"):
        return _cmd_status(rest)
    if cmd in ("update", "up"):
        return _cmd_update(rest)
    if cmd in ("template", "templates", "tpl"):
        return _cmd_template(rest)
    if cmd in ("-h", "--help", "help"):
        print(
            """lazysheprd — LazySheprd, team builder for Herdr

Shepherd a multi-agent team: scaffold, layout, seed, status, update.

Commands:
  lazysheprd init [flags]          Create a new project (default if no command)
  lazysheprd status [--workspace]  Agent overview across workspaces
  lazysheprd status --focus TARGET Jump to workspace or agent
  lazysheprd update PATH           Update existing project agent config
  lazysheprd template list|save|show|delete

Also:
  lazysheprd-tui     interactive curses wizard
  lazysheprd-init    same as lazysheprd init
  lazysheprd-status  same as lazysheprd status
  lazysheprd-update  same as lazysheprd update
"""
        )
        return 0

    print(f"unknown command {cmd!r}; try: lazysheprd help", file=sys.stderr)
    return 2
