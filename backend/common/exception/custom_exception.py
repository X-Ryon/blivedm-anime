# -*- coding: utf-8 -*-
from typing import Optional, Any
from backend.common.exception.code import ResponseCode

class BaseExceptionMixin(Exception):
    """
    基础异常类
    """
    def __init__(
        self, 
        code: int = ResponseCode.FAIL, 
        message: str = "Internal Server Error", 
        data: Any = None
    ):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(self.message)

class NotFoundException(BaseExceptionMixin):
    def __init__(self, message: str = "Resource Not Found", data: Any = None):
        super().__init__(code=ResponseCode.NOT_FOUND, message=message, data=data)

class BadRequestException(BaseExceptionMixin):
    def __init__(self, message: str = "Bad Request", data: Any = None):
        super().__init__(code=ResponseCode.BAD_REQUEST, message=message, data=data)

class UnauthorizedException(BaseExceptionMixin):
    def __init__(self, message: str = "Unauthorized", data: Any = None):
        super().__init__(code=ResponseCode.UNAUTHORIZED, message=message, data=data)

class ForbiddenException(BaseExceptionMixin):
    def __init__(self, message: str = "Forbidden", data: Any = None):
        super().__init__(code=ResponseCode.FORBIDDEN, message=message, data=data)

class InternalServerException(BaseExceptionMixin):
    def __init__(self, message: str = "Internal Server Error", data: Any = None):
        super().__init__(code=ResponseCode.INTERNAL_SERVER_ERROR, message=message, data=data)
