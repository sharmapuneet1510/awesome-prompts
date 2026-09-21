"""Safe, idempotent edits of a Claude Code settings file for the Prompt Preflight hook.

The pure functions work on a settings dict. The file helpers add the guards: refuse a file
that is not a JSON object, back it up before writing, and write atomically.
"""
import copy
import datetime
import difflib
import json
import os
import re
import shutil
import tempfile
from typing import Any, Dict, List, Optional

EVENT = "UserPromptSubmit"
MARKER = "prompt-preflight/hook.py"

Settings = Dict[str, Any]


class SettingsError(Exception):
    """The settings file cannot be edited safely."""


_MARKER = re.compile(r"(?:^|[/\s\"'])" + re.escape(MARKER))


def _ours(handler: Any) -> bool:
    """True for Preflight's own entry. The marker must begin a path component, so a user's
    `.../my-prompt-preflight/hook.py` is not mistaken for it."""
    return isinstance(handler, dict) and _MARKER.search(str(handler.get("command", "")).replace("\\", "/")) is not None


def _strip(groups: List[Any]) -> List[Any]:
    """Remove Preflight's handler from every matcher group; drop groups that only held it."""
    kept: List[Any] = []
    for group in groups:
        handlers = group.get("hooks") if isinstance(group, dict) else None
        if not isinstance(handlers, list):
            kept.append(group)
            continue
        remaining = [handler for handler in handlers if not _ours(handler)]
        if remaining or len(remaining) == len(handlers):
            kept.append(dict(group, hooks=remaining))
    return kept


def _groups(settings: Settings) -> List[Any]:
    hooks = settings.get("hooks", {})
    if not isinstance(hooks, dict):
        raise SettingsError('"hooks" is not an object')
    groups = hooks.get(EVENT, [])
    if not isinstance(groups, list):
        raise SettingsError('"hooks.%s" is not a list' % EVENT)
    return groups


def has_hook(settings: Settings) -> bool:
    return any(
        _ours(handler)
        for group in _groups(settings)
        if isinstance(group, dict) and isinstance(group.get("hooks"), list)
        for handler in group["hooks"]
    )


def add_hook(settings: Settings, command: str, timeout: int = 5) -> Settings:
    """Return a copy of `settings` with exactly one Preflight handler (any older one is replaced)."""
    groups = _strip(copy.deepcopy(_groups(settings)))
    groups.append({"hooks": [{"type": "command", "command": command, "timeout": timeout}]})
    result = copy.deepcopy(settings)
    result.setdefault("hooks", {})[EVENT] = groups
    return result


def remove_hook(settings: Settings) -> Settings:
    """Return a copy of `settings` without Preflight handler, tidying any container it empties."""
    groups = _strip(copy.deepcopy(_groups(settings)))
    result = copy.deepcopy(settings)
    if groups:
        result["hooks"][EVENT] = groups
    else:
        result.get("hooks", {}).pop(EVENT, None)
    if "hooks" in result and not result["hooks"]:
        del result["hooks"]
    return result


def read_settings(path: str) -> Settings:
    """Load `path`. A missing file is an empty settings object; anything unreadable is an error."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except ValueError as exc:
        raise SettingsError("%s is not valid JSON (%s); refusing to touch it" % (path, exc)) from exc
    except OSError as exc:
        raise SettingsError("cannot read %s: %s" % (path, exc)) from exc
    if not isinstance(data, dict):
        raise SettingsError("%s does not contain a JSON object; refusing to touch it" % path)
    return data


def _backup_path(path: str) -> str:
    stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    candidate, count = "%s.bak-%s" % (path, stamp), 0
    while os.path.exists(candidate):  # two writes in one second must not overwrite the first backup
        count += 1
        candidate = "%s.bak-%s-%d" % (path, stamp, count)
    return candidate


def write_settings(path: str, settings: Settings, backup: bool = True) -> Optional[str]:
    """Write atomically. Returns the backup path when an existing file was backed up.

    A symlinked settings file (dotfile setups) is written through, not replaced by a regular file, and the
    file keeps its permissions. Backups never overwrite each other.
    """
    path = os.path.realpath(path)
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)
    backup_path = None
    if backup and os.path.exists(path):
        backup_path = _backup_path(path)
        shutil.copy2(path, backup_path)
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".settings-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(settings, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        if os.path.exists(path):
            shutil.copymode(path, tmp)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return backup_path


def diff_text(before: Settings, after: Settings, name: str = "settings") -> str:
    """A unified diff of the two settings objects, for --dry-run and the confirmation step."""
    old = json.dumps(before, indent=2).splitlines()
    new = json.dumps(after, indent=2).splitlines()
    return "\n".join(difflib.unified_diff(old, new, "%s (before)" % name, "%s (after)" % name, lineterm=""))
