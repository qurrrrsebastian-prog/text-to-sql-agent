"""database.py — SQLite persistence for the Text-to-SQL Agent.

Stores query history, a cached schema and an audit log in `app.db`. This is
separate from the queried demo database (data/rkari_sales.db).

Author: Avatar Putra Sigit | GitHub: qurrrrsebastian-prog
"""
import os
import sqlite3
from datetime import datetime
from typing import List

import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection (metadata DB) with row access by name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create metadata tables. Call once at app start."""
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS query_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT,
            natural_language TEXT, generated_sql TEXT, execution_time_ms REAL,
            row_count INTEGER, success BOOLEAN);
        CREATE TABLE IF NOT EXISTS schema_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT, table_name TEXT,
            column_name TEXT, data_type TEXT, sample_values TEXT);
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, user TEXT,
            action TEXT, details TEXT);
        """
    )
    conn.commit()
    conn.close()


def add_log(action: str, details: str = "", user: str = "anonymous") -> None:
    """Append an entry to the audit log."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO audit_log (timestamp, user, action, details) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(timespec="seconds"), user, action, details),
    )
    conn.commit()
    conn.close()


# --------------------------------------------------------------------------- #
# Query history
# --------------------------------------------------------------------------- #
def add_query(natural_language: str, generated_sql: str, execution_time_ms: float,
              row_count: int, success: bool) -> None:
    """Record one NL -> SQL execution."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO query_history
           (timestamp, natural_language, generated_sql, execution_time_ms,
            row_count, success)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (datetime.now().isoformat(timespec="seconds"), natural_language,
         generated_sql, execution_time_ms, row_count, 1 if success else 0),
    )
    conn.commit()
    conn.close()


def get_query_history(limit: int = 200) -> pd.DataFrame:
    """Return query history, newest first."""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM query_history ORDER BY id DESC LIMIT ?", conn, params=[limit])
    conn.close()
    return df


def clear_query_history() -> None:
    """Delete all query history."""
    conn = get_connection()
    conn.execute("DELETE FROM query_history")
    conn.commit()
    conn.close()


# --------------------------------------------------------------------------- #
# Schema cache
# --------------------------------------------------------------------------- #
def refresh_schema_cache(target_db_path: str) -> int:
    """Introspect the target SQLite DB and cache its schema. Returns column count."""
    conn = get_connection()
    conn.execute("DELETE FROM schema_cache")
    count = 0
    try:
        tgt = sqlite3.connect(target_db_path)
        tgt.row_factory = sqlite3.Row
        tables = [r[0] for r in tgt.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%'")]
        for table in tables:
            cols = tgt.execute(f"PRAGMA table_info({table})").fetchall()
            for col in cols:
                samples = tgt.execute(
                    f"SELECT DISTINCT {col['name']} FROM {table} "
                    f"WHERE {col['name']} IS NOT NULL LIMIT 3").fetchall()
                sample_str = ", ".join(str(s[0]) for s in samples)
                conn.execute(
                    """INSERT INTO schema_cache
                       (table_name, column_name, data_type, sample_values)
                       VALUES (?, ?, ?, ?)""",
                    (table, col["name"], col["type"] or "TEXT", sample_str),
                )
                count += 1
        tgt.close()
        conn.commit()
    except Exception:  # noqa: BLE001
        pass
    finally:
        conn.close()
    return count


def get_schema_cache() -> pd.DataFrame:
    """Return the cached schema as a DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT table_name, column_name, data_type, sample_values "
        "FROM schema_cache ORDER BY table_name, id",
        conn,
    )
    conn.close()
    return df
