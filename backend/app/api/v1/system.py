from fastapi import APIRouter
from backend.app.schemas.config import AppConfig
from backend.app.services.config_service import config_service
from backend.common.resp import Resp

router = APIRouter()

@router.get("/config", response_model=Resp[AppConfig])
async def get_system_config():
    """
    获取系统配置
    """
    config = config_service.get_config()
    return Resp.success(data=config)
