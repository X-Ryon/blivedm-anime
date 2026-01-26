# -*- coding: utf-8 -*-
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# 数据库文件路径
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./sql_app.db"

# 创建异步引擎
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# 声明性基类
Base = declarative_base()

# 依赖项：获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
