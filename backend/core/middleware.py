from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.services.uidinfo_service import uidinfo_service

class BilibiliUserInfoMiddleware(BaseHTTPMiddleware):
    """
    中间件：尝试从请求中获取UID，并从B站获取用户信息
    """
    async def dispatch(self, request: Request, call_next):
        # 尝试从 Query Params 获取 uid
        uid = request.query_params.get("uid")
        
        if uid:
            logger.info(f"从请求中获取到uid: {uid}, 尝试从B站获取用户信息...")
            try:
                user_info = await uidinfo_service.get_user_info_by_uid(uid, cookies=dict(request.cookies))
                if user_info:
                    # 将用户信息注入到 request.state 中
                    request.state.bili_user_info = user_info
                    logger.info(f"获取到用户信息:uid{uid} 用户:{user_info['user_name']}")
                else:
                    logger.warning(f"获取用户信息失败：uid{uid}")
            except Exception as e:
                logger.error(f"从uid {uid} 获取用户信息时出错: {e}")
        
        response = await call_next(request)
        return response

