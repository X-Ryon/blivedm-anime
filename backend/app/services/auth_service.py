# -*- coding: utf-8 -*-
import logging
from typing import Optional
from backend.app.schemas.auth import UserInfo
from backend.app.crud.auth import crud_auth
from backend.database.db import AsyncSessionLocal
from backend.app.models.auth import Auth as Auth_model

logger = logging.getLogger(__name__)

class AuthService:
    """
    认证服务
    负责用户的创建、查询、删除等业务逻辑
    """
    
    async def create_user(self, user: UserInfo) -> Auth_model:
        """
        创建新用户
        
        Args:
            user (UserInfo): 用户信息对象
            
        Returns:
            Auth_model: 创建成功的用户模型对象
            
        Raises:
            Exception: 创建失败抛出异常
        """
        async with AsyncSessionLocal() as db:
            try:
                db_user = await crud_auth.create_user(db, user)
                await db.commit()
                await db.refresh(db_user)
                logger.info(f"成功创建用户: {user.user_name}")
                return db_user
            except Exception as e:
                await db.rollback()
                logger.error(f"创建用户失败: {e}")
                raise e

    async def get_user_by_name(self, user_name: str) -> Optional[Auth_model]:
        """
        根据用户名获取用户信息
        
        Args:
            user_name (str): 用户名
            
        Returns:
            Optional[Auth_model]: 用户模型对象，如果不存在返回 None
        """
        async with AsyncSessionLocal() as db:
            try:
                return await crud_auth.get_user_by_name(db, user_name)
            except Exception as e:
                logger.error(f"获取用户 {user_name} 失败: {e}")
                return None

    async def get_user_by_uid(self, uid: str) -> Optional[Auth_model]:
        """
        根据UID获取用户信息
        
        Args:
            uid (str): 用户UID
            
        Returns:
            Optional[Auth_model]: 用户模型对象，如果不存在返回 None
        """
        async with AsyncSessionLocal() as db:
            try:
                return await crud_auth.get_user_by_uid(db, uid)
            except Exception as e:
                logger.error(f"获取用户UID {uid} 失败: {e}")
                return None

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
                success = await crud_auth.delete_user_by_name(db, user_name)
                if success:
                    await db.commit()
                    logger.info(f"成功删除用户: {user_name}")
                else:
                    logger.warning(f"删除用户失败，用户不存在: {user_name}")
                return success
            except Exception as e:
                await db.rollback()
                logger.error(f"删除用户异常: {e}")
                raise e

    async def delete_user_by_uid(self, uid: str) -> bool:
        """
        根据UID删除用户
        """
        async with AsyncSessionLocal() as db:
            try:
                success = await crud_auth.delete_user_by_uid(db, uid)
                if success:
                    await db.commit()
                    logger.info(f"成功删除用户UID: {uid}")
                return success
            except Exception as e:
                await db.rollback()
                logger.error(f"删除用户UID {uid} 异常: {e}")
                raise e

    async def get_all_users(self):
        """
        获取所有用户
        """
        async with AsyncSessionLocal() as db:
             try:
                return await crud_auth.get_all_users(db)
             except Exception as e:
                logger.error(f"获取所有用户失败: {e}")
                return []

# 实例化对象
auth_service : AuthService = AuthService()
