from app.db import connect
from app.engines.night_compare import compare_day_night
from app.engines.tariff_breakdown import calc_fare
from app.repositories import runs, settings, tariff, trips

class TaxiService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_trips(self): return trips.list_all(self._c)
    def trip(self, tid): return trips.get(self._c, tid)
    def tariff(self): return tariff.get_active(self._c)
    def settings(self):
        m = settings.get_map(self._c)
        m.setdefault(settings.SLOW_THRESHOLD_KEY, str(settings.DEFAULT_SLOW_THRESHOLD))
        return m
    def slow_threshold(self): return settings.get_slow_threshold(self._c)
    def update_settings(self, slow_threshold_kmh):
        # 阈值时速必须为正；非法值直接拒绝，不写库，原值保持不变
        v = float(slow_threshold_kmh)
        if not (v == v and v > 0):  # 同时排除 NaN
            raise ValueError("slow_threshold_kmh must be positive")
        settings.upsert(self._c, settings.SLOW_THRESHOLD_KEY, v)
        return self.settings()
    def history(self, limit=50): return runs.list_recent(self._c, limit)
    def fare(self, distance_km, slow_min, night, trip_id, persist, duration_min=None):
        t = tariff.get_active(self._c)
        threshold = self.slow_threshold() if duration_min is not None else None
        r = calc_fare(distance_km, slow_min or 0.0, night, t,
                      duration_min=duration_min, threshold_kmh=threshold)
        if persist:
            payload = {"distance_km": distance_km, "night": night}
            if duration_min is not None:
                payload["duration_min"] = duration_min
            else:
                payload["slow_min"] = slow_min
            rid = runs.insert(self._c, "fare", payload, r, trip_id)
        else:
            rid = None
        return {"run_id": rid, **r}
    def compare(self, distance_km, slow_min, persist):
        t = tariff.get_active(self._c)
        r = compare_day_night(distance_km, slow_min, t)
        rid = runs.insert(self._c, "compare", {"distance_km": distance_km, "slow_min": slow_min}, r, None) if persist else None
        return {"run_id": rid, **r}
    def dashboard(self):
        items = trips.list_all(self._c)
        clean = [x for x in items if "种子" not in x["label"]]
        dirty = [x for x in items if "种子" in x["label"]]
        return {"trip_count": len(items), "clean": len(clean), "dirty": len(dirty)}
