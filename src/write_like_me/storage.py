from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .paths import database_path, ensure_private_dir


SCHEMA = """
CREATE TABLE IF NOT EXISTS samples (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  digest TEXT NOT NULL UNIQUE,
  text TEXT NOT NULL,
  source TEXT NOT NULL,
  channel TEXT NOT NULL,
  redactions TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS samples_created_at ON samples(created_at);
"""


class Store:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or database_path()

    def connect(self) -> sqlite3.Connection:
        ensure_private_dir()
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.executescript(SCHEMA)
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            pass
        return connection

    def add(self, text: str, source: str, channel: str, redactions: list[str], max_samples: int) -> bool:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        with self.connect() as db:
            cursor = db.execute(
                "INSERT OR IGNORE INTO samples(digest, text, source, channel, redactions, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (digest, text, source, channel, json.dumps(redactions), datetime.now(timezone.utc).isoformat()),
            )
            inserted = cursor.rowcount > 0
            if inserted:
                overflow = db.execute("SELECT COUNT(*) - ? FROM samples", (max_samples,)).fetchone()[0]
                if overflow > 0:
                    db.execute(
                        "DELETE FROM samples WHERE id IN (SELECT id FROM samples ORDER BY created_at ASC LIMIT ?)",
                        (overflow,),
                    )
            return inserted

    def texts(self) -> list[str]:
        with self.connect() as db:
            return [row[0] for row in db.execute("SELECT text FROM samples ORDER BY created_at ASC")]

    def rows(self) -> list[dict[str, object]]:
        with self.connect() as db:
            return [dict(row) for row in db.execute("SELECT * FROM samples ORDER BY created_at ASC")]

    def count(self) -> int:
        with self.connect() as db:
            return int(db.execute("SELECT COUNT(*) FROM samples").fetchone()[0])

    def clear(self) -> int:
        with self.connect() as db:
            count = int(db.execute("SELECT COUNT(*) FROM samples").fetchone()[0])
            db.execute("DELETE FROM samples")
            return count

    def delete_ids(self, ids: Iterable[int]) -> int:
        values = list(ids)
        if not values:
            return 0
        placeholders = ",".join("?" for _ in values)
        with self.connect() as db:
            cursor = db.execute(f"DELETE FROM samples WHERE id IN ({placeholders})", values)
            return cursor.rowcount

