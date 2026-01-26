import logging
import sys
from loguru import logger
from backend.core.conf import settings

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def setup_logging():
    # 移除所有现有的 handler
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(settings.LOG_STD_LEVEL)

    # 移除 loguru 默认 handler
    logger.remove()
    
    # 设置默认的 request_id 防止 KeyError
    logger.configure(extra={"request_id": "-"})

    # 添加控制台输出
    logger.add(
        sys.stderr,
        format=settings.LOG_FORMAT,
        level=settings.LOG_STD_LEVEL,
        enqueue=True
    )

    # 添加文件输出 (Access Log)
    logger.add(
        "logs/access.log",
        rotation="10 MB",
        retention="10 days",
        format=settings.LOG_FORMAT,
        level=settings.LOG_FILE_ACCESS_LEVEL,
        enqueue=True,
        filter=lambda record: record["level"].name == "INFO"
    )

    # 添加文件输出 (Error Log)
    logger.add(
        "logs/error.log",
        rotation="10 MB",
        retention="10 days",
        format=settings.LOG_FORMAT,
        level=settings.LOG_FILE_ERROR_LEVEL,
        enqueue=True
    )

    # 配置 uvicorn 和 fastapi 的日志使用 loguru
    # 这一步将 uvicorn 的日志重定向到 loguru
    logging.getLogger("uvicorn").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    
    # 也可以遍历所有 logger 进行重置
    # for name in logging.root.manager.loggerDict.keys():
    #     logging.getLogger(name).handlers = []
    #     logging.getLogger(name).propagate = True
