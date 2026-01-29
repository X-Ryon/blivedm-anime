import uvicorn
import uuid
from fastapi import FastAPI, Request
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app.api.router import v1
from backend.database.db import engine, Base
from backend.core.conf import settings
from backend.core.logger import setup_logging
from backend.core.middleware import BilibiliUserInfoMiddleware
from backend.common.exception.handler import register_exception_handler

# 设置日志
setup_logging()

app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    docs_url=settings.FASTAPI_DOCS_URL,
    redoc_url=settings.FASTAPI_REDOC_URL,
    openapi_url=settings.FASTAPI_OPENAPI_URL,
)

# 注册全局异常处理器
register_exception_handler(app)

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    with logger.contextualize(request_id=request_id):
        logger.info(f"Request started: {request.method} {request.url}")
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=settings.CORS_EXPOSE_HEADERS,
)

# 注册自定义中间件
app.add_middleware(BilibiliUserInfoMiddleware)

# 注册路由
app.include_router(v1)

# 挂载静态文件
import os
static_dir = os.path.join(os.getcwd(), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.on_event("startup")
async def startup():
    # 检查并创建 static/asset 目录
    import os
    from pathlib import Path
    
    # 假设 static 目录在项目根目录下
    base_dir = Path(__file__).resolve().parent.parent
    asset_dir = base_dir / "static" / "asset"
    
    if not asset_dir.exists():
        logger.info(f"Creating asset directory: {asset_dir}")
        asset_dir.mkdir(parents=True, exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
