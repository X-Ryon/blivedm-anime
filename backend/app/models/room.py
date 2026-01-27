from backend.database.db import Base
from backend.utils.timezone import timezone
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class Room(Base):
    """
    直播间模型
    """
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_id: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(64), nullable=True)
    host: Mapped[str] = mapped_column(String(64), nullable=True)
    create_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=timezone.now)
