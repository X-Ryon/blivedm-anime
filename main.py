# -*- coding: utf-8 -*-
import uvicorn
from fastapi import FastAPI
from backend.app.api import endpoints
from backend.app.database.db import engine, Base

# 创建 FastAPI 应用
app = FastAPI(
    title="Bilibili Live Monitor API",
    description="监听 Bilibili 直播间弹幕、礼物、上舰、SC 并实时推送",
    version="1.0.0"
)

# 注册路由
app.include_router(endpoints.router, prefix="/api", tags=["live"])

# 事件处理：启动时初始化数据库
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # 仅开发环境使用：自动创建表
        # 生产环境建议使用 Alembic
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    # 使用 Uvicorn 启动
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
