# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from backend.common.resp import Resp
from backend.common.exception.code import ResponseCode
from backend.common.exception.custom_exception import BaseExceptionMixin

def register_exception_handler(app: FastAPI):
    """
    注册全局异常处理器
    """
    
    # 处理自定义异常
    @app.exception_handler(BaseExceptionMixin)
    async def custom_exception_handler(request: Request, exc: BaseExceptionMixin):
        return JSONResponse(
            status_code=200, # 统一返回 200，具体状态码在 body 中体现，或者根据 exc.code 映射
            content=Resp.fail(code=exc.code, message=exc.message, data=exc.data).dict()
        )

    # 处理 FastAPI/Starlette 的 HTTPException
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=Resp.fail(code=exc.status_code, message=exc.detail).dict()
        )

    # 处理参数校验异常
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # 提取详细的错误信息
        details = exc.errors()
        message = "; ".join([f"{e['loc'][-1]}: {e['msg']}" for e in details])
        return JSONResponse(
            status_code=422,
            content=Resp.fail(code=ResponseCode.PARAM_ERROR, message=f"Validation Error: {message}", data=details).dict()
        )

    # 处理所有未捕获的异常
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        import traceback
        traceback.print_exc() # 打印堆栈信息以便调试
        return JSONResponse(
            status_code=500,
            content=Resp.fail(code=ResponseCode.INTERNAL_SERVER_ERROR, message=f"Internal Server Error: {str(exc)}").dict()
        )
