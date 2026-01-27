from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from backend.app.models import danmaku as dm_model
from backend.app.schemas import danmaku as dm_schema

class CRUDDanmaku:
    async def create_danmaku(self, db: AsyncSession, danmaku: dm_schema.DanmakuCreate) -> dm_model.Danmaku:
        db_danmaku = dm_model.Danmaku(**danmaku.model_dump())
        db.add(db_danmaku)
        await db.flush()
        return db_danmaku

    async def create_gift(self, db: AsyncSession, gift: dm_schema.GiftCreate) -> dm_model.Gift:
        db_gift = dm_model.Gift(**gift.model_dump())
        db.add(db_gift)
        await db.flush()
        return db_gift

    async def create_super_chat(self, db: AsyncSession, sc: dm_schema.SuperChatCreate) -> dm_model.SuperChat:
        db_sc = dm_model.SuperChat(**sc.model_dump())
        db.add(db_sc)
        await db.flush()
        return db_sc

    async def replace_gift_info_room(self, db: AsyncSession, gifts: list[dm_schema.GiftInfoRoomCreate]) -> list[dm_model.GiftInfoRoom]:
        await db.execute(delete(dm_model.GiftInfoRoom))
        db_gifts = [dm_model.GiftInfoRoom(**gift.model_dump()) for gift in gifts]
        db.add_all(db_gifts)
        await db.flush()
        return db_gifts

crud_danmaku = CRUDDanmaku()
