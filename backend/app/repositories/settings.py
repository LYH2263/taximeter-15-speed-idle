import sqlite3

SLOW_THRESHOLD_KEY = "slow_threshold_kmh"
DEFAULT_SLOW_THRESHOLD = 12.0


def get_map(conn):
    return {r["key"]: r["value"] for r in conn.execute("SELECT * FROM settings").fetchall()}


def get_float(conn, key: str, default: float | None = None) -> float | None:
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    if row is None:
        return default
    return float(row["value"])


def get_slow_threshold(conn) -> float:
    return get_float(conn, SLOW_THRESHOLD_KEY, DEFAULT_SLOW_THRESHOLD)


def upsert(conn, key: str, value) -> None:
    conn.execute(
        "INSERT INTO settings(key,value) VALUES (?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, str(value)),
    )
    conn.commit()
