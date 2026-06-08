# Импортируем типы колонок
from sqlalchemy import Column, Integer, String, DateTime

# Импортируем Base из database.py
from backend.database import Base

# Создадим таблицу зарегистрированных чатов
# состав: id записи, telegram-id группы(уникальный в таблице, чтобы нельзя было зарегистрировать одну группу дважды), наименование группы
class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, unique=True)
    title = Column(String)

# Создадим таблицу истории анонимных запросов
# состав: id записи, telegram-id пользователя, отправившего запрос, id чата, куда отправляется запрос, текст сообщения,
# путь к медиафайлу(если есть), время отправки(при необходимости отложенной отправки), статус
class Request(Base):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    chat_id = Column(Integer)
    text = Column(String)
    media = Column(String, default="")
    media_type = Column(String, default="")
    send_time = Column(DateTime)
    status = Column(String, default="pending") # 2 варианта: pending - ожидает отправки, sent - отправлено
