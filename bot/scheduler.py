# импорт библиотек
# запуск асинхронного кода
import asyncio
# для получения токена
import os
# для запросов к api
import requests
# lkz
from datetime import datetime
# tg-bot api через aiogram
from aiogram import Bot
# загруза переменных из .env
from dotenv import load_dotenv

load_dotenv() # загружаем .env
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token = TOKEN) # создаем объект бота
API = "http://127.0.0.1:8000" # Адрес API - локальный сервер на собственном компе

# ПРОВЕРКА отложенных сообщений
async def process_queue():
    # создаём бесконечный цикл, проверяющий БД каждую минуту (тк минимальное отложенное время отправки в тг - 1 минута)
    while True:
        try:
            pending = requests.get(f"{API}/pending_requests").json() # списрок неотправленных сообщений
            now = datetime.now() # текущее время на компе

            # проработка неотправленных заявок - сообзщений
            for req in pending:
                send_time = req.get("send_time")
                if not send_time: # если время отправки не указано (т.е. пользователь хотел отправить сразу, - такую заявку прпускаем)
                    continue
                
                send_time = datetime.fromisoformat(send_time) # преобразовываем строку в datetime

                # проверяем время отправки
                if send_time <= now:
                    media = req.get("media") # получаем вложение
                    media_type = req.get("media_type") # получаем тип вложения

                    #если фото
                    if media_type == "photo":
                        await bot.send_photo(chat_id=req["chat_id"], photo=media, caption=req["text"])
                    
                    #если видео
                    elif media_type == "video":
                        await bot.send_video(chat_id=req["chat_id"], video=media, caption=req["text"])
                    
                    #если документ
                    elif media_type == "document":
                        await bot.send_document(chat_id=req["chat_id"], document=media, caption=req["text"])
                    
                    #если просто текст
                    else:
                        await bot.send_message(chat_id=req["chat_id"], text=req["text"])
                    
                    # после отправки необходимо изменить статус сообщения
                    requests.post(f"{API}/mark_sent", params={"request_id": req["id"]})

                    print(f"Сообщение #{req['id']} отправлено") # вывод итога отправки в консоль
        
        except Exception as e:
            print("Ошибка schedular:", e) #вывод ошибки планировщика отправки в консоль
        
        await asyncio.sleep(60) # уходим в ожидание на 60 секунд, после чего повторяем проверку


# точка входа в программу
async def main():
    await  process_queue() # Запуск цикла проверки

if __name__== "__main__": # если файл запущен напрямую 
    asyncio.run(main())

