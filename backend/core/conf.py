from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """全局配置"""
    # .env 当前环境
    ENVIRONMENT: Literal["dev", "prod"] = "dev"

    # 接口配置
    API_V1_PATH: str = "/api/v1"
    APP_TITLE: str = "Bilibili Live dm API"
    APP_DESCRIPTION: str = "监听 Bilibili 直播间弹幕、礼物、上舰、SC 并实时推送"
    FASTAPI_DOCS_URL: str = "/docs"
    FASTAPI_REDOC_URL: str = "/redoc"
    FASTAPI_OPENAPI_URL: str = "/openapi.json"

    # Bilibili API 配置
    BILIBILI_API_ROOM_INFO: str = "https://api.live.bilibili.com/room/v1/Room/get_info"
    BILIBILI_API_LIVE_USER_INFO: str = "https://api.live.bilibili.com/live_user/v1/Master/info"
    BILIBILI_API_GIFT_LIST: str = "https://api.live.bilibili.com/xlive/web-room/v1/giftPanel/roomGiftList"
    QR_GENERATE_URL: str = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
    QR_POLL_URL: str = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
    QR_API_URL: str = "https://api.qrserver.com/v1/create-qr-code/"
    USER_INFO_URL: str = "https://api.bilibili.com/x/web-interface/nav"
    USER_SPACE_URL: str = "https://api.bilibili.com/x/space/acc/info"
    
    HEADERS: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.bilibili.com/"
    }
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///dmjdb.db"

    # CORS
    CORS_ALLOWED_ORIGINS: list[str] = [  # 末尾不带斜杠
        "http://127.0.0.1:5000",
        "http://localhost:5173",
    ]
    CORS_EXPOSE_HEADERS: list[str] = [
        "X-Request-ID",
    ]

    # 时间配置
    DATETIME_TIMEZONE: str = "Asia/Shanghai"
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    
    # 日志
    LOG_FORMAT: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <lvl>{level: <8}</> | <cyan>{extra[request_id]}</> | <lvl>{message}</>"
    )

    # 日志（控制台）
    LOG_STD_LEVEL: str = "INFO"

    # 日志（文件）
    LOG_FILE_ACCESS_LEVEL: str = "INFO"
    LOG_FILE_ERROR_LEVEL: str = "ERROR"


@lru_cache
def get_settings() -> Settings:
    """获取全局配置单例"""
    return Settings()


# 创建全局配置实例
settings = get_settings()
