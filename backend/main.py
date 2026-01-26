import uvicorn
import uuid
from fastapi import FastAPI, Request
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.router import api_router
from backend.database.db import engine, Base
from backend.core.conf import settings
from backend.core.logger import setup_logging

# 设置日志
setup_logging()

app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    docs_url=settings.FASTAPI_DOCS_URL,
    redoc_url=settings.FASTAPI_REDOC_URL,
    openapi_url=settings.FASTAPI_OPENAPI_URL,
)

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

# 注册路由
app.include_router(api_router, prefix=settings.API_V1_PATH)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
