def counted_from_duration(duration_min: float, distance_km: float, threshold_kmh: float) -> float:
    """按时速折算计入低速的分钟：时长 - 公里/阈值时速*60，再与 0 取大。阈值必须为正。"""
    threshold_kmh = float(threshold_kmh)
    if threshold_kmh <= 0:
        raise ValueError("threshold_kmh must be positive")
    return max(0.0, float(duration_min) - float(distance_km) / threshold_kmh * 60.0)


def calc_fare(
    distance_km: float,
    slow_min: float | None = 0.0,
    night: bool = False,
    tariff: dict | None = None,
    *,
    duration_min: float | None = None,
    threshold_kmh: float | None = None,
) -> dict:
    tariff = tariff or {}
    base = float(tariff["start_price"])
    include = float(tariff["start_include_km"])
    per_km = float(tariff["per_km"])
    per_slow = float(tariff["per_slow_min"])
    night_f = float(tariff.get("night_factor", 1.0)) if night else 1.0
    dist = max(0.0, float(distance_km) - include)
    mile = dist * per_km
    # 提供行驶时长时按时速折算计入低速分钟，否则沿用直接提交的低速分钟（改造前行为）
    if duration_min is not None:
        counted = counted_from_duration(duration_min, distance_km, threshold_kmh)
    else:
        counted = float(slow_min or 0.0)
    slow = counted * per_slow
    sub = base + mile + slow
    return {
        "distance_km": round(float(distance_km), 2),
        "slow_min": round(counted, 1),
        "night": night,
        "night_factor": night_f,
        "duration_min": round(float(duration_min), 1) if duration_min is not None else None,
        "threshold_kmh": round(float(threshold_kmh), 2) if threshold_kmh is not None else None,
        "start": round(base * night_f, 2),
        "mileage": round(mile * night_f, 2),
        "slow_fee": round(slow * night_f, 2),
        "total": round(sub * night_f, 2),
    }
