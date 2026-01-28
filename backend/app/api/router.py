# -*- coding: utf-8 -*-
from fastapi import APIRouter
from backend.app.api.v1.listener import router as listener_router
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.gift import router as gift_router
from backend.app.api.v1.system import router as system_router

from backend.core.conf import settings

# 创建顶层路由器
v1 = APIRouter(prefix=settings.API_V1_PATH)

# 注册 v1 版本的路由模块
v1.include_router(auth_router, tags=["Auth"])
v1.include_router(listener_router, tags=["Listener"])
v1.include_router(gift_router, tags=["Gift"])
v1.include_router(system_router, tags=["System"])
