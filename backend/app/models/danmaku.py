from backend.database.db import Base
from backend.utils.timezone import timezone
from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class Danmaku(Base):
    """
    弹幕数据模型
    """
    __tablename__ = "danmu"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_id: Mapped[str] = mapped_column(String(64), index=True)
    user_name: Mapped[str] = mapped_column(String(64))
    uid: Mapped[str] = mapped_column(String(64), nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=0)
    privilege_name: Mapped[str] = mapped_column(String(64), default="普通")
    identity: Mapped[str] = mapped_column(String(64), default="普通")
    face_img: Mapped[str] = mapped_column(String(255), nullable=True)
    dm_text: Mapped[str] = mapped_column(String(255))
    create_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=timezone.now)

class Gift(Base):
    """
    礼物/打赏数据模型
    """
    __tablename__ = "gift"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_id: Mapped[str] = mapped_column(String(64), index=True)
    user_name: Mapped[str] = mapped_column(String(64))
    uid: Mapped[str] = mapped_column(String(64), nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=0)
    privilege_name: Mapped[str] = mapped_column(String(64), default="普通")
    identity: Mapped[str] = mapped_column(String(64), default="普通")
    face_img: Mapped[str] = mapped_column(String(255), nullable=True)
    gift_name: Mapped[str] = mapped_column(String(255))
    gift_num: Mapped[int] = mapped_column(Integer, default=1)
    price: Mapped[float] = mapped_column(Float)
    create_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=timezone.now)

class SuperChat(Base):
    """
    醒目留言模型
    """
    __tablename__ = "superchat"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_id: Mapped[str] = mapped_column(String(64), index=True)
    user_name: Mapped[str] = mapped_column(String(64))
    uid: Mapped[str] = mapped_column(String(64), nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=0)
    privilege_name: Mapped[str] = mapped_column(String(64), default="普通")
    identity: Mapped[str] = mapped_column(String(64), default="普通")
    face_img: Mapped[str] = mapped_column(String(255), nullable=True)
    sc_text: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(Float)
    create_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=timezone.now)

class GiftInfoRoom(Base):
    """
    房间可赠送礼物信息模型
    """
    __tablename__ = "gift_info_room"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64))
    price: Mapped[float] = mapped_column(Float)
    coin_type: Mapped[str] = mapped_column(String(64))
    img: Mapped[str] = mapped_column(String(255))
