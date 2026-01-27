# -*- coding: utf-8 -*-
from backend.app.schemas import schemas
from backend.app.crud.crud import crud_dao
from backend.database.db import AsyncSessionLocal
from backend.app.models import models

class UserService:
    async def create_user(self, user: schemas.UserCreate) -> models.User:
        async with AsyncSessionLocal() as db:
            return await crud_dao.create_user(db, user)

    async def get_user_by_name(self, user_name: str) -> models.User | None:
        async with AsyncSessionLocal() as db:
            return await crud_dao.get_user_by_name(db, user_name)

    async def delete_user(self, user_name: str) -> bool:
        """
        删除用户

        Args:
            user_name (str): 用户名称

        Returns:
            bool: 是否删除成功
        """
        async with AsyncSessionLocal() as db:
            return await crud_dao.delete_user_by_name(db, user_name)

# 实例化对象
user_service = UserService()
