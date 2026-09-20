from fastapi import APIRouter
from app.schemas.settings import SettingsUpdate
from app.services.taxi_service import TaxiService
router = APIRouter()
@router.get("/settings")
def settings():
    with TaxiService() as s: return s.settings()
@router.post("/settings")
def update_settings(body: SettingsUpdate):
    with TaxiService() as s:
        # 非正数在 schema 层即 422；这里再兜一层，任何保存失败都不改变原值。
        return s.save_settings(body.slow_speed_threshold)
