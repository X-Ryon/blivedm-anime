from backend.database.db import Base
from backend.utils.timezone import timezone
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class User(Base):
    """
    用户数据模型
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_name: Mapped[str] = mapped_column(String(64))
    face_img: Mapped[str] = mapped_column(String(255), nullable=True)
    sessdata: Mapped[str] = mapped_column(String(512))
    create_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=timezone.now)
