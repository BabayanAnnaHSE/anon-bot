# Импортируем FastAPI
from fastapi import FastAPI

# Импортируем подключение к БД
from backend.database import Base, engine, SessionLocal

# Импортируем модели таблиц
from backend.models import Chat, Request

# Для работы с датой и временем
from datetime import datetime

app = FastAPI() # создаём приложение FastAPI

# Автоматически при запуске создаём таблички 
Base.metadata.create_all(bind=engine)

# Проверочный маршрут
@app.get("/")
def root():
    return{"message": "API работает"} # при отрытии сайта увидим это сообщение
    

# Добавление нового чата
@app.post("/chats")
def add_chat(chat_id: int, title: str):
    db = SessionLocal() # Открываем сессию БД
    chat = Chat(chat_id=chat_id, title=title) # Создаём новую зхапись
    db.add(chat) # добавляем запись в БД
    db.commit() # сохраняем изменения
    return{"ok": True}

# Получение списка всех чатов
@app.get("/chats")
def get_chats():
    db = SessionLocal()
    return db.query(Chat).all() # возрвращаем все записи

# Получение чата по названию
@app.get("/chat_by_title")
def get_chat(title: str):
    db = SessionLocal()
    return db.query(Chat).filter(Chat.title == title).first() # Возвращаем первую запись из таблицы с совпадающим названием

# Сохранение истории запроса
@app.post("/requests")
def save_request(user_id: int, chat_id: int, text: str, media: str = "", media_type: str = "", send_time: str = "", status: str = "pending"):
    db = SessionLocal()
    # Создаем запись
    req = Request(user_id=user_id, chat_id = chat_id, text=text, media=media, media_type=media_type,
        # Если время передано - меняем тип со строки на дату
        send_time=datetime.fromisoformat(send_time) if send_time else None,
        status = status
    )
    db.add(req)
    db.commit()
    return{"ok": True}

# Запросы со статусом pending - ожидающие отправки
@app.get("/pending_requests")
def get_pending_requests():
    db = SessionLocal()
    return (db.query(Request).filter(Request.status== "pending").all())

# помечать отложенные сообщения как отправленные 
@app.post("/mark_sent")
def mark_sent(request_id: int):
    db = SessionLocal()
    req = (db.query(Request).filter(Request.id== request_id).first())

    if req:
        req.status = "sent"
        db.commit()

    return {"ok": True}