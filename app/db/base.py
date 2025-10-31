from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
from app.core.logger import logger
from app.core.config import settings

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print("DATABASE_URL =", DATABASE_URL) 

logger.info("Подключение к базе данных...")
engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)

logger.info("Создание SessionLocal...")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logger.info("Создание базовой модели...")
Base = declarative_base()

def init_db():
    logger.info("Создание таблиц...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Таблицы успешно созданы.")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")

