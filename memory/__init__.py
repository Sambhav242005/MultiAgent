from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Mapping

DB = Path("memory/memory").with_suffix(".db")
_thread_local = threading.local()          # stores per-thread connection


def _ensure_schema() -> None:
    """Run exactly once at startup to create the table."""
    with sqlite3.connect(DB) as cx:
        cx.execute(
            """CREATE TABLE IF NOT EXISTS log(
                 id       INTEGER PRIMARY KEY,
                 thread_id TEXT,
                 source    TEXT,
                 fmt       TEXT,
                 intent    TEXT,
                 payload   JSON,
                 ts        DATETIME DEFAULT CURRENT_TIMESTAMP
             )"""
        )


class Memory:
    def __init__(self) -> None:
        _ensure_schema()

    # ───────────────── helpers ───────────────── #

    @staticmethod
    def _cx() -> sqlite3.Connection:
        """Return a per-thread connection (cached)."""
        cx = getattr(_thread_local, "cx", None)
        if cx is None:
            cx = sqlite3.connect(DB, detect_types=sqlite3.PARSE_DECLTYPES)
            _thread_local.cx = cx
        return cx

    # ───────────────── public API ─────────────── #

    def write(
        self,
        *,
        thread_id: str,
        source: str,
        fmt: str,
        intent: str,
        payload: Mapping[str, Any],
    ) -> None:
        cx = self._cx()
        cx.execute(
            "INSERT INTO log(thread_id, source, fmt, intent, payload)"
            " VALUES (?, ?, ?, ?, json(?))",
            (thread_id, source, fmt, intent, json.dumps(payload)),
        )
        cx.commit()

    def last(self, thread_id: str) -> tuple | None:
        cx = self._cx()
        cur = cx.execute(
            "SELECT * FROM log WHERE thread_id = ? ORDER BY ts DESC LIMIT 1",
            (thread_id,),
        )
        return cur.fetchone()
