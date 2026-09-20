from pydantic import BaseModel, Field, model_validator

# 低速费两种口径：直接给低速分钟，或给行驶时长+公里按阈值时速折算。
# 二者只能提交其一，同时提交直接拒绝（422），不写任何记录。


class FareRequest(BaseModel):
    distance_km: float = Field(ge=0)
    slow_min: float | None = Field(default=None, ge=0)
    duration_min: float | None = Field(default=None, ge=0)
    night: bool = False
    trip_id: int | None = None
    persist: bool = True

    @model_validator(mode="after")
    def _check_slow_input(self):
        if self.slow_min is not None and self.duration_min is not None:
            raise ValueError("slow_min 与 duration_min 只能提交其一")
        return self


class CompareRequest(BaseModel):
    # 昼夜对比沿用直接低速分钟，不参与时长折算。
    distance_km: float = Field(ge=0)
    slow_min: float = Field(ge=0)
    persist: bool = False
