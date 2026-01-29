# -*- coding: utf-8 -*-
from fastapi import APIRouter
from backend.app.api.v1.listener import router as listener_router
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.gift import router as gift_router
from backend.app.api.v1.system import router as system_router
from backend.app.api.v1.resources import router as resources_router
from backend.app.api.v1.proxy import router as proxy_router
from backend.app.api.v1.danmaku import router as danmaku_router

from backend.core.conf import settings

# 创建顶层路由器
v1 = APIRouter(prefix=settings.API_V1_PATH)

# 注册 v1 版本的路由模块
v1.include_router(auth_router, tags=["Auth"])
v1.include_router(listener_router, tags=["Listener"], prefix="/listener")
v1.include_router(gift_router, tags=["Gift"], prefix="/gift")
v1.include_router(danmaku_router, tags=["Danmaku"], prefix="/danmaku")
v1.include_router(system_router, tags=["System"])
v1.include_router(resources_router, tags=["Resources"], prefix="/resources")
v1.include_router(proxy_router, tags=["Proxy"], prefix="/proxy")
