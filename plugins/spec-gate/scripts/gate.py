#!/usr/bin/env python3
"""spec-gate: enforce the spec-driven gate with Claude Code hooks.

Reads one hook event as JSON on stdin (UserPromptSubmit or PreToolUse) and
prints a JSON decision on stdout. Standard library only.
Spec: https://github.com/sharmapuneet1510/awesome-prompts/blob/main/docs/superpowers/specs/2026-09-29-spec-gate-design.md
"""
from __future__ import annotations

import datetime
import fnmatch
import hashlib
import json
import os
import re
import shlex
import sys
from pathlib import Path, PurePosixPath

CONFIG = ".spec-gate.json"
STATE_DIR = ".spec-gate"
DEFAULT_EXEMPT = ["specs/**", "docs/**", "tests/**"]
CHAIN = ["requirements.md", "design.md", "tasks.md"]
ADR_DIR = "docs/adr"
# "Status: X", "**Status:** X", "**Status**: X", "- Status: X", "> Status: X", "| Status | X |"
_STATUS = r"[\s>|*-]*\**Status\**\s*:?\s*\**\s*\|?\s*"
MARKER = re.compile(r"^" + _STATUS + r"(Approved|Accepted)\b", re.M | re.I)
MARKER_TEXT = re.compile(r"Status\**\s*:?\s*\**\s*\|?\s*(Approved|Accepted)\b", re.I)
DRAFT_LINE = re.compile(r"^(" + _STATUS + r")(Draft|Proposed)\b", re.M | re.I)
SHELL_WRAPPERS = {"env", "command", "sudo", "xargs", "nohup", "time", "exec", "builtin"}
FILE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}


class ConfigError(Exception):
    """.spec-gate.json exists but cannot be used."""


# ── config and state ──────────────────────────────────────────────────────────

def load_config(root: Path) -> dict | None:
    """None when the project has not opted in; ConfigError when the file is unusable."""
    path = root / CONFIG
    if not path.exists():
        return None
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise ConfigError(f"{CONFIG} does not parse: {err}") from err
    def globs(key: str) -> bool:
        value = cfg.get(key)
        return isinstance(value, list) and all(isinstance(g, str) and g for g in value)

    if not isinstance(cfg, dict) or not globs("source") or not cfg["source"]:
        raise ConfigError(f'{CONFIG} needs a non-empty "source" list of globs')
    if "exempt" in cfg and not globs("exempt"):
        raise ConfigError(f'{CONFIG}: "exempt" must be a list of globs')
    cfg.setdefault("exempt", DEFAULT_EXEMPT)
    spec_dir = cfg.get("spec_dir", "specs")
    folder = PurePosixPath(spec_dir) if isinstance(spec_dir, str) else None
    if folder is None or folder.is_absolute() or ".." in folder.parts or folder.as_posix() in ("", "."):
        raise ConfigError(f'{CONFIG}: "spec_dir" must be a folder inside the project')
    cfg["spec_dir"] = folder.as_posix()
    return cfg


def load_state(root: Path) -> dict:
    path = root / STATE_DIR / "approvals.json"
    state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    state.setdefault("active_feature", None)
    state.setdefault("approvals", {})
    state.setdefault("bypass", None)
    return state


