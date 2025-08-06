"""
utils/database.py
Tiny SQLite helper used by the pipeline.

– One connection helper             → get_connection()
– Context-manager wrapper           → get_db_cursor()
– One-time table creator            → init_database()

All tables use the column name **file_hash** so they
match core/document_processor.py .
"""

from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from config.settings import PROCESSED_DIR

# --------------------------------------------------------------------------- #
#  paths & logging
# --------------------------------------------------------------------------- #
DB_PATH = PROCESSED_DIR / "metadata.db"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
#  connection helpers
# --------------------------------------------------------------------------- #
def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection (caller must close or commit)."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)


@contextmanager
def get_db_cursor():
    """`with get_db_cursor() as cur:` yields a cursor and commits/rolls back."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
#  schema creator
# --------------------------------------------------------------------------- #
def init_database() -> None:
    """
    Create the two tables **documents** and **chunks**.
    Column names MATCH those used by the rest of the code –
    especially `file_hash`.
    """
    with get_db_cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                file_hash     TEXT UNIQUE NOT NULL,
                filename      TEXT,
                file_size     INTEGER,
                file_type     TEXT,
                processed_at  TIMESTAMP,
                total_chunks  INTEGER,
                total_chars   INTEGER,
                language      TEXT,
                summary       TEXT
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id        INTEGER,
                idx           INTEGER,
                text          TEXT,
                embedding     BLOB,
                FOREIGN KEY (doc_id) REFERENCES documents(id)
            )
            """
        )

        log.info("SQLite schema ensured (documents / chunks)")


# --------------------------------------------------------------------------- #
#  quick health check (optional)
# --------------------------------------------------------------------------- #
def database_ok() -> bool:
    """Return True if we can SELECT 1; False otherwise."""
    try:
        with get_db_cursor() as cur:
            cur.execute("SELECT 1")
        return True
    except Exception as exc:  # noqa: BLE001
        log.error("Database health check failed: %s", exc)
        return False
