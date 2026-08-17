"""Minimal YAML subset load/dump (stdlib only)."""
from __future__ import annotations

from typing import Any

def _strip_inline_comment(line: str) -> str:
    in_single = False
    in_double = False
    escaped = False
    out: list[str] = []
    for ch in line:
        if escaped:
            out.append(ch)
            escaped = False
            continue
        if ch == "\\" and in_double:
            out.append(ch)
            escaped = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            break
        out.append(ch)
    return "".join(out).rstrip()


def _parse_scalar(raw: str) -> Any:
    if raw == "" or raw in ("null", "~"):
        return None
    if raw in ("true", "True", "yes"):
        return True
    if raw in ("false", "False", "no"):
        return False
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
        quote = raw[0]
        inner = raw[1:-1]
        if quote == '"':
            return (
                inner.replace("\\\"", '"')
                .replace("\\n", "\n")
                .replace("\\\\", "\\")
            )
        return inner.replace("''", "'")
    try:
        if raw.startswith(("+", "-")) or raw.isdigit():
            return int(raw, 10)
    except ValueError:
        pass
    return raw


def _needs_quotes(s: str) -> bool:
    if s == "" or s in ("true", "false", "null", "yes", "no", "~"):
        return True
    if s[0].isspace() or s[-1].isspace():
        return True
    special = set(":{}[]#&*!|>%@`,")
    return any(ch in special or ch in "\n\r\t" or ch == "'" or ch == '"' for ch in s)


def dump_yaml(data: Any) -> str:
    lines: list[str] = []

    def emit_scalar(value: Any) -> str:
        if value is None:
            return "null"
        if value is True:
            return "true"
        if value is False:
            return "false"
        if isinstance(value, int) and not isinstance(value, bool):
            return str(value)
        text = str(value)
        if not _needs_quotes(text):
            return text
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    def emit(value: Any, indent: int, prefix: str = "") -> None:
        pad = "  " * indent
        if isinstance(value, dict):
            if not value:
                lines.append(f"{pad}{prefix}{{}}")
                return
            first = True
            for key, item in value.items():
                head = f"{pad}{prefix}{key}:" if first else f"{pad}{key}:"
                first = False
                if isinstance(item, (dict, list)):
                    if not item:
                        empty = "{}" if isinstance(item, dict) else "[]"
                        lines.append(f"{head} {empty}")
                    else:
                        lines.append(head)
                        emit(item, indent + 1)
                else:
                    lines.append(f"{head} {emit_scalar(item)}")
            return
        if isinstance(value, list):
            if not value:
                lines.append(f"{pad}{prefix}[]")
                return
            for item in value:
                dash = f"{pad}- "
                if isinstance(item, dict):
                    if not item:
                        lines.append(f"{pad}- {{}}")
                        continue
                    keys = list(item.items())
                    first_k, first_v = keys[0]
                    if isinstance(first_v, (dict, list)):
                        lines.append(f"{dash}{first_k}:")
                        emit(first_v, indent + 2)
                    else:
                        lines.append(f"{dash}{first_k}: {emit_scalar(first_v)}")
                    for rest_k, rest_v in keys[1:]:
                        key_pad = "  " * (indent + 1)
                        if isinstance(rest_v, (dict, list)):
                            if not rest_v:
                                empty = "{}" if isinstance(rest_v, dict) else "[]"
                                lines.append(f"{key_pad}{rest_k}: {empty}")
                            else:
                                lines.append(f"{key_pad}{rest_k}:")
                                emit(rest_v, indent + 2)
                        else:
                            lines.append(f"{key_pad}{rest_k}: {emit_scalar(rest_v)}")
                elif isinstance(item, list):
                    lines.append(f"{pad}-")
                    emit(item, indent + 1)
                else:
                    lines.append(f"{dash}{emit_scalar(item)}")
            return
        lines.append(f"{pad}{prefix}{emit_scalar(value)}")

    emit(data, 0)
    return "\n".join(lines) + "\n"


def load_yaml(text: str) -> Any:
    entries: list[tuple[int, str]] = []
    for raw in text.splitlines():
        if not raw.strip():
            continue
        if raw.startswith("\t"):
            raise ValueError("YAML tabs are not supported")
        stripped = _strip_inline_comment(raw)
        if not stripped.strip():
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        entries.append((indent, stripped.strip()))

    def parse_from(idx: int, min_indent: int) -> tuple[Any, int]:
        if idx >= len(entries):
            return None, idx
        indent, content = entries[idx]
        if indent < min_indent:
            return None, idx
        if content.startswith("- ") or content == "-":
            return parse_list(idx, indent)
        return parse_map(idx, indent)

    def parse_map(idx: int, map_indent: int) -> tuple[dict[str, Any], int]:
        result: dict[str, Any] = {}
        while idx < len(entries):
            indent, content = entries[idx]
            if indent != map_indent or content.startswith("-"):
                break
            if ":" not in content:
                raise ValueError(f"expected key: value, got {content!r}")
            key, rest = content.split(":", 1)
            key = key.strip()
            rest = rest.strip()
            idx += 1
            if rest != "":
                result[key] = _parse_scalar(rest)
                continue
            if idx >= len(entries) or entries[idx][0] <= map_indent:
                result[key] = None
                continue
            child, idx = parse_from(idx, map_indent + 1)
            result[key] = child
        return result, idx

    def parse_list(idx: int, list_indent: int) -> tuple[list[Any], int]:
        result: list[Any] = []
        while idx < len(entries):
            indent, content = entries[idx]
            if indent != list_indent or not (content.startswith("- ") or content == "-"):
                break
            item_body = content[1:].strip()
            idx += 1
            if item_body == "":
                if idx < len(entries) and entries[idx][0] > list_indent:
                    child, idx = parse_from(idx, list_indent + 1)
                    result.append(child)
                else:
                    result.append(None)
                continue
            if ":" in item_body:
                key, rest = item_body.split(":", 1)
                mapping: dict[str, Any] = {key.strip(): _parse_scalar(rest.strip()) if rest.strip() != "" else None}
                if rest.strip() == "" and idx < len(entries) and entries[idx][0] > list_indent + 1:
                    child, idx = parse_from(idx, list_indent + 2)
                    mapping[key.strip()] = child
                key_indent = list_indent + 2
                while idx < len(entries):
                    nindent, ncontent = entries[idx]
                    if nindent != key_indent or ncontent.startswith("-"):
                        break
                    if ":" not in ncontent:
                        raise ValueError(f"expected key: value in list item, got {ncontent!r}")
                    nkey, nrest = ncontent.split(":", 1)
                    nkey, nrest = nkey.strip(), nrest.strip()
                    idx += 1
                    if nrest != "":
                        mapping[nkey] = _parse_scalar(nrest)
                    elif idx < len(entries) and entries[idx][0] > key_indent:
                        child, idx = parse_from(idx, key_indent + 1)
                        mapping[nkey] = child
                    else:
                        mapping[nkey] = None
                result.append(mapping)
            else:
                result.append(_parse_scalar(item_body))
        return result, idx

    if not entries:
        return None
    value, idx = parse_from(0, entries[0][0])
    if idx != len(entries):
        raise ValueError("failed to consume YAML document")
    return value


