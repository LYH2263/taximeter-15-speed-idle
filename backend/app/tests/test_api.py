import json
import os
import tempfile

# 在导入 app 之前把数据目录指到临时库，避免污染开发库。
_TMP = tempfile.mkdtemp(prefix="taxitest_")
os.environ.setdefault("DATA_DIR", _TMP)

import sqlite3  # noqa: E402

from fastapi.testclient import TestClient  # noqa: E402

from app.db import DB_PATH  # noqa: E402
from app.main import app  # noqa: E402


def _runs():
    with sqlite3.connect(DB_PATH) as c:
        return c.execute("SELECT id, kind, input_json, result_json FROM calc_runs ORDER BY id").fetchall()


def _threshold():
    with sqlite3.connect(DB_PATH) as c:
        row = c.execute("SELECT value FROM settings WHERE key='slow_speed_threshold'").fetchone()
    return float(row[0])


with TestClient(app) as client:  # 触发 startup 建表/种子
    pass


def test_mutually_exclusive_rejected_without_record():
    before = len(_runs())
    r = client.post("/api/fare", json={"distance_km": 6, "slow_min": 5, "duration_min": 40})
    assert r.status_code == 422
    assert len(_runs()) == before  # 拒绝即不写记录


def test_readonly_duration_trial_writes_nothing():
    before = len(_runs())
    r = client.post("/api/fare", json={"distance_km": 6, "duration_min": 40, "persist": False})
    assert r.status_code == 200
    body = r.json()
    assert body["run_id"] is None
    # 40 - 6/12*60 = 10 分钟
    assert body["slow_min"] == 10
    assert body["slow_fee"] == 8.0
    assert body["total"] == 26.5
    assert body["slow_speed_threshold"] == 12
    assert len(_runs()) == before  # 只读试算不落库


def test_direct_slow_min_unchanged():
    r = client.post("/api/fare", json={"distance_km": 5, "slow_min": 2, "persist": False})
    body = r.json()
    assert body["slow_min"] == 2
    assert body["slow_fee"] == 1.6
    assert body["total"] == 17.6


def test_threshold_save_failure_keeps_old_value():
    old = _threshold()
    for bad in (0, -3):
        r = client.post("/api/settings", json={"slow_speed_threshold": bad})
        assert r.status_code == 422
        assert _threshold() == old  # 保存失败不得改原值
    r = client.post("/api/settings", json={"slow_speed_threshold": 20})
    assert r.status_code == 200
    assert _threshold() == 20
    # 改阈值后只读试算的计入分钟随之变化：40 - 6/20*60 = 22
    body = client.post("/api/fare", json={"distance_km": 6, "duration_min": 40, "persist": False}).json()
    assert body["slow_min"] == 22


def test_persisted_record_survives_threshold_change():
    client.post("/api/settings", json={"slow_speed_threshold": 12})
    saved = client.post("/api/fare", json={"distance_km": 6, "duration_min": 40, "persist": True}).json()
    rid = saved["run_id"]
    assert saved["slow_min"] == 10
    # 之后改阈值，已写入记录的计入分钟与低速费快照不变。
    client.post("/api/settings", json={"slow_speed_threshold": 25})
    row = next(r for r in _runs() if r[0] == rid)
    result = json.loads(row[3])
    assert result["slow_min"] == 10
    assert result["slow_fee"] == 8.0
