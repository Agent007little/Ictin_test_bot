from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Клавиатура перехода в чат с пользователем при отправлении претензии
def to_user_chat_kb(user_name):
    kb_builder = InlineKeyboardBuilder()
    # Добавляем в билдер ряд с кнопками.
    kb_builder.row(InlineKeyboardButton(text=f"Чат с пользователем {user_name}", callback_data="User_chat"), width=1)
    return kb_builder.as_markup()
