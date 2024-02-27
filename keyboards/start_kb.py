from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Создание первой клавиатуры выбора пользователя
def create_start_kb():
    kb_builder = InlineKeyboardBuilder()
    # Добавляем в билдер ряд с кнопками.
    kb_builder.row(InlineKeyboardButton(text="Пользователь", callback_data="User"),
                   InlineKeyboardButton(text="Менеджер", callback_data="Manager"),
                   width=2)
    return kb_builder.as_markup()
