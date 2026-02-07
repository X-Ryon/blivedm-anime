from pydantic import BaseModel, Field
from typing import Optional

class RoomCreate(BaseModel):
    room_id: str = Field(..., max_length=64, description="房间号")
    title: Optional[str] = Field(default=None, max_length=255, description="直播间标题")
    host: Optional[str] = Field(default=None, max_length=64, description="主播名称")

class ListenRequest(BaseModel):
    """
    监听请求体
    """
    room_id: str = Field(..., max_length=64, description="房间号")
    sessdata: Optional[str] = Field(default=None, description="直接传入的 Sessdata (Cookie)")

class StartListenResponse(BaseModel):
    message: str = Field(..., description="监听成功消息")
    stream_url: str = Field(..., description="直播流URL")
    protocol: str = Field(..., description="直播流协议")
    room_title: Optional[str] = Field(default=None, description="直播间标题")
    anchor_name: Optional[str] = Field(default=None, description="主播名称")

class StopListenResponse(BaseModel):
    message: str = Field(..., description="取消监听成功消息")
