# Импортируем инструменты FSM (машина состояний)
from aiogram.fsm.state import StatesGroup, State

# Этапы диалога с юзером  
class Form(StatesGroup):
    choosing_chat = State() # Выбор чата
    typing_text = State() # Ввод текста
    choosing_media = State() # Выбор вложений
    choosing_time = State() # Выбор времени отправки
    entering_datetime = State() # Ввод времени отправк
    confirming = State() # Подтверждение в конце