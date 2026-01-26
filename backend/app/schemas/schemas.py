# -*- coding: utf-8 -*-
from pydantic import BaseModel
from typing import Optional

# ----------------- 请求模型 -----------------

class ListenRequest(BaseModel):
    """
    监听请求体
    """
    room_id: str  # 保持为字符串以兼容前端输入，后端可转 int
    sessdata: Optional[str] = None # 用于认证，可选

# ----------------- 响应模型 (推送到客户端的数据格式) -----------------

class DanmakuResponse(BaseModel):
    """
    弹幕/SC 推送数据格式
    """
    user_name: str
    level: int
    privilege_name: str  # 枚举: '普通', '舰长', '提督', '总督'
    dm_text: str
    identity: str   # 枚举: '主播', '房管', '普通'
    price: float   # SC 金额，非 SC 则为 0

class GiftResponse(BaseModel):
    """
    礼物/上舰 推送数据格式
    """
    user_name: str
    level: int
    privilege_name: str  # 枚举: '普通', '舰长', '提督', '总督'
    gift_type: str # 具体礼物名称或 '舰长', '提督', '总督'
    price: float   # 礼物价值

# ----------------- 数据库交互模型 (DTO) -----------------

class DanmakuCreate(BaseModel):
    room_id: int
    user_name: str
    uid: Optional[int]
    level: int
    privilege_name: str
    dm_text: str
    identity: str

class SuperChatCreate(BaseModel):
    room_id: int
    user_name: str
    uid: Optional[int]
    price: float
    message: str

class GiftCreate(BaseModel):
    room_id: int
    user_name: str
    uid: Optional[int]
    level: int
    privilege_name: str
    gift_name: str
    gift_num: int
    price: float
    currency: str
