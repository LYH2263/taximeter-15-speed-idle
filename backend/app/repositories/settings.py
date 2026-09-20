import sqlite3

DEFAULT_SLOW_SPEED_THRESHOLD = 12.0
_SLOW_SPEED_THRESHOLD_KEY = "slow_speed_threshold"


def get_map(conn):
    return {r["key"]: r["value"] for r in conn.execute("SELECT * FROM settings").fetchall()}


def get_slow_speed_threshold(conn) -> float:
    row = conn.execute(
        "SELECT value FROM settings WHERE key=?", (_SLOW_SPEED_THRESHOLD_KEY,)
    ).fetchone()
    if row is None:
        return DEFAULT_SLOW_SPEED_THRESHOLD
    try:
        value = float(row["value"])
    except (TypeError, ValueError):
        return DEFAULT_SLOW_SPEED_THRESHOLD
    # 库里的脏数据不应让计价崩掉：非正数回退默认值。
    return value if value > 0 else DEFAULT_SLOW_SPEED_THRESHOLD


def set_slow_speed_threshold(conn, value: float) -> None:
    # 必须为正；先抛异常再动手，保存失败时原值不变。
    if value <= 0:
        raise ValueError("阈值时速必须为正")
    conn.execute(
        "INSERT INTO settings(key,value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (_SLOW_SPEED_THRESHOLD_KEY, str(float(value))),
    )
    conn.commit()
