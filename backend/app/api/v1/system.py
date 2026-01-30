from fastapi import APIRouter
from backend.app.schemas.config import AppConfig
from backend.app.services.config_service import config_service
from backend.common.resp import Resp

router = APIRouter()

@router.get("/config", response_model=Resp[AppConfig])
async def get_system_config():
    """
    获取系统配置

    Description:
        读取当前系统的所有配置项。

    Args:
        无

    Return:
        Resp[AppConfig]: 包含系统配置对象的响应

    Raises:
        无
    """
    config = config_service.get_config()
    return Resp.success(data=config)

@router.post("/config", response_model=Resp[AppConfig])
async def update_system_config(config: AppConfig):
    """
    更新系统配置

    Description:
        全量更新系统配置，并持久化到配置文件。

    Args:
        config (AppConfig): 完整的配置对象

    Return:
        Resp[AppConfig]: 更新后的系统配置

    Raises:
        无
    """
    updated_config = config_service.update_config(config)
    return Resp.success(data=updated_config)

@router.post("/config/reset", response_model=Resp[AppConfig])
async def reset_system_config():
    """
    恢复默认配置

    Description:
        将系统配置重置为模板中的默认值。

    Args:
        无

    Return:
        Resp[AppConfig]: 重置后的系统配置

    Raises:
        无
    """
    reset_config = config_service.reset_config()
    return Resp.success(data=reset_config)
