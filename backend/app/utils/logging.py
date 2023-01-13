import logging
from logging import Logger


def init_logging(loggers: list[str] = [], log_level: str = "INFO"):
    _loggers = [logging.getLogger(name) for name in loggers]
    _loggers.append(logging.getLogger())
    for logger in _loggers:
        make_logger(logger, log_level)


def make_logger(logger: logging.Logger, log_level: str = "INFO"):
    # prevent double logs; loggers are nested
    logger.propagate = False
    level = logging.getLevelName(log_level.upper())
    logger.setLevel(level)


# convenience
def get_app_logger(log_level: str = "INFO") -> Logger:
    init_logging(
        loggers=["uvicorn.access", "uvicorn.error", "uvicorn"],
        log_level=log_level,
    )
    return logging.getLogger("uvicorn")
