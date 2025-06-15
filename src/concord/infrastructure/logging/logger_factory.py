import logging
from logging import FileHandler, Formatter, Logger, getLogger
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

BACKGROUND_LOG_LEVEL = logging.INFO
BACKGROUND_LOG_FORMATTER = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEBUG_LOG_FORMATTER = (
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s "
    "[%(filename)s:%(lineno)d] "
    "(module: %(module)s, func: %(funcName)s)"
)
DEFAULT_LOG_DIR = Path(__file__).parent.parent.parent.parent / "logs"


def get_background_log(name: str, log_dir: Path) -> Logger:
    logger = getLogger(name)
    logger.setLevel(BACKGROUND_LOG_LEVEL)
    handler = TimedRotatingFileHandler(
        (log_dir / f"{name}.background.log").as_posix(),
        when="midnight",
        interval=7,
        backupCount=4,
        encoding="utf-8",
    )
    formatter = Formatter(BACKGROUND_LOG_FORMATTER)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def my_logger(name: str, level: int, log_dir: Path) -> Logger:
    logger = getLogger(name)
    logger.setLevel(level)
    handler = FileHandler((log_dir / f"{name}.log").as_posix(), encoding="utf-8")
    formatter = Formatter(DEBUG_LOG_FORMATTER)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_logger(
    name: str,
    level: int = logging.INFO,
    log_dir: Path = DEFAULT_LOG_DIR,
) -> logging.Logger:
    logger = get_background_log(name, log_dir)
    if level < BACKGROUND_LOG_LEVEL:
        logger = my_logger(name, level, log_dir)
    return logger
