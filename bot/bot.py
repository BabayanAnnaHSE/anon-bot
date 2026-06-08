# Для запуска асинхронного кода
import asyncio

# Для запросов к backend API
import requests

# Для чтения переменных окружения
import os

# Основные классы aiogram
from aiogram import Bot, Dispatcher, F

# Для хранения состояния диалога
from aiogram.fsm.context import FSMContext

# Кнопки клавиатуры
from aiogram.types import Message

# Простое хранение FSM в памяти
from aiogram.fsm.storage.memory import MemoryStorage

# Загрузка .env
from dotenv import load_dotenv

# Наши состояния
from states import Form

# Клавиатуры
from keyboards import chats_keyboard, confirm_keyboard, m_menu_keyboard, time_keyboard

from datetime import datetime

load_dotenv() #загружаем переменные из .env
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token = TOKEN) # создаем объект бота
dp = Dispatcher(storage=MemoryStorage())
API = "http://127.0.0.1:8000" # Адрес API - локальный сервер на собственном компе

# Регистрация группы
@dp.message(F.text== "/register")
async def register_chat(message: Message):
    # проверка, что чат - не личка, а группа
    if message.chat.type != "private": 
        # отправляем данные группы в бэк
        requests.post(f"{API}/chats", params={"chat_id": message.chat.id, "title": message.chat.title})
        await message.answer("Чат сохранён ✅")
    else:
        await message.answer("Эту команду можно использовать только для групп")

# Возможность отмены на любом этапе
@dp.message(F.text == "/cancel")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Текущее действие отменено", reply_markup=m_menu_keyboard())

# Начало работы в лс
@dp.message(F.text== "/start")
async def start(message: Message, state: FSMContext):
    # получам список чатов пользователя
    chats = requests.get(f"{API}/chats").json()
    if not chats:
        await message.answer("Нет зарегистрированных групп")
        return
    await message.answer("Выберите чат:", reply_markup=chats_keyboard(chats))
    await state.set_state(Form.choosing_chat) # переход на следующий этап

# Отправка нового сообщения после завершения операций с прошлым
@dp.message(F.text== "Создать новое сообщение")
async def new_message(message: Message, state: FSMContext):
    # очистка состояния
    await state.clear()
    chats = requests.get(f"{API}/chats").json()
    await message.answer("Выберите чат:", reply_markup=chats_keyboard(chats))
    await state.set_state(Form.choosing_chat) # переход на следующий этап

# после выбора чата пользователем
@dp.message(Form.choosing_chat)
async def choose_chat(message: Message, state: FSMContext):
    # сохраняем выбранный чат
    await state.update_data(chat_title=message.text)
    await message.answer("Напишите своё сообщение для анонимной отправки:")
    await state.set_state(Form.typing_text)

# после отправки текста пользователем
@dp.message(Form.typing_text)
async def enter_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer(
        "Хотите прикрепить файл?\n\n"
        "Отправьте вложение или напишите 'нет'"
        )
    await state.set_state(Form.choosing_media) 

# обработка медиа
@dp.message(Form.choosing_media)
async def media_handler(message: Message, state: FSMContext):
    # если пользователь ответил "нет"
    if message.text and message.text.lower() == "нет":
        await state.update_data(media_type=None, media_id=None)
        await message.answer("Когда отправить сообщение", reply_markup=time_keyboard())
        await state.set_state(Form.choosing_time)
        return
    
    # если пользователь прислал фото
    if message.photo:
        file_id = message.photo[-1].file_id
        await state.update_data(media_type="photo", media_id=file_id)

    # если пользователь прислал видео
    elif message.video:
        await state.update_data(media_type="video", media_id=message.video.file_id)

    # если пользователь прислал доуцмент
    elif message.document:
        await state.update_data(media_type="document", media_id=message.document.file_id)

    # если что-то непонятное (ну вдруг)))
    else:
        await message.answer("Отправьте фото, видео, документ или 'нет'")
        return
    
    await message.answer(
        "Файл сохранён!\n\n" 
        "Когда отправить сообщение", 
        reply_markup=time_keyboard()
        )
    
    await state.set_state(Form.choosing_time) 

