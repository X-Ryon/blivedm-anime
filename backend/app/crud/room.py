from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.models import room as room_model
from backend.app.schemas import room as room_schema

class CRUDRoom:
    async def create_or_update_room(self, db: AsyncSession, room: room_schema.RoomCreate) -> room_model.Room:
        # 查找是否存在
        result = await db.execute(select(room_model.Room).filter(room_model.Room.room_id == room.room_id))
        db_room = result.scalars().first()
        
        if db_room:
            # 更新
            db_room.title = room.title
            db_room.host = room.host
        else:
            # 创建
            db_room = room_model.Room(**room.model_dump())
            db.add(db_room)
        
        await db.flush()
        return db_room

crud_room = CRUDRoom()
