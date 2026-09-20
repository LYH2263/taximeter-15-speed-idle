def _counted_slow_min(distance_km: float, duration_min: float, threshold: float) -> float:
    # 时长减去按阈值时速折算的“非低速行驶时间”（公里 / 时速 * 60），再与零取大。
    return max(0.0, float(duration_min) - float(distance_km) / float(threshold) * 60.0)


def calc_fare(
    distance_km: float,
    slow_min: float | None = None,
    night: bool = False,
    tariff: dict | None = None,
    *,
    duration_min: float | None = None,
    slow_speed_threshold: float | None = None,
) -> dict:
    tariff = tariff or {}
    base = float(tariff["start_price"])
    include = float(tariff["start_include_km"])
    per_km = float(tariff["per_km"])
    per_slow = float(tariff["per_slow_min"])
    night_f = float(tariff.get("night_factor", 1.0)) if night else 1.0
    dist = max(0.0, float(distance_km) - include)
    mile = dist * per_km
    # 给了行驶时长就按阈值时速折算计入低速分钟；否则沿用直接提交的低速分钟（改造前口径）。
    if duration_min is not None:
        counted = _counted_slow_min(distance_km, duration_min, slow_speed_threshold)
    else:
        counted = float(slow_min or 0.0)
    slow = counted * per_slow
    sub = base + mile + slow
    return {
        "distance_km": round(float(distance_km), 2),
        "duration_min": round(float(duration_min), 1) if duration_min is not None else None,
        # slow_min 即“计入低速分钟”：折算口径下为折算结果，并随阈值设置即时变化（只读）。
        "slow_min": round(counted, 1),
        "slow_speed_threshold": round(float(slow_speed_threshold), 1) if slow_speed_threshold is not None else None,
        "night": night,
        "night_factor": night_f,
        "start": round(base * night_f, 2),
        "mileage": round(mile * night_f, 2),
        "slow_fee": round(slow * night_f, 2),
        "total": round(sub * night_f, 2),
    }
