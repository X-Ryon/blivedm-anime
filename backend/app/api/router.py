# -*- coding: utf-8 -*-
from fastapi import APIRouter
from backend.app.api.v1 import dm

# 创建顶层路由器
api_router = APIRouter()

# 注册 v1 版本的路由模块
# 可以在这里聚合多个模块的路由，例如:
# api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(dm.router, tags=["哔哩哔哩弹幕接口"])
