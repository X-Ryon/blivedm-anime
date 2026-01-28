# -*- coding: utf-8 -*-
from enum import Enum

class ResponseCode(int, Enum):
    """
    统一响应状态码
    """
    SUCCESS = 200
    FAIL = -1
    
    # 客户端错误 400~499
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    
    # 服务端错误 500~599
    INTERNAL_SERVER_ERROR = 500
    
    # 业务错误 (根据需要扩展)
    DB_ERROR = 5001
    PARAM_ERROR = 4001
    AUTH_ERROR = 4010