def save_state(root: Path, state: dict) -> None:
    (root / STATE_DIR).mkdir(exist_ok=True)
    (root / STATE_DIR / "approvals.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def log(root: Path, entry: dict) -> None:
    (root / STATE_DIR).mkdir(exist_ok=True)
    with open(root / STATE_DIR / "log.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ── paths ─────────────────────────────────────────────────────────────────────

def rel(root: Path, path: str, base: Path | None = None) -> str | None:
    """Project-relative POSIX path, or None when it lies outside the project.

    Relative paths resolve against `base` (a shell's working directory), else the project root.
    """
    p = Path(path)
    p = (p if p.is_absolute() else (base or root) / p).resolve()
    try:
        return p.relative_to(root.resolve()).as_posix()
    except ValueError:
        return None


# Comparisons ignore case: on case-insensitive filesystems (macOS, Windows) SRC/ is src/.
def matches(path: str, globs: list[str]) -> bool:
    p = path.casefold()
    return any(fnmatch.fnmatchcase(p, g.casefold()) or fnmatch.fnmatchcase(p, g.casefold().rstrip("/*")) for g in globs)


def under(path: str, folder: str) -> bool:
    return path.casefold().startswith(folder.casefold().rstrip("/") + "/")


def is_state_path(path: str) -> bool:
    p = path.casefold()
    return p == CONFIG or p == STATE_DIR or under(p, STATE_DIR)


def is_marked_path(path: str, cfg: dict) -> bool:
    """Spec files and ADRs: the files whose approval markers only the hook may write."""
    return under(path, cfg["spec_dir"]) or under(path, ADR_DIR)


# ── the gate ──────────────────────────────────────────────────────────────────

def approved(root: Path, state: dict, path: str) -> bool:
    entry = state["approvals"].get(path)
    file = root / path
    return bool(entry) and file.exists() and sha256(file) == entry["sha256"]


def missing_approvals(root: Path, cfg: dict, state: dict) -> list[str]:
    feature = state["active_feature"]
    if not feature:
        return [f"{cfg['spec_dir']}/<feature>/tasks.md"]
    chain = [f"{cfg['spec_dir']}/{feature}/{name}" for name in CHAIN]
    return [p for p in chain if not approved(root, state, p)]


def bypass_open(state: dict, session_id: str) -> bool:
    return bool(state["bypass"]) and state["bypass"].get("session_id") == session_id


def closed_reason(root: Path, cfg: dict, state: dict, session_id: str) -> str | None:
    """Why a gated edit is refused now, or None when the gate is open."""
    if bypass_open(state, session_id):
        return None
    missing = missing_approvals(root, cfg, state)
    if not missing:
        return None
    first = missing[0]
    how = (f"type: /spec-gate:approve {first}" if "<feature>" not in first
           else "approve the feature's requirements.md, design.md and tasks.md with /spec-gate:approve <file>")
    return (f"Blocked by spec-gate: {first} is not approved. When you have reviewed it, {how}. "
            f"For a trivial change, type: /spec-gate:trivial <reason>.")


# ── UserPromptSubmit ──────────────────────────────────────────────────────────

def approve(root: Path, cfg: dict, state: dict, arg: str, prompt: str) -> str:
    path = rel(root, arg.strip())
    if not path or not (root / path).is_file():
        return f"spec-gate: not approved — {arg.strip() or '(no file given)'} is not a file in this project."
    spec_prefix = cfg["spec_dir"].rstrip("/") + "/"
    parts = path[len(spec_prefix):].split("/") if under(path, cfg["spec_dir"]) else []
    if len(parts) == 2 and parts[1].casefold() in CHAIN:
        feature, name = parts[0], parts[1].casefold()
        earlier = [f"{spec_prefix}{feature}/{n}" for n in CHAIN[: CHAIN.index(name)]]
        waiting = [p for p in earlier if not approved(root, state, p)]
        if waiting:
            return f"spec-gate: not approved — approve {waiting[0]} first (the chain is requirements → design → tasks)."
        status = "Approved"
    elif under(path, ADR_DIR) and path.casefold().endswith(".md"):
        feature, name, status = None, None, "Accepted"
    else:
        return (f"spec-gate: not approved — {path} is neither a spec file "
                f"({spec_prefix}<feature>/requirements.md|design.md|tasks.md) nor an ADR ({ADR_DIR}/*.md).")
    file = root / path
    text = file.read_text(encoding="utf-8")
    if DRAFT_LINE.search(text):
        text = DRAFT_LINE.sub(lambda m: m.group(1) + status, text, count=1)
    elif not MARKER.search(text):
        text = text.rstrip("\n") + f"\n\nStatus: {status}\n"
    file.write_text(text, encoding="utf-8")
    state["approvals"][path] = {"sha256": sha256(file), "at": now(), "prompt": prompt, "status": status}
    if name == "tasks.md":
        state["active_feature"] = feature
    log(root, {"at": now(), "event": "approve", "path": path, "status": status})
    active = f" Active feature: {state['active_feature']}." if state["active_feature"] else ""
    return f"spec-gate: {path} is {status} (recorded by the hook, bound to its current content).{active}"


def status_report(root: Path, cfg: dict, state: dict, session_id: str) -> str:
    lines = [f"spec-gate status — active feature: {state['active_feature'] or 'none'}"]
    for path in sorted(state["approvals"]):
        mark = "current" if approved(root, state, path) else "VOID (file changed since approval)"
        lines.append(f"  {path}: {state['approvals'][path].get('status', 'Approved')}, {mark}")
    lines.append(f"  trivial bypass: {'open' if bypass_open(state, session_id) else 'closed'}")
    reason = closed_reason(root, cfg, state, session_id)
    lines.append("  gated edits: " + ("allowed" if reason is None else "blocked"))
    return "\n".join(lines)


def on_prompt(event: dict, root: Path) -> dict | None:
    try:
        cfg = load_config(root)
    except ConfigError as err:
        return _context(f"spec-gate: {err}. Gated edits are blocked until it is fixed.")
    if cfg is None:
        return None
    state = load_state(root)
    prompt = event.get("prompt", "").strip()
    session_id = event.get("session_id", "")
    command, _, arg = prompt.partition(" ")
    closed = bool(state["bypass"]) and command != "/spec-gate:trivial"
    if closed:                       # a bypass lasts until the user's next message, whatever it is
        state["bypass"] = None
    if command == "/spec-gate:approve":
        message = approve(root, cfg, state, arg, prompt)
    elif command == "/spec-gate:trivial":
        state["bypass"] = {"session_id": session_id, "reason": arg.strip(), "opened_at": now()}
        log(root, {"at": now(), "event": "trivial", "reason": arg.strip(), "session_id": session_id})
        message = ("spec-gate: trivial bypass open until your next message. "
                   f"Reason logged: {arg.strip() or '(none given)'}")
    elif command == "/spec-gate:status":
        message = status_report(root, cfg, state, session_id)
    else:
        if closed:
            save_state(root, state)
        return None
    save_state(root, state)
    return _context(message)


def _context(message: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": message}}


# ── PreToolUse ────────────────────────────────────────────────────────────────

def resulting_text(root: Path, path: str, tool: str, tool_input: dict) -> str:
    """The file as it would read after the tool call (NotebookEdit: the new cell source)."""
    existing = (root / path).read_text(encoding="utf-8") if (root / path).is_file() else ""
    if tool == "Write":
        return tool_input.get("content", "")
    if tool == "Edit":
        edits = [tool_input]
    elif tool == "MultiEdit":
        edits = tool_input.get("edits", [])
    else:
        return existing + "\n" + tool_input.get("new_source", "")
    text = existing
    for e in edits:
        old, new = e.get("old_string", ""), e.get("new_string", "")
        text = text.replace(old, new) if e.get("replace_all") else text.replace(old, new, 1)
    return text


def adds_marker(root: Path, path: str, after: str) -> bool:
    existing = (root / path).read_text(encoding="utf-8") if (root / path).is_file() else ""
    before = {m.group(0).strip() for m in MARKER.finditer(existing)}
    return any(m.group(0).strip() not in before for m in MARKER.finditer(after))


def bash_targets(command: str) -> list[str]:
    """Paths a shell command would write, for the common write forms (best effort)."""
    # >, >>, 1>, &>, >| — but not 2>&1
    targets = [m.group(1) for m in re.finditer(r"(?:[0-9]*|&)>{1,2}\|?\s*([^\s;&|<>()]+)", command)]
    for segment in re.split(r"[;&|\n]+", command):
        try:
            words = shlex.split(segment)
        except ValueError:
            words = segment.split()
        while words and (words[0].lstrip("({") in SHELL_WRAPPERS or re.match(r"^[A-Za-z_]\w*=", words[0])
                         or words[0].lstrip("({") == ""):
            words.pop(0)
        if not words:
            continue
        words[0] = words[0].lstrip("({")
        name = os.path.basename(words[0])
        flags = [w for w in words[1:] if w.startswith("-")]
        args = [w for w in words[1:] if not w.startswith("-")]
        if name == "tee" or name in ("rm", "truncate", "touch"):
            targets += args
        elif name == "sed" and any(f.startswith("-i") or f.startswith("--in-place") for f in flags):
            targets += args[1:]
        elif name == "perl" and any("i" in f[1:] for f in flags if not f.startswith("--")):
            targets += args
        elif name in ("ln", "mv") or (name == "cp" and any(f in ("-l", "--link") or (f.startswith("-") and not f.startswith("--") and "l" in f) for f in flags)):
            targets += args            # every operand: a link or a move changes the source too
        elif name in ("cp", "install") and args:
            targets.append(args[-1])
    return [t.strip("'\"(){}") for t in targets]


def on_tool(event: dict, root: Path) -> dict | None:
    tool = event.get("tool_name", "")
    tool_input = event.get("tool_input", {}) or {}
    session_id = event.get("session_id", "")
    try:
        cfg = load_config(root)
    except ConfigError as err:
        if tool in FILE_TOOLS or (tool == "Bash" and bash_targets(tool_input.get("command", ""))):
            return _deny(f"Blocked by spec-gate: {err}. Ask the user to fix {CONFIG}.")
        return None
    if cfg is None:
        return None
    state = load_state(root)

    if tool == "Bash":
        command = tool_input.get("command", "")
        if re.search(r"spec-gate", command, re.I):
            return _deny("Blocked by spec-gate: shell commands may not touch the approval record, its config, "
                         "or spec-gate commands; only the user types /spec-gate:approve.")
        base = Path(event.get("cwd") or root)
        targets = [p for p in (rel(root, t, base) for t in bash_targets(command)) if p]
        if MARKER_TEXT.search(command) and targets:
            return _deny("Blocked by spec-gate: only the user approves (type /spec-gate:approve <file>).")
        gated = [p for p in targets if matches(p, cfg["source"]) and not matches(p, cfg["exempt"])]
        reason = closed_reason(root, cfg, state, session_id) if gated else None
        return _deny(reason) if reason else None

    if tool not in FILE_TOOLS:
        return None
    path = rel(root, tool_input.get("file_path") or tool_input.get("notebook_path") or "")
    if path is None:
        return None
    if is_state_path(path):
        return _deny("Blocked by spec-gate: the approval record and its config are managed by the hook.")
    target = root / path
    linked = target.is_file() and target.stat().st_nlink > 1      # a hard link edits another path too
    if (is_marked_path(path, cfg) or linked) and adds_marker(root, path, resulting_text(root, path, tool, tool_input)):
        return _deny(f"Blocked by spec-gate: only the user approves. When they have reviewed {path}, "
                     f"they type: /spec-gate:approve {path}")
    if linked:
        reason = closed_reason(root, cfg, state, session_id)
        if reason:
            return _deny(f"{reason} ({path} is hard-linked to another file.)")
    if matches(path, cfg["exempt"]) or not matches(path, cfg["source"]):
        return None
    reason = closed_reason(root, cfg, state, session_id)
    return _deny(reason) if reason else None


def _deny(reason: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": reason}}


# ── entry point ───────────────────────────────────────────────────────────────

def project_root(event: dict) -> Path:
    """CLAUDE_PROJECT_DIR when Claude Code sets it; otherwise the nearest folder above cwd with a config."""
    if os.environ.get("CLAUDE_PROJECT_DIR"):
        return Path(os.environ["CLAUDE_PROJECT_DIR"])
    start = Path(event.get("cwd") or os.getcwd()).resolve()
    return next((d for d in [start, *start.parents] if (d / CONFIG).exists()), start)


def main() -> int:
    raw = sys.stdin.read()
    try:
        event = json.loads(raw)
    except ValueError:
        return 0
    root = project_root(event)
    name = event.get("hook_event_name")
    try:
        result = on_prompt(event, root) if name == "UserPromptSubmit" else on_tool(event, root)
    except Exception as err:  # a crash must not open the gate
        if name == "PreToolUse":
            result = _deny(f"Blocked by spec-gate: internal error ({type(err).__name__}: {err}).")
        else:
            result = _context(f"spec-gate: internal error ({type(err).__name__}: {err}).")
    if result:
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
