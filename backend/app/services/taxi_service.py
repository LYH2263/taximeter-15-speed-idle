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
        m["slow_speed_threshold"] = settings.get_slow_speed_threshold(self._c)
        return m
    def save_settings(self, slow_speed_threshold):
        # 非法值在仓库层直接拒绝，库里的旧值保持不变。
        settings.set_slow_speed_threshold(self._c, float(slow_speed_threshold))
        return self.settings()
    def history(self, limit=50): return runs.list_recent(self._c, limit)
    def fare(self, distance_km, slow_min, night, trip_id, persist, duration_min=None):
        t = tariff.get_active(self._c)
        threshold = settings.get_slow_speed_threshold(self._c)
        r = calc_fare(
            distance_km,
            slow_min,
            night,
            t,
            duration_min=duration_min,
            slow_speed_threshold=threshold,
        )
        if persist:
            payload = {"distance_km": distance_km, "night": night}
            if duration_min is not None:
                # 记录原始口径；计入分钟快照在 result_json 里，改阈值不影响已写记录。
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
