from pydantic import BaseModel, Field
from typing import Optional

# ----------------- 响应模型 (推送到客户端的数据格式) -----------------

class DanmakuResponse(BaseModel):
    """
    弹幕/SC 推送数据格式
    """
    user_name: str = Field(..., max_length=64, description="用户名称")
    level: int = Field(default=0, description="粉丝牌等级")
    privilege_name: str = Field(..., max_length=64, description="身份名称：普通、舰长、提督、总督")
    dm_text: str = Field(..., max_length=255, description="弹幕内容")
    identity: str = Field(..., max_length=64, description="直播间身份：主播、房管、普通")
    price: float = Field(default=0.0, description="SC金额，普通弹幕为0")
    uid: Optional[str] = Field(default=None, description="用户UID")
    face_img: Optional[str] = Field(default=None, description="用户头像")
    msg_type: str = Field(default="danmaku", description="消息类型: danmaku, super_chat")
    timestamp: float = Field(default=0.0, description="创建时间戳")

class GiftResponse(BaseModel):
    """
    礼物/上舰 推送数据格式
    """
    user_name: str = Field(..., max_length=64, description="用户名称")
    level: int = Field(default=0, description="粉丝牌等级")
    privilege_name: str = Field(..., max_length=64, description="身份名称：普通、舰长、提督、总督")
    gift_type: str = Field(..., max_length=255, description="礼物名称或上舰类型")
    num: int = Field(default=0, description="礼物数量")
    price: float = Field(default=0.0, description="礼物价值(元)")
    uid: Optional[str] = Field(default=None, description="用户UID")
    face_img: Optional[str] = Field(default=None, description="用户头像")
    msg_type: str = Field(default="gift", description="消息类型: gift, guard")
    timestamp: float = Field(default=0.0, description="创建时间戳")

class GiftInfoRoomResponse(BaseModel):
    id: int = Field(..., description="礼物ID")
    name: str = Field(..., max_length=64, description="礼物名称")
    price: float = Field(..., description="礼物价格")
    coin_type: str = Field(..., max_length=64, description="货币类型")
    img: str = Field(..., max_length=255, description="礼物图片")

    class Config:
        from_attributes = True

class FetchGiftInfoResponse(BaseModel):
    message: str = Field(..., description="操作消息")
    count: int = Field(..., description="礼物数量")
    gifts: list[GiftInfoRoomResponse] = Field(default_factory=list, description="礼物列表")

# ----------------- 数据库交互模型 (DTO) -----------------

class DanmakuCreate(BaseModel):
    room_id: str = Field(..., max_length=64, description="房间号")
    user_name: str = Field(..., max_length=64, description="用户名称")
    uid: Optional[str] = Field(default=None, max_length=64, description="用户UID")
    level: int = Field(default=0, description="粉丝牌等级")
    privilege_name: str = Field(default="普通", max_length=64, description="身份名称")
    identity: str = Field(default="普通", max_length=64, description="直播间身份")
    face_img: Optional[str] = Field(default=None, max_length=255, description="用户头像URL")
    dm_text: str = Field(..., max_length=255, description="弹幕内容")

class SuperChatCreate(BaseModel):
    room_id: str = Field(..., max_length=64, description="房间号")
    user_name: str = Field(..., max_length=64, description="用户名称")
    uid: Optional[str] = Field(default=None, max_length=64, description="用户UID")
    level: int = Field(default=0, description="粉丝牌等级")
    privilege_name: str = Field(default="普通", max_length=64, description="身份名称")
    identity: str = Field(default="普通", max_length=64, description="直播间身份")
    sc_text: str = Field(..., max_length=255, description="SC内容")
    price: float = Field(default=0.0, description="SC金额")

class GiftCreate(BaseModel):
    room_id: str = Field(..., max_length=64, description="房间号")
    user_name: str = Field(..., max_length=64, description="用户名称")
    uid: Optional[str] = Field(default=None, max_length=64, description="用户UID")
    level: int = Field(default=0, description="粉丝牌等级")
    privilege_name: str = Field(default="普通", max_length=64, description="身份名称")
    identity: str = Field(default="普通", max_length=64, description="直播间身份")
    face_img: Optional[str] = Field(default=None, max_length=255, description="用户头像URL")
    gift_name: str = Field(..., max_length=255, description="礼物名称")
    gift_num: int = Field(default=1, description="礼物数量")
    price: float = Field(default=0.0, description="礼物总价值")

class GiftInfoRoomCreate(BaseModel):
    name: str = Field(..., max_length=64, description="礼物名称")
    price: float = Field(..., description="礼物价格")
    coin_type: str = Field(..., max_length=64, description="货币类型")
    img: str = Field(..., max_length=255, description="礼物图片")

class FetchGiftInfoRequest(BaseModel):
    room_id: str = Field(..., max_length=64, description="房间号")
    user_name: Optional[str] = Field(default=None, max_length=64, description="用户名称，用于查找数据库中的 Cookie")
