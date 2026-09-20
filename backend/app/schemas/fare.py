from pydantic import BaseModel, Field, model_validator


class FareRequest(BaseModel):
    distance_km: float = Field(ge=0)
    slow_min: float | None = Field(default=None, ge=0)
    duration_min: float | None = Field(default=None, ge=0)
    night: bool = False
    trip_id: int | None = None
    persist: bool = True

    @model_validator(mode="after")
    def _mutex(self):
        # 低速分钟与行驶时长互斥：同时提交直接拒绝，不写任何记录
        if self.slow_min is not None and self.duration_min is not None:
            raise ValueError("slow_min 与 duration_min 只能二选一")
        return self


class CompareRequest(BaseModel):
    distance_km: float = Field(ge=0)
    slow_min: float = Field(ge=0)
    persist: bool = False


class SettingsUpdate(BaseModel):
    # 阈值时速必须为正；0、负数、NaN 一律拒绝
    slow_threshold_kmh: float = Field(gt=0)
