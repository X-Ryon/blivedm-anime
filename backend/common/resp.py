# -*- coding: utf-8 -*-
from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, ConfigDict
from backend.common.exception.code import ResponseCode

T = TypeVar("T")

class Resp(BaseModel, Generic[T]):
    """
    统一响应模型
    """
    code: int
    message: str
    data: Optional[T] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def success(cls, data: T = None, message: str = "Success") -> "Resp[T]":
        return cls(code=ResponseCode.SUCCESS, message=message, data=data)

    @classmethod
    def fail(cls, code: int = ResponseCode.FAIL, message: str = "Fail", data: Any = None) -> "Resp[Any]":
        return cls(code=code, message=message, data=data)
