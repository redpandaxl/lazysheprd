"""Stdlib curses TUI for US-01 + US-02 + US-03.

Steps (with back): Project → Directory → Archetype → Roles → Models → Git → Confirm.
"""

from __future__ import annotations

import curses
from pathlib import Path
from typing import Any

from .archetypes import iter_archetypes, load_archetype, tasks_markdown_for
from .cli import run_plan
from .packs import apply_defaults, load_pack
from .paths import DEFAULT_PACK, EFFORTS, KNOWN_KINDS, OPS_ID
from .packs import validate_project_name


class WizardState:
    def __init__(self) -> None:
        self.name = ""
        self.target = ""
        self.pack_id = DEFAULT_PACK
        self.archetype_id = "greenfield-web"
        self.personas: list[dict[str, Any]] = []
        self.git_init = True
        self.git_commit = False
        self.herdr_layout = True  # US-04 default on
        self.role_index = 0
        self.kind_index = 0
        self.effort_index = 1


def _center(stdscr: curses.window, y: int, text: str) -> None:
    h, w = stdscr.getmaxyx()
    x = max(0, (w - len(text)) // 2)
    if 0 <= y < h:
        stdscr.addnstr(y, x, text, max(0, w - x - 1))


def _menu(
    stdscr: curses.window,
    title: str,
    subtitle: str,
    options: list[str],
    selected: int,
    footer: str = "↑/↓ move  Enter select  b back  q quit",
) -> None:
    stdscr.erase()
    h, w = stdscr.getmaxyx()
    stdscr.addnstr(0, 0, " herd-tui  ·  multi-agent project composer ", w - 1, curses.A_REVERSE)
    stdscr.addnstr(2, 2, title[: w - 4], w - 4, curses.A_BOLD)
    if subtitle:
        for i, line in enumerate(subtitle.split("\n")):
            stdscr.addnstr(3 + i, 2, line[: w - 4], w - 4)
    base = 5 if not subtitle else 5 + subtitle.count("\n")
    for i, opt in enumerate(options):
        attr = curses.A_REVERSE if i == selected else curses.A_NORMAL
        y = base + i
        if y < h - 2:
            prefix = "❯ " if i == selected else "  "
            stdscr.addnstr(y, 2, (prefix + opt)[: w - 4], w - 4, attr)
    stdscr.addnstr(h - 1, 0, footer[: w - 1], w - 1)
    stdscr.refresh()


def _input_line(
    stdscr: curses.window,
    prompt: str,
    initial: str = "",
    *,
    empty_means_default: bool = True,
    hint: str = "Enter accepts default  ·  type b then Enter to go back  ·  Esc abort",
) -> str | None:
    """Read a line. Blank Enter keeps `initial` when empty_means_default.

    Returns None if the user aborts (Esc). Returns the sentinel \"__back__\" if
    the user types only b / back (when empty_means_default is True).
    """
    curses.echo()
    curses.curs_set(1)
    h, w = stdscr.getmaxyx()
    stdscr.erase()
    stdscr.addnstr(0, 0, " herd-tui  ·  multi-agent project composer ", w - 1, curses.A_REVERSE)
    stdscr.addnstr(2, 2, prompt[: w - 4], w - 4, curses.A_BOLD)
    if initial:
        stdscr.addnstr(3, 2, f"default: {initial}"[: w - 4], w - 4)
    stdscr.addnstr(4, 2, "> ", w - 4)
    # Pre-fill buffer so Enter keeps the default without retyping.
    prefill = initial if empty_means_default else ""
    stdscr.addnstr(4, 4, prefill[: w - 6], w - 6)
    stdscr.move(4, 4 + len(prefill))
    if hint:
        stdscr.addnstr(h - 1, 0, hint[: w - 1], w - 1)
    stdscr.refresh()
    try:
        raw = stdscr.getstr(4, 4, max(8, w - 8))
    except KeyboardInterrupt:
        curses.noecho()
        curses.curs_set(0)
        return None
    curses.noecho()
    curses.curs_set(0)
    if raw is None:
        return None
    text = raw.decode("utf-8", errors="replace").strip()
    if text == "" and empty_means_default:
        return initial
    if empty_means_default and text.lower() in ("b", "back"):
        return "__back__"
    return text


def _run(stdscr: curses.window) -> dict[str, Any] | None:
    curses.curs_set(0)
    state = WizardState()
    pack = load_pack(state.pack_id)
    state.personas = apply_defaults(pack)
    archetypes = iter_archetypes()
    arch_ids = [a["id"] for a in archetypes] or ["blank"]
    if state.archetype_id not in arch_ids:
        state.archetype_id = arch_ids[0]

    # 0 name, 1 dir, 2 archetype, 3 roles, 4 models, 5 git, 6 herdr layout, 7 confirm
    step = 0
    arch_sel = arch_ids.index(state.archetype_id)
    git_sel = 0
    herdr_sel = 0

    while True:
        if step == 0:
            name = _input_line(
                stdscr,
                "Project name",
                state.name,
                empty_means_default=bool(state.name),
                hint="Type a name and Enter  ·  Esc abort",
            )
            if name is None:
                return None
            if name == "__back__":
                continue
            if not name:
                continue
            try:
                state.name = validate_project_name(name)
            except SystemExit as exc:
                _menu(stdscr, "Invalid name", str(exc), ["OK"], 0, "Enter to retry")
                stdscr.getch()
                continue
            # Always refresh default target from name when name changes
            state.target = str(Path.home() / state.name)
            step = 1
            continue

        if step == 1:
            path = _input_line(
                stdscr,
                "Target directory",
                state.target,
                empty_means_default=True,
            )
            if path is None:
                return None
            if path == "__back__":
                step = 0
                continue
            if not path:
                # Should not happen when empty_means_default keeps initial
                path = state.target
            state.target = str(Path(path).expanduser())
            step = 2
            continue

        if step == 2:
            opts = [
                f"{a['id']} — {a.get('title') or ''}: {a.get('description') or ''}"
                for a in archetypes
            ] or ["blank — Blank"]
            _menu(
                stdscr,
                "Choose project archetype (US-03)",
                "Seeds TASKS.md with a realistic first board. You can edit files after.",
                opts,
                arch_sel,
            )
            ch = stdscr.getch()
            if ch in (ord("q"), 27):
                return None
            if ch in (ord("b"), curses.KEY_BACKSPACE, 127):
                step = 1
                continue
            if ch in (curses.KEY_UP, ord("k")):
                arch_sel = (arch_sel - 1) % len(opts)
            elif ch in (curses.KEY_DOWN, ord("j")):
                arch_sel = (arch_sel + 1) % len(opts)
            elif ch in (curses.KEY_ENTER, 10, 13):
                state.archetype_id = arch_ids[arch_sel]
                step = 3
            continue

        if step == 3:
            opts = []
            for p in state.personas:
                flag = "ON " if p["enabled"] else "off"
                desc = p.get("description") or ""
                opts.append(f"[{flag}] {p['title']} ({p['id']}) — {desc}")
            opts.append("Next: configure models →")
            sel = min(state.role_index, len(opts) - 1)
            _menu(
                stdscr,
                "Roles to include (US-02)",
                "Space/Enter toggles role (ops always on). Select “Next” when ready.",
                opts,
                sel,
            )
            ch = stdscr.getch()
            if ch in (ord("q"), 27):
                return None
            if ch in (ord("b"),):
                step = 2
                continue
            if ch in (curses.KEY_UP, ord("k")):
                state.role_index = (sel - 1) % len(opts)
            elif ch in (curses.KEY_DOWN, ord("j")):
                state.role_index = (sel + 1) % len(opts)
            elif ch in (ord(" "), curses.KEY_ENTER, 10, 13):
                if sel == len(opts) - 1:
                    state.role_index = 0
                    step = 4
                else:
                    p = state.personas[sel]
                    if p["id"] == OPS_ID:
                        p["enabled"] = True
                    else:
                        p["enabled"] = not p["enabled"]
            continue

        if step == 4:
            enabled = [p for p in state.personas if p["enabled"]]
            if not enabled:
                step = 3
                continue
            idx = min(state.role_index, len(enabled) - 1)
            persona = enabled[idx]
            kinds = KNOWN_KINDS
            if persona["agent_kind"] in kinds:
                kind_i = kinds.index(persona["agent_kind"])
            else:
                kind_i = 0
            efforts = EFFORTS
            eff = persona.get("effort") or "medium"
            effort_i = efforts.index(eff) if eff in efforts else 1
            opts = [
                f"Role: {persona['title']} ({idx + 1}/{len(enabled)})",
                f"Kind/tool: {persona['agent_kind']}  (←/→ change)",
                f"Model: {persona['model'] or '(default/null)'}  (e edit)",
                f"Effort: {persona.get('effort') or 'medium'}  ([/] change)",
                "Next role →" if idx < len(enabled) - 1 else "Next: git options →",
            ]
            # selection among editable rows 1-4
            sel = min(state.kind_index, len(opts) - 1)
            _menu(
                stdscr,
                "Models & tools per role (US-02)",
                "←/→ kind  e model  [/] effort  Enter on last row to continue  b back",
                opts,
                sel,
            )
            ch = stdscr.getch()
            if ch in (ord("q"), 27):
                return None
            if ch in (ord("b"),):
                step = 3
                continue
            if ch in (curses.KEY_UP, ord("k")):
                state.kind_index = (sel - 1) % len(opts)
            elif ch in (curses.KEY_DOWN, ord("j")):
                state.kind_index = (sel + 1) % len(opts)
            elif ch in (curses.KEY_LEFT,):
                kind_i = (kind_i - 1) % len(kinds)
                persona["agent_kind"] = kinds[kind_i]
            elif ch in (curses.KEY_RIGHT,):
                kind_i = (kind_i + 1) % len(kinds)
                persona["agent_kind"] = kinds[kind_i]
            elif ch in (ord("["),):
                effort_i = (effort_i - 1) % len(efforts)
                persona["effort"] = efforts[effort_i]
            elif ch in (ord("]"),):
                effort_i = (effort_i + 1) % len(efforts)
                persona["effort"] = efforts[effort_i]
            elif ch in (ord("e"),):
                m = _input_line(
                    stdscr,
                    f"Model for {persona['id']} (empty = null)",
                    str(persona["model"] or ""),
                    empty_means_default=False,
                    hint="Enter empty for null model  ·  Esc cancel",
                )
                if m is not None and m != "__back__":
                    persona["model"] = m if m else None
            elif ch in (curses.KEY_ENTER, 10, 13):
                if sel == len(opts) - 1 or sel == 0:
                    if idx < len(enabled) - 1:
                        state.role_index = idx + 1
                        state.kind_index = 0
                    else:
                        state.role_index = 0
                        step = 5
            continue

        if step == 5:
            opts = [
                f"git init: {'yes' if state.git_init else 'no'}",
                f"initial commit: {'yes' if state.git_commit else 'no'} (only if git init)",
                "Next: Herdr layout →",
            ]
            _menu(stdscr, "Git options (US-01)", "Space toggles  Enter on Next", opts, git_sel)
            ch = stdscr.getch()
            if ch in (ord("q"), 27):
                return None
            if ch in (ord("b"),):
                step = 4
                continue
            if ch in (curses.KEY_UP, ord("k")):
                git_sel = (git_sel - 1) % len(opts)
            elif ch in (curses.KEY_DOWN, ord("j")):
                git_sel = (git_sel + 1) % len(opts)
            elif ch in (ord(" "),):
                if git_sel == 0:
                    state.git_init = not state.git_init
                    if not state.git_init:
                        state.git_commit = False
                elif git_sel == 1 and state.git_init:
                    state.git_commit = not state.git_commit
            elif ch in (curses.KEY_ENTER, 10, 13):
                if git_sel == 2:
                    step = 6
                elif git_sel == 0:
                    state.git_init = not state.git_init
                elif git_sel == 1 and state.git_init:
                    state.git_commit = not state.git_commit
            continue

        if step == 6:
            opts = [
                f"Also set up Herdr layout: {'yes' if state.herdr_layout else 'no'}",
                "Next: confirm →",
            ]
            _menu(
                stdscr,
                "Herdr layout (US-04)",
                "Creates a workspace named after the project + tabs (ops/infra/dev/…/services).\n"
                "Works if Herdr is already running; starts the server if needed.",
                opts,
                herdr_sel,
            )
            ch = stdscr.getch()
            if ch in (ord("q"), 27):
                return None
            if ch in (ord("b"),):
                step = 5
                continue
            if ch in (curses.KEY_UP, ord("k")):
                herdr_sel = (herdr_sel - 1) % len(opts)
            elif ch in (curses.KEY_DOWN, ord("j")):
                herdr_sel = (herdr_sel + 1) % len(opts)
            elif ch in (ord(" "),):
                if herdr_sel == 0:
                    state.herdr_layout = not state.herdr_layout
            elif ch in (curses.KEY_ENTER, 10, 13):
                if herdr_sel == 1:
                    step = 7
                else:
                    state.herdr_layout = not state.herdr_layout
            continue

        if step == 7:
            lines = [
                f"name: {state.name}",
                f"dir:  {state.target}",
                f"archetype: {state.archetype_id}",
                f"git: init={state.git_init} commit={state.git_commit}",
                f"herdr_layout: {state.herdr_layout}",
                "roles:",
            ]
            for p in state.personas:
                if not p["enabled"]:
                    continue
                lines.append(
                    f"  - {p['id']}: {p['agent_kind']} / {p['model'] or '-'} / {p['effort'] or '-'}"
                )
            opts = ["Create project", "Back", "Quit"]
            sel = 0
            while True:
                _menu(stdscr, "Confirm (US-01)", "\n".join(lines), opts, sel)
                ch = stdscr.getch()
                if ch in (ord("q"), 27):
                    return None
                if ch in (curses.KEY_UP, ord("k")):
                    sel = (sel - 1) % len(opts)
                elif ch in (curses.KEY_DOWN, ord("j")):
                    sel = (sel + 1) % len(opts)
                elif ch in (ord("b"),):
                    step = 6
                    break
                elif ch in (curses.KEY_ENTER, 10, 13):
                    if sel == 0:
                        archetype = load_archetype(state.archetype_id)
                        return {
                            "name": state.name,
                            "target": Path(state.target).expanduser().resolve(),
                            "pack": pack,
                            "personas": state.personas,
                            "archetype_id": state.archetype_id,
                            "tasks_markdown": tasks_markdown_for(archetype, state.name),
                            "git_init": state.git_init,
                            "git_commit": state.git_commit,
                            "herdr_layout": state.herdr_layout,
                        }
                    if sel == 1:
                        step = 6
                        break
                    return None


def main(argv: list[str] | None = None) -> int:
    del argv  # reserved
    try:
        plan = curses.wrapper(_run)
    except curses.error as exc:
        raise SystemExit(
            f"TUI failed ({exc}). Use ./bin/herd-init for the CLI rail instead."
        ) from exc
    if plan is None:
        print("aborted")
        return 1
    # leave curses before printing
    return run_plan(plan)
