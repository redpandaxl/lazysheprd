"""CLI rail for herd-init (US-01/02/03 without full TUI chrome)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from .archetypes import iter_archetypes, load_archetype, tasks_markdown_for
from .herdr_layout import (
    HerdrLayoutError,
    merge_herdr_into_team,
    setup_herdr_layout,
)
from .materialize import materialize, print_next_steps
from .seed_panes import (
    SeedError,
    merge_seed_into_team,
    print_seed_report,
    seed_panes,
)
from .packs import (
    apply_defaults,
    apply_overrides,
    apply_persona_fields,
    iter_packs,
    load_pack,
    parse_persona_fields,
    validate_project_name,
)
from .paths import DEFAULT_PACK, OPS_ID
from .yamlutil import dump_yaml, load_yaml


def prompt_line(label: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default not in (None, "") else ""
    try:
        raw = input(f"{label}{suffix}: ").strip()
    except EOFError:
        raise SystemExit("error: EOF on prompt; use --non-interactive")
    if raw == "" and default is not None:
        return default
    return raw


def pick_from_list(label: str, items: list[tuple[str, str]], default_id: str) -> str:
    print(f"\n{label}")
    ids = []
    for i, (iid, desc) in enumerate(items, 1):
        mark = "*" if iid == default_id else " "
        print(f"  {i}. [{mark}] {iid} — {desc}")
        ids.append(iid)
    raw = prompt_line("Choice (number or id)", default_id)
    if raw.isdigit():
        idx = int(raw)
        if 1 <= idx <= len(ids):
            return ids[idx - 1]
        raise SystemExit(f"invalid choice {raw}")
    if raw not in ids:
        raise SystemExit(f"unknown id {raw!r}")
    return raw


def interactive_plan(
    *,
    name: str | None,
    target: Path | None,
    pack_id: str,
    archetype_id: str | None,
    persona_specs: list[str],
    git_init: bool | None,
    assume_yes: bool,
) -> dict[str, Any]:
    """Return a plan dict ready for materialize."""
    name = prompt_line("Project name", name) if not (name and assume_yes) else name
    if not name:
        name = prompt_line("Project name")
    name = validate_project_name(name)

    default_target = str(target) if target else str(Path.cwd() / name)
    target_s = prompt_line("Target directory", default_target)
    target_path = Path(target_s).expanduser().resolve()

    available = {p["id"]: p for p in iter_packs()}
    if not available:
        raise SystemExit("no packs found")
    pack_id = prompt_line("Pack", pack_id or DEFAULT_PACK)
    if pack_id not in available:
        raise SystemExit(f"unknown pack {pack_id!r}")
    pack = available[pack_id]

    arch_items = [(a["id"], a.get("description") or a.get("title") or "") for a in iter_archetypes()]
    if not arch_items:
        arch_items = [("blank", "Blank")]
    archetype_id = archetype_id or "greenfield-web"
    if archetype_id not in {a[0] for a in arch_items}:
        archetype_id = arch_items[0][0]
    archetype_id = pick_from_list("Archetype / starting phase", arch_items, archetype_id)
    archetype = load_archetype(archetype_id)

    personas = apply_defaults(pack)
    apply_overrides(personas, persona_specs)

    print("\nRoles (Enter=keep, kind:model:effort, n/off=disable, y/on=enable; ops always on)")
    for persona in personas:
        desc = persona.get("description") or ""
        model_s = persona["model"] if persona["model"] is not None else "-"
        effort_s = persona["effort"] if persona["effort"] is not None else "-"
        print(f"  {persona['id']} — {persona['title']}")
        if desc:
            print(f"      {desc}")
        print(f"      kind={persona['agent_kind']}  model={model_s}  effort={effort_s}")
        reply = prompt_line("      value", "")
        if reply == "":
            continue
        low = reply.lower()
        if low in ("n", "off", "disable", "disabled"):
            if persona["id"] == OPS_ID:
                print("      ops cannot be disabled; keeping enabled")
            else:
                persona["enabled"] = False
            continue
        if low in ("y", "on", "enable", "enabled"):
            persona["enabled"] = True
            continue
        kind, model_slot, effort_slot = parse_persona_fields(reply)
        apply_persona_fields(persona, kind, model_slot, effort_slot)

    if git_init is None:
        git_reply = prompt_line("Initialize git repo?", "y")
        git_init = git_reply.lower() in ("y", "yes")
    git_commit = False
    if git_init:
        gc = prompt_line("Create initial commit?", "n")
        git_commit = gc.lower() in ("y", "yes")

    if assume_yes:
        herdr_layout = True
    else:
        hl = prompt_line("Also set up Herdr layout (workspace + tabs)?", "y")
        herdr_layout = hl.lower() in ("y", "yes")

    seed_panes_flag = False
    if herdr_layout:
        if assume_yes:
            seed_panes_flag = True
        else:
            sp = prompt_line("Seed agent panes (start agents + inject role prompts)?", "y")
            seed_panes_flag = sp.lower() in ("y", "yes")

    print("\nPlan")
    print(f"  name:       {name}")
    print(f"  dir:        {target_path}")
    print(f"  pack:       {pack_id}")
    print(f"  archetype:  {archetype_id}")
    print(f"  git_init:   {git_init}  commit={git_commit}")
    print(f"  herdr_layout: {herdr_layout}")
    print(f"  seed_panes:   {seed_panes_flag}")
    for persona in personas:
        flag = "on " if persona["enabled"] else "off"
        print(
            f"  [{flag}] {persona['id']}: {persona['agent_kind']} / "
            f"{persona['model'] or '-'} / {persona['effort'] or '-'}"
        )
    if not assume_yes:
        confirm = prompt_line("Create project?", "y")
        if confirm.lower() not in ("y", "yes"):
            raise SystemExit("aborted")

    return {
        "name": name,
        "target": target_path,
        "pack": pack,
        "personas": personas,
        "archetype_id": archetype_id,
        "tasks_markdown": tasks_markdown_for(archetype, name),
        "git_init": git_init,
        "git_commit": git_commit,
        "herdr_layout": herdr_layout,
        "seed_panes": seed_panes_flag,
    }


def noninteractive_plan(
    *,
    name: str | None,
    target: Path | None,
    pack_id: str,
    archetype_id: str,
    persona_specs: list[str],
    git_init: bool,
    git_commit: bool,
    herdr_layout: bool = False,
    seed_panes_flag: bool = False,
) -> dict[str, Any]:
    if not name:
        raise SystemExit("--non-interactive requires --name")
    name = validate_project_name(name)
    pack = load_pack(pack_id)
    personas = apply_defaults(pack)
    apply_overrides(personas, persona_specs)
    dest = (target if target else Path.cwd() / name).expanduser().resolve()
    archetype = load_archetype(archetype_id)
    if seed_panes_flag and not herdr_layout:
        raise SystemExit("--seed-panes requires --herdr-layout")
    return {
        "name": name,
        "target": dest,
        "pack": pack,
        "personas": personas,
        "archetype_id": archetype_id,
        "tasks_markdown": tasks_markdown_for(archetype, name),
        "git_init": git_init,
        "git_commit": git_commit,
        "herdr_layout": herdr_layout,
        "seed_panes": seed_panes_flag,
    }


def list_packs() -> int:
    packs = iter_packs()
    if not packs:
        print("no packs")
        return 1
    width = max(len(p["id"]) for p in packs)
    for pack in packs:
        print(f"{pack['id']:<{width}}  {pack.get('title') or ''}  {pack.get('description') or ''}".rstrip())
    return 0


def list_archetypes() -> int:
    items = iter_archetypes()
    if not items:
        print("no archetypes")
        return 1
    width = max(len(a["id"]) for a in items)
    for a in items:
        print(f"{a['id']:<{width}}  {a.get('title') or ''}  {a.get('description') or ''}".rstrip())
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Initialize a Herdr multi-agent project (files + optional Herdr layout)."
    )
    p.add_argument("--name")
    p.add_argument("--dir", dest="dir")
    p.add_argument("--pack", default=DEFAULT_PACK)
    p.add_argument("--archetype", default="greenfield-web", help="Starting TASKS seed (default: greenfield-web)")
    p.add_argument("--yes", action="store_true")
    p.add_argument("--persona", action="append", default=[], metavar="id:kind:model:effort")
    p.add_argument("--non-interactive", action="store_true")
    p.add_argument("--git", dest="git", action="store_true", default=None, help="git init")
    p.add_argument("--no-git", dest="git", action="store_false", help="skip git init")
    p.add_argument("--git-commit", action="store_true", help="with --git, also initial commit")
    p.add_argument(
        "--herdr-layout",
        dest="herdr_layout",
        action="store_true",
        default=None,
        help="Create Herdr workspace + tabs (US-04)",
    )
    p.add_argument(
        "--no-herdr-layout",
        dest="herdr_layout",
        action="store_false",
        help="Skip Herdr layout",
    )
    p.add_argument(
        "--seed-panes",
        dest="seed_panes",
        action="store_true",
        default=None,
        help="Start agents and inject role prompts (requires layout; US-05)",
    )
    p.add_argument(
        "--no-seed-panes",
        dest="seed_panes",
        action="store_false",
        help="Skip seeding panes",
    )
    p.add_argument(
        "--template",
        help="US-06: start from a saved user template id",
    )
    p.add_argument(
        "--save-template",
        metavar="NAME",
        help="US-06: after plan is built, save it as a named template",
    )
    p.add_argument(
        "--force-template",
        action="store_true",
        help="Overwrite template when using --save-template",
    )
    p.add_argument("--list-packs", action="store_true")
    p.add_argument("--list-archetypes", action="store_true")
    p.add_argument("--list-templates", action="store_true", help="US-06 list user templates")
    return p.parse_args(argv)


def run_plan(plan: dict[str, Any]) -> int:
    if plan.get("save_template"):
        from .user_templates import save_template_from_plan

        path = save_template_from_plan(
            plan,
            template_id=str(plan["save_template"]),
            overwrite=bool(plan.get("force_template")),
        )
        print(f"✅ Saved template {plan['save_template']} → {path}")

    # Allow --save-template-only workflows (no project name materialize)
    if plan.get("save_template_only"):
        return 0

    materialize(
        name=plan["name"],
        target=plan["target"],
        pack=plan["pack"],
        personas=plan["personas"],
        tasks_markdown=plan.get("tasks_markdown"),
        git_init=bool(plan.get("git_init")),
        git_commit=bool(plan.get("git_commit")),
        archetype_id=plan.get("archetype_id"),
    )
    team = load_yaml((plan["target"] / "team.yaml").read_text(encoding="utf-8"))
    layout_meta = None
    layout_err = None
    seed_report = None
    seed_err = None
    if plan.get("herdr_layout"):
        try:
            layout_meta = setup_herdr_layout(
                project_name=plan["name"],
                project_cwd=plan["target"],
                team=team,
                focus=True,
            )
            team = merge_herdr_into_team(team, layout_meta)
            (plan["target"] / "team.yaml").write_text(dump_yaml(team), encoding="utf-8")
            print(
                f"✅ Herdr layout: workspace {layout_meta['workspace_id']} "
                f"({layout_meta['workspace_label']}) tabs="
                f"{[t['label'] for t in layout_meta['tabs']]}"
            )
        except HerdrLayoutError as exc:
            layout_err = str(exc)
            print(f"⚠️  Herdr layout failed (project files are fine): {exc}", file=sys.stderr)

    if plan.get("seed_panes"):
        if not layout_meta:
            seed_err = "seed panes skipped (Herdr layout missing or failed)"
            print(f"⚠️  {seed_err}", file=sys.stderr)
        else:
            try:
                print("⏳ Seeding agent panes (start + inject role prompts)...")
                seed_report = seed_panes(
                    project_name=plan["name"],
                    project_cwd=plan["target"],
                    team=team,
                    layout=layout_meta,
                    wait_ready=False,
                )
                team = merge_seed_into_team(team, seed_report)
                (plan["target"] / "team.yaml").write_text(dump_yaml(team), encoding="utf-8")
                print_seed_report(seed_report)
            except (SeedError, HerdrLayoutError) as exc:
                seed_err = str(exc)
                print(f"⚠️  Pane seed failed (layout/files kept): {exc}", file=sys.stderr)

    print_next_steps(
        plan["target"],
        team,
        herdr_layout=layout_meta,
        herdr_layout_error=layout_err,
        seed_report=seed_report,
        seed_error=seed_err,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if args.list_packs:
        return list_packs()
    if args.list_archetypes:
        return list_archetypes()
    if args.list_templates:
        from .user_templates import print_templates

        return print_templates()

    target = Path(args.dir).expanduser() if args.dir else None
    git_flag = args.git  # None / True / False
    herdr_flag = args.herdr_layout  # None / True / False
    seed_flag = args.seed_panes  # None / True / False

    if args.template:
        from .user_templates import load_template, plan_from_template

        if not args.name and not args.non_interactive:
            # interactive can still ask name
            pass
        if args.non_interactive and not args.name:
            raise SystemExit("--template with --non-interactive requires --name")
        name = args.name
        if not name:
            name = prompt_line("Project name")
        name = validate_project_name(name)
        dest = (target if target else Path.cwd() / name).expanduser().resolve()
        tpl = load_template(args.template)
        plan = plan_from_template(tpl, name=name, target=dest)
        # CLI flags override template defaults when explicitly set
        if git_flag is not None:
            plan["git_init"] = bool(git_flag)
        if herdr_flag is not None:
            plan["herdr_layout"] = bool(herdr_flag)
        if seed_flag is not None:
            plan["seed_panes"] = bool(seed_flag)
        if args.persona:
            apply_overrides(plan["personas"], args.persona)
        if args.save_template:
            plan["save_template"] = args.save_template
            plan["force_template"] = args.force_template
        if not args.yes and not args.non_interactive:
            print("\nPlan from template", args.template)
            print(f"  name: {plan['name']}")
            print(f"  dir:  {plan['target']}")
            print(f"  archetype: {plan['archetype_id']}")
            confirm = prompt_line("Create project?", "y")
            if confirm.lower() not in ("y", "yes"):
                raise SystemExit("aborted")
        return run_plan(plan)

    if args.non_interactive:
        git_init = True if git_flag is True else False if git_flag is False else False
        herdr_layout = True if herdr_flag is True else False
        seed_panes_flag = True if seed_flag is True else False
        plan = noninteractive_plan(
            name=args.name,
            target=target,
            pack_id=args.pack,
            archetype_id=args.archetype,
            persona_specs=args.persona,
            git_init=git_init,
            git_commit=bool(args.git_commit and git_init),
            herdr_layout=herdr_layout,
            seed_panes_flag=seed_panes_flag,
        )
    else:
        if not sys.stdin.isatty() and not args.yes:
            raise SystemExit("error: not a tty; use --non-interactive")
        plan = interactive_plan(
            name=args.name,
            target=target,
            pack_id=args.pack,
            archetype_id=args.archetype,
            persona_specs=args.persona,
            git_init=git_flag,
            assume_yes=args.yes,
        )
        # CLI flag overrides interactive default when explicitly set
        if herdr_flag is not None:
            plan["herdr_layout"] = herdr_flag
        if seed_flag is not None:
            plan["seed_panes"] = seed_flag
        if plan.get("seed_panes") and not plan.get("herdr_layout"):
            plan["seed_panes"] = False

    if args.save_template:
        plan["save_template"] = args.save_template
        plan["force_template"] = args.force_template
    return run_plan(plan)
