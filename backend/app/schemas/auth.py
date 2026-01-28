from pydantic import BaseModel, Field
from typing import Optional


class UserCreate(BaseModel):
    uid: Optional[str] = Field(None, max_length=64, description="用户UID")
    sessdata: str = Field(..., max_length=512, description="B站 SESSDATA")

class UserInfo(BaseModel):
    """
    用户响应模型
    """
    uid: Optional[str] = Field(None, description="用户UID")
    user_name: str = Field(..., max_length=64, description="用户名称")
    face_img: Optional[str] = Field(None, description="用户头像")
    sessdata: str = Field(..., max_length=512, description="Sessdata Cookie值")

    class Config:
        from_attributes = True

class DeleteUserResponse(BaseModel):
    success: bool = Field(..., description="是否删除成功")
    message: str = Field(..., description="操作消息")
