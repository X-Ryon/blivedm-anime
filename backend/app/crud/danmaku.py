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

    async def get_all_gift_info_room(self, db: AsyncSession) -> list[dm_model.GiftInfoRoom]:
        from sqlalchemy import select
        result = await db.execute(select(dm_model.GiftInfoRoom))
        return result.scalars().all()

    async def get_recent_danmaku(self, db: AsyncSession, room_id: str, limit: int = 100) -> list[dm_model.Danmaku]:
        from sqlalchemy import select
        # Use simple string ordering if created_at is not available, or assume id is auto-incrementing
        stmt = select(dm_model.Danmaku).where(dm_model.Danmaku.room_id == room_id).order_by(dm_model.Danmaku.id.desc()).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()[::-1] # Reverse to chronological order

    async def get_recent_gifts(self, db: AsyncSession, room_id: str, limit: int = 100) -> list[dm_model.Gift]:
        from sqlalchemy import select
        stmt = select(dm_model.Gift).where(dm_model.Gift.room_id == room_id).order_by(dm_model.Gift.id.desc()).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()[::-1]

    async def get_recent_super_chats(self, db: AsyncSession, room_id: str, limit: int = 100) -> list[dm_model.SuperChat]:
        from sqlalchemy import select
        stmt = select(dm_model.SuperChat).where(dm_model.SuperChat.room_id == room_id).order_by(dm_model.SuperChat.id.desc()).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()[::-1]

crud_danmaku = CRUDDanmaku()
