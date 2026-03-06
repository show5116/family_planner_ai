import logging
import sys
from loguru import logger
from app.core.config import settings

class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documention.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """
    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            if frame.f_back:
                frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """
    Configure loguru to intercept standard logging formats and pipe to loguru.
    Sets up console and file logging.
    """
    # Remove all default handlers
    logger.remove()

    # Define common format including request_id
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<magenta>{extra[request_id]}</magenta> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # Set default extra attributes
    logger.configure(extra={"request_id": "-"})

    # Add console handler
    logger.add(
        sys.stdout,
        format=log_format,
        level="INFO",
        colorize=True,
    )

    # Add file handler for rotating logs
    logger.add(
        "logs/app.log",
        format=log_format,
        level="INFO",
        rotation="10 MB",      # Rotate every 10 MB
        retention="10 days",   # Keep logs for 10 days
        compression="zip",     # Compress rotated logs
    )

    # Intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logging.INFO)

    # Intercept specific loggers (e.g., uvicorn, fastapi)
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = [InterceptHandler()]
        logging.getLogger(name).propagate = False
        
    logger.info("Logging is configured via Loguru!")