# обработка выбора времени 
@dp.message(Form.choosing_time)
async def choose_time(message: Message, state: FSMContext):
    # если сейчас
    if message.text == "Сейчас":
        await state.update_data(send_time=None)
        # сохраняем
        # получаем все сохраненные данные
        data = await state.get_data()

        # Формируем итог перед отправкой
        summary = (
            f"Чат: {data['chat_title']}\n\n"
            f"Текст: \n{data['text']}\n\n"
            f"Время отправки - сейчас"
        )
        await message.answer(summary, reply_markup=confirm_keyboard())
        await state.set_state(Form.confirming)
    
    # если позже
    elif message.text == "Позже":
        await message.answer(
            "Введите дату и время\n\n"
            "Формат:\n"
            "01.01.2026 13:00"
        )
        await state.set_state(Form.entering_datetime)
        return

# получаем время отправки
@dp.message(Form.entering_datetime)
async def enter_datetime(message: Message, state: FSMContext):
    #проверяем формат
    try:
        dt = datetime.strptime(message.text, "%d.%m.%Y %H:%M")

    except ValueError:
        await message.answer(
            "Неверный формат\n"
            "Пример:\n"
            "01.01.2026 13:00"
        )
        return
    
    # сохраняем
    await state.update_data(send_time=dt.isoformat())
    
    # получаем все сохраненные данные
    data = await state.get_data()

    # Формируем итог перед отправкой
    summary = (
        f"Чат: {data['chat_title']}\n\n"
        f"Текст: \n{data['text']}\n\n"
        f"Время отправки: {message.text}"
    )
    await message.answer(summary, reply_markup=confirm_keyboard())
    await state.set_state(Form.confirming)

# получаем ответ-подтверждение
@dp.message(Form.confirming)
async def send(message: Message, state: FSMContext):
    if message.text == "Отправить ✅":
        # получаем данные
        data = await state.get_data()

        # берем чат-id по названию
        chat = requests.get(f"{API}/chat_by_title", params={"title": data["chat_title"]}).json()
        
        #проверка существования чата
        if not chat:
            await message.answer("Чат не найден!")
            await state.clear()
            return


        # ОТЛОЖЕННАЯ ОТПРАВКА
        if data.get("send_time"):
            requests.post(
                f"{API}/requests",
                params={
                    "user_id": message.from_user.id,
                    "chat_id": chat["chat_id"],
                    "text": data["text"], 
                    "media": data.get("media_id", ""),
                    "media_type": data.get("media_type", ""),
                    "send_time": data["send_time"],
                    "status": "pending"
                }
            )
            await message.answer("Сообщение поставлено в очередь ✅", reply_markup=m_menu_keyboard())



        # МГНОВЕННАЯ ОТПРАВКА
        else:
            # если во вложениях есть фото
            if data.get("media_type")=="photo":
                await bot.send_photo(
                    chat_id=chat["chat_id"],
                    photo=data["media_id"], 
                    caption=data["text"]
                    )

            # если во вложениях есть видео
            elif data.get("media_type")=="video":
                await bot.send_video(
                    chat_id=chat["chat_id"],
                    video=data["media_id"], 
                    caption=data["text"]
                    )
            # если во вложениях есть документ
            elif data.get("media_type")=="document":
                await bot.send_document(
                    chat_id=chat["chat_id"],
                    document=data["media_id"], 
                    caption=data["text"]
                    )

            # если вложений нет
            else:
                await bot.send_message(chat["chat_id"], data["text"])
    
            # сохраняем историю
            requests.post(f"{API}/requests", params={
                "user_id": message.from_user.id,
                "chat_id": chat["chat_id"],
                "text": data["text"],
                "media": data.get("media_id", ""),
                "media_type": data.get("media_type", ""),
                "status": "sent"
                })
            
            await message.answer("Сообщение отправлено анонимно ✅", reply_markup = m_menu_keyboard())

    else: 
        await message.answer("Отменено ❌", reply_markup=m_menu_keyboard())

    # очищаем состояние
    await state.clear()

# главная функция запуска
async def main():
    # запускаем long polling
    await dp.start_polling(bot)

# старт программы
if __name__ == "__main__": 
    asyncio.run(main())