from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from States.States import FSMUser, FSMManager
from database.database import save_user, save_manager, save_user_to_manager
from keyboards.start_kb import create_start_kb
from lexicon.lexicon import LEXICON_MAIN_COMMANDS

router = Router()
dict_users = {}


# Этот хэндлер будет срабатывать на команду /start вне состояний
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    dict_users[message.from_user.id] = [message.from_user.id, message.chat.id, message.from_user.username]
    await message.answer(LEXICON_MAIN_COMMANDS[message.text], reply_markup=create_start_kb())


@router.callback_query(F.data.in_({"User", "Manager"}))
async def process_choice_lang(callback: CallbackQuery, state: FSMContext):
    if callback.data == "User":
        # Переводим в выбранное состояние
        await state.set_state(FSMUser.default_user)
        # Сохранить пользователя в БД
        await save_user(telegram_id=dict_users[callback.from_user.id][0],
                        chat_id=dict_users[callback.from_user.id][1],
                        user_name=dict_users[callback.from_user.id][2])
        # Привязать нового пользователя к свободному менеджеру
        await save_user_to_manager(callback.from_user.id)
        # ответ новому пользователю
        await callback.message.answer(text=LEXICON_MAIN_COMMANDS["User"])
    else:
        # Переводим в выбранное состояние
        await state.set_state(FSMManager.default_manager)
        # Сохранить менеджера в БД
        await save_manager(telegram_id=dict_users[callback.from_user.id][0],
                           chat_id=dict_users[callback.from_user.id][1])
        # Ответ новому менеджеру
        await callback.message.answer(text=LEXICON_MAIN_COMMANDS["Manager"])
    await callback.answer()
