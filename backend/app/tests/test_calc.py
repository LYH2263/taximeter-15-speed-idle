import pytest
from pydantic import ValidationError

from app.engines.night_compare import compare_day_night
from app.engines.tariff_breakdown import calc_fare, counted_from_duration
from app.schemas.fare import FareRequest, SettingsUpdate

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


def test_counted_formula():
    # 30 分钟行驶 4 公里，阈值 12km/h：4/12*60=20 分钟按阈值行驶，剩余 10 分钟计入低速
    assert counted_from_duration(30, 4, 12) == pytest.approx(10.0)


def test_counted_floored_at_zero():
    # 全程均速高于阈值时不计低速
    assert counted_from_duration(10, 10, 12) == 0.0


def test_counted_threshold_must_be_positive():
    with pytest.raises(ValueError):
        counted_from_duration(30, 4, 0)
    with pytest.raises(ValueError):
        counted_from_duration(30, 4, -5)


def test_calc_fare_duration_mode():
    r = calc_fare(4, None, False, T, duration_min=30, threshold_kmh=12)
    # 计入 10 分钟 * 0.8 = 8；起步 11 + (4-3)*2.5=2.5 → 21.5
    assert r["slow_min"] == 10.0
    assert r["slow_fee"] == 8.0
    assert r["total"] == 21.5
    assert r["duration_min"] == 30.0
    assert r["threshold_kmh"] == 12.0


def test_calc_fare_direct_mode_unchanged():
    # 只给低速分钟时与改造前完全一致，且不带折算字段
    r = calc_fare(5, 2, False, T)
    assert r["total"] == 17.6
    assert r["duration_min"] is None
    assert r["threshold_kmh"] is None


def test_request_rejects_both_slow_and_duration():
    # 同时提交低速分钟与行驶时长：拒绝
    with pytest.raises(ValidationError):
        FareRequest(distance_km=4, slow_min=3, duration_min=30)


def test_request_accepts_either():
    assert FareRequest(distance_km=4, slow_min=3).duration_min is None
    assert FareRequest(distance_km=4, duration_min=30).slow_min is None


def test_settings_threshold_must_be_positive():
    with pytest.raises(ValidationError):
        SettingsUpdate(slow_threshold_kmh=0)
    with pytest.raises(ValidationError):
        SettingsUpdate(slow_threshold_kmh=-1)
    assert SettingsUpdate(slow_threshold_kmh=12).slow_threshold_kmh == 12
