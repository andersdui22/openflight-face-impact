"""Local, versioned archive for server-produced synthetic Face Impact shots."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


class OfflineSessionArchive:
    """Persist each (session, shot) once, including rejected results."""

    def __init__(self, path: Path):
        self.path = path

    @contextmanager
    def _connection(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        try:
            with connection:
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS offline_shots (
                        session_id TEXT NOT NULL, shot_id TEXT NOT NULL,
                        saved_at TEXT NOT NULL, document TEXT NOT NULL,
                        PRIMARY KEY (session_id, shot_id)
                    )
                """)
                yield connection
        finally:
            connection.close()

    def save(self, evidence: dict, provenance: dict) -> dict:
        """Commit the first evidence for an identity before returning it."""
        session_id, shot_id = evidence["session_id"], evidence["shot_id"]
        saved_at = datetime.now(timezone.utc).isoformat()
        document = json.dumps({
            "schema_version": 1, "saved_at_utc": saved_at,
            "evidence": evidence, "provenance": provenance,
        }, allow_nan=False)
        with self._connection() as connection:
            connection.execute("""
                INSERT INTO offline_shots VALUES (?, ?, ?, ?)
                ON CONFLICT (session_id, shot_id) DO NOTHING
            """, (session_id, shot_id, saved_at, document))
            row = connection.execute(
                "SELECT document FROM offline_shots WHERE session_id = ? AND shot_id = ?",
                (session_id, shot_id),
            ).fetchone()
            return json.loads(row[0])["evidence"]

    def contains_session(self, session_id: str) -> bool:
        """Check session identity without reading or decoding shot documents."""
        with self._connection() as connection:
            return connection.execute(
                "SELECT 1 FROM offline_shots WHERE session_id = ? LIMIT 1", (session_id,),
            ).fetchone() is not None

    def list_sessions(self) -> list[dict]:
        """Return the 100 most recently recorded sessions."""
        with self._connection() as connection:
            rows = connection.execute("""
                SELECT session_id, COUNT(*), MAX(saved_at) FROM offline_shots
                GROUP BY session_id ORDER BY MAX(saved_at) DESC, session_id LIMIT 100
            """).fetchall()
        return [{"session_id": key, "shot_count": count, "saved_at_utc": saved_at}
                for key, count, saved_at in rows]

    def load(self, session_id: str) -> dict | None:
        """Return a complete session document suitable for JSON export."""
        with self._connection() as connection:
            rows = connection.execute("""
                SELECT document FROM offline_shots WHERE session_id = ?
                ORDER BY saved_at, shot_id
            """, (session_id,)).fetchall()
        if not rows:
            return None
        return {
            "schema_version": 1, "source": "offline_synthetic_analysis",
            "session_id": session_id, "shots": [json.loads(row[0]) for row in rows],
        }
