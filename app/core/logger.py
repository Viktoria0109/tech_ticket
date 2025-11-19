import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = RotatingFileHandler("startup.log", maxBytes=10_000_000, backupCount=3)
    file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler.setFormatter(file_formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
