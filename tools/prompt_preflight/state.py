"""Best-effort JSON state: model cooldown, once-a-day notice, seen sessions, block overrides.

Every read and write is guarded. A broken state file must never break the hook.
"""
import hashlib
import json
import os
import tempfile
import time
from typing import Callable

MAX_SESSIONS = 50
MAX_BLOCKS = 20


def _digest(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8", "replace")).hexdigest()


class State:
    def __init__(self, path: str, clock: Callable[[], float] = time.time) -> None:
        self._path = path
        self._clock = clock
        self._data = self._load()

    def _load(self) -> dict:
        try:
            with open(self._path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, ValueError):
            return {}
        return data if isinstance(data, dict) else {}

    def _save(self) -> bool:
        """Write the state; False when it could not be saved."""
        try:
            directory = os.path.dirname(self._path) or "."
            fd, tmp = tempfile.mkstemp(dir=directory, prefix=".state-")
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(self._data, handle)
            os.replace(tmp, self._path)
        except OSError:
            return False
        return True

    def in_cooldown(self) -> bool:
        until = self._data.get("cooldown_until", 0)
        return isinstance(until, (int, float)) and self._clock() < until

    def start_cooldown(self, seconds: float) -> None:
        self._data["cooldown_until"] = self._clock() + seconds
        self._save()

    def notice_due(self, kind: str, every_s: float = 86400) -> bool:
        """True at most once per `every_s` for `kind`; records the time when it returns True."""
        notices = self._data.get("notices", {})
        if not isinstance(notices, dict):
            notices = {}
        self._data["notices"] = notices
        last = notices.get(kind)
        now = self._clock()
        if isinstance(last, (int, float)) and now - last < every_s:
            return False
        notices[kind] = now
        self._save()
        return True

    def register_session(self, session_id: str) -> bool:
        """True only the first time this session id is seen. An empty id is never 'first'."""
        if not session_id:
            return False
        seen = self._data.get("sessions", [])
        if not isinstance(seen, list):
            seen = []
        if session_id in seen:
            return False
        seen.append(session_id)
        self._data["sessions"] = seen[-MAX_SESSIONS:]
        self._save()
        return True

    def remember_block(self, prompt: str) -> bool:
        """Record a block so the identical prompt can pass once. False if it could not be saved."""
        blocks = self._data.get("blocks", {})
        if not isinstance(blocks, dict):
            blocks = {}
        blocks[_digest(prompt)] = self._clock()
        blocks = {k: v for k, v in blocks.items() if isinstance(v, (int, float))}
        newest = sorted(blocks.items(), key=lambda item: item[1])[-MAX_BLOCKS:]
        self._data["blocks"] = dict(newest)
        return self._save()

    def consume_override(self, prompt: str, window_s: float) -> bool:
        """True if this exact prompt was blocked within `window_s`. Consumes the record."""
        blocks = self._data.get("blocks", {})
        if not isinstance(blocks, dict):
            return False
        stamp = blocks.get(_digest(prompt))
        if not isinstance(stamp, (int, float)) or self._clock() - stamp > window_s:
            return False
        del blocks[_digest(prompt)]
        self._save()
        return True
