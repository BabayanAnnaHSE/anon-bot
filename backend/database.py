# Импортируем create_engine — он создаёт подключение к базе данных
from sqlalchemy import create_engine

# Импортируем инструменты для работы с ORM
# sessionmaker — создаёт сессии для запросов к БД
# declarative_base — базовый класс для моделей (таблиц)
from sqlalchemy.orm import sessionmaker, declarative_base

# Указываем путь к SQLite базе данных
# db.sqlite3 будет создан автоматически в корне проекта
DATABASE_URL = "sqlite:///./db.sqlite3"

# Создаём подключение к базе
# check_same_thread=False нужен для корректной работы SQLite с FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Создаём фабрику сессий, через неё будем открывать подключение к БД
# autocommit - изменения сохраняются только после commit()
# autoflush - SQLAlchemy не отправляет запрос на изменение в БД автоматические
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine)

# Базовый класс для всех моделей таблиц
Base = declarative_base()