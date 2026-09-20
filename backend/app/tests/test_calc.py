from app.engines.night_compare import compare_day_night
from app.engines.tariff_breakdown import calc_fare

T = {"start_price": 11, "start_include_km": 3, "per_km": 2.5, "per_slow_min": 0.8, "night_factor": 1.2}

def test_day_short():
    r = calc_fare(5, 2, False, T)
    assert r["total"] == 17.6
    assert r["mileage"] == 5.0

def test_night_long():
    r = calc_fare(18, 12, True, T)
    assert r["total"] == 69.72

def test_compare_delta():
    c = compare_day_night(18, 12, T)
    assert c["night_total"] > c["day_total"]

def test_duration_counts_slow_min():
    # 40 分钟开 6 公里，阈值 12km/h：非低速时间 = 6/12*60 = 30 分钟，计入低速 10 分钟。
    r = calc_fare(6, duration_min=40, night=False, tariff=T, slow_speed_threshold=12)
    assert r["slow_min"] == 10
    assert r["slow_fee"] == 8.0
    assert r["total"] == 26.5
    assert r["slow_speed_threshold"] == 12
    assert r["duration_min"] == 40

def test_duration_fast_trip_counts_zero():
    # 全程均速高于阈值，计入分钟与零取大 → 0，不得出现负低速费。
    r = calc_fare(6, duration_min=20, night=False, tariff=T, slow_speed_threshold=12)
    assert r["slow_min"] == 0
    assert r["slow_fee"] == 0
    assert r["total"] == 18.5

def test_duration_follows_threshold():
    # 阈值提到 20km/h：非低速时间 6/20*60 = 18 分钟，计入低速 22 分钟。
    r = calc_fare(6, duration_min=40, night=False, tariff=T, slow_speed_threshold=20)
    assert r["slow_min"] == 22
    assert r["slow_fee"] == 17.6

def test_direct_slow_min_backward_compatible():
    # 只给低速分钟时与改造前完全一致，且不回传阈值折算口径。
    r = calc_fare(5, 2, False, T)
    assert r["total"] == 17.6
    assert r["slow_min"] == 2
    assert r["duration_min"] is None
