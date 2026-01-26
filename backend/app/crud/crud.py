# -*- coding: utf-8 -*-
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models import models
from backend.app.schemas import schemas

async def create_danmaku(db: AsyncSession, danmaku: schemas.DanmakuCreate):
    db_danmaku = models.Danmaku(**danmaku.dict())
    db.add(db_danmaku)
    await db.commit()
    await db.refresh(db_danmaku)
    return db_danmaku

async def create_gift(db: AsyncSession, gift: schemas.GiftCreate):
    db_gift = models.Gift(**gift.dict())
    db.add(db_gift)
    await db.commit()
    await db.refresh(db_gift)
    return db_gift

async def create_super_chat(db: AsyncSession, sc: schemas.SuperChatCreate):
    db_sc = models.SuperChat(**sc.dict())
    db.add(db_sc)
    await db.commit()
    await db.refresh(db_sc)
    return db_sc
