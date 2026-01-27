# -*- coding: utf-8 -*-
from backend.app.schemas import user as user_schema
from backend.app.crud.user import crud_user
from backend.database.db import AsyncSessionLocal
from backend.app.models import user as user_model

class UserService:
    async def create_user(self, user: user_schema.UserCreate) -> user_model.User:
        async with AsyncSessionLocal() as db:
            try:
                db_user = await crud_user.create_user(db, user)
                await db.commit()
                await db.refresh(db_user)
                return db_user
            except Exception as e:
                await db.rollback()
                raise e

    async def get_user_by_name(self, user_name: str) -> user_model.User | None:
        async with AsyncSessionLocal() as db:
            return await crud_user.get_user_by_name(db, user_name)

    async def delete_user(self, user_name: str) -> bool:
        """
        删除用户

        Args:
            user_name (str): 用户名称

        Returns:
            bool: 是否删除成功
        """
        async with AsyncSessionLocal() as db:
            try:
                success = await crud_user.delete_user_by_name(db, user_name)
                if success:
                    await db.commit()
                return success
            except Exception as e:
                await db.rollback()
                raise e

# 实例化对象
user_service = UserService()
