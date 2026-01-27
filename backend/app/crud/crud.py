# -*- coding: utf-8 -*-
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.models import models
from backend.app.schemas import schemas

class CRUDDao:
    async def create_danmaku(self, db: AsyncSession, danmaku: schemas.DanmakuCreate) -> models.Danmaku:
        db_danmaku = models.Danmaku(**danmaku.model_dump())
        db.add(db_danmaku)
        await db.commit()
        await db.refresh(db_danmaku)
        return db_danmaku

    async def create_gift(self, db: AsyncSession, gift: schemas.GiftCreate) -> models.Gift:
        db_gift = models.Gift(**gift.model_dump())
        db.add(db_gift)
        await db.commit()
        await db.refresh(db_gift)
        return db_gift

    async def create_super_chat(self, db: AsyncSession, sc: schemas.SuperChatCreate) -> models.SuperChat:
        db_sc = models.SuperChat(**sc.model_dump())
        db.add(db_sc)
        await db.commit()
        await db.refresh(db_sc)
        return db_sc

    async def create_user(self, db: AsyncSession, user: schemas.UserCreate) -> models.User:
        # Check if user exists
        result = await db.execute(select(models.User).filter(models.User.user_name == user.user_name))
        db_user = result.scalars().first()
        
        if db_user:
            # Update SESSDATA
            db_user.sessdata = user.sessdata
        else:
            # Create new user
            db_user = models.User(**user.model_dump())
            db.add(db_user)
            
        await db.commit()
        await db.refresh(db_user)
        return db_user

    async def get_user_by_name(self, db: AsyncSession, user_name: str) -> models.User | None:
        result = await db.execute(select(models.User).filter(models.User.user_name == user_name))
        return result.scalars().first()

    async def delete_user_by_name(self, db: AsyncSession, user_name: str) -> bool:
        """
        根据用户名删除用户

        Args:
            db (AsyncSession): 数据库会话
            user_name (str): 用户名称

        Returns:
            bool: 是否删除成功
        """
        result = await db.execute(select(models.User).filter(models.User.user_name == user_name))
        db_user = result.scalars().first()
        if db_user:
            await db.delete(db_user)
            await db.commit()
            return True
        return False

    async def create_or_update_room(self, db: AsyncSession, room: schemas.RoomCreate) -> models.Room:
        # 查找是否存在
        result = await db.execute(select(models.Room).filter(models.Room.room_id == room.room_id))
        db_room = result.scalars().first()
        
        if db_room:
            # 更新
            db_room.title = room.title
            db_room.host = room.host
        else:
            # 创建
            db_room = models.Room(**room.model_dump())
            db.add(db_room)
        
        await db.commit()
        await db.refresh(db_room)
        return db_room

# 实例化对象
crud_dao = CRUDDao()
