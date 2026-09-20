from pydantic import BaseModel, Field


class SettingsUpdate(BaseModel):
    # 阈值时速必须为正；非正数在入口即拒绝，原值保持不变。
    slow_speed_threshold: float = Field(gt=0)
