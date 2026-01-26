# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.db import Base
from backend.utils.timezone import timezone

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

class User(Base):
    """
    用户数据模型
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_name: Mapped[str] = mapped_column(String(64))
    sessdata: Mapped[str] = mapped_column(String(512))
    create_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=timezone.now)

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
    sc_text: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(Float)
    create_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=timezone.now)
