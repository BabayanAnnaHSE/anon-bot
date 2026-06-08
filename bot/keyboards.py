# кнопочка в TG и просто клавиатура
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# создание клавиатуры со списком групп
def chats_keyboard(chats: list):
    keyboard = []
    for chat in chats:
        keyboard.append([KeyboardButton(text=chat["title"])])
    
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# клавиатура подтверждения отправки
def confirm_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить ✅")],
            [KeyboardButton(text="Отмена ❌")]
        ],
        resize_keyboard=True
    )

# клавиатура - возврат в главное меню после завершения операций
def m_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Создать новое сообщение")]],
        resize_keyboard=True
    )

#клавиатура выбора времени
def time_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Сейчас")], 
            [KeyboardButton(text="Позже")]
        ],
        resize_keyboard=True
    )