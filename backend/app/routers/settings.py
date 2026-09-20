from fastapi import APIRouter, HTTPException
from app.schemas.fare import SettingsUpdate
from app.services.taxi_service import TaxiService
router = APIRouter()
@router.get("/settings")
def settings():
    with TaxiService() as s: return s.settings()
@router.post("/settings")
def update_settings(body: SettingsUpdate):
    # gt=0 校验在 schema 层完成（422）；只有校验通过才会写库，保存失败原值不变
    try:
        with TaxiService() as s: return s.update_settings(body.slow_threshold_kmh)
    except ValueError:
        raise HTTPException(status_code=422, detail="slow_threshold_kmh must be positive")
