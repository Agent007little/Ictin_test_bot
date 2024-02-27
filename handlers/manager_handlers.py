from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from States.States import FSMManager
from database.database import get_claim_list, get_user_chat_id
from lexicon.lexicon import LEXICON_MANAGER_COMMANDS

router = Router()
dict_chats = {}


# Команда help

@router.message(Command(commands="help"), StateFilter(FSMManager.default_manager))
async def process_start_command(message: Message):
    await message.answer(LEXICON_MANAGER_COMMANDS[message.text])


# Переход к переписке с пользователем

@router.message(Command(commands="chat_with_user"), StateFilter(FSMManager.default_manager))
async def chat_with_user(message: Message, state: FSMContext):
    await message.answer(text='Введите имя пользователя')
    await state.set_state(FSMManager.wait_user_name)


@router.message(StateFilter(FSMManager.wait_user_name))
async def go_to_chat(message: Message, state: FSMContext):
    user_name = message.text
    user_chat_id = await get_user_chat_id(user_name)
    dict_chats[message.from_user.id] = user_chat_id
    await state.set_state(FSMManager.chat_with_user)
    await message.answer(text=f"Ваши сообщения будут пересылаться пользователю {user_name}")


# Команда выхода из чата с пользователем
@router.message(Command(commands="leave"), StateFilter(FSMManager.chat_with_user))
async def leave_chat(message: Message, state: FSMContext):
    del dict_chats[message.from_user.id]
    await state.set_state(FSMManager.default_manager)
    await message.answer(text="Вы вышли из чата с пользователем")


# Пересылка сообщения указанному пользователю
@router.message(StateFilter(FSMManager.chat_with_user))
async def go_to_chat(message: Message, bot: Bot):
    await bot.send_message(chat_id=dict_chats[message.from_user.id], text=message.text)


# Список пользователей которые создали претензию

@router.message(Command(commands="claim_list"), StateFilter(FSMManager.default_manager))
async def show_claim_list(message: Message):
    user_l = await get_claim_list()
    str_user_l = ''
    for i in user_l:
        for j in i:
            str_user_l += j + "\n"
    await message.answer(text=str_user_l)
