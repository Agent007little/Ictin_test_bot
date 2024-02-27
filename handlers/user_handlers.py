from aiogram import Router, Bot, types
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from States.States import FSMUser, FSMUserInvoice, FSMUserClaim
from database.database import save_invoice, update_user_invoices, manager_chat_id, save_claim
from lexicon.lexicon import LEXICON_USER_COMMANDS
from middleware.pdf_invoice.text_to_pdf import create_pdf_invoice

router = Router()
dict_invoice = {}
dict_claim = {}


# Команда help

@router.message(Command(commands="help"), StateFilter(FSMUser.default_user))
async def process_start_command(message: Message):
    await message.answer(LEXICON_USER_COMMANDS[message.text])


# Команда для вызова менеджера
@router.message(Command(commands="manager"), StateFilter(FSMUser.default_user))
async def call_manager(message: Message, bot: Bot):
    m_chat_id = await manager_chat_id(message.from_user.id)
    await bot.send_message(m_chat_id, text='Пользователь вызывает в чат')


# Создание накладной

@router.message(Command(commands="new_invoice"), StateFilter(FSMUser.default_user))
async def create_invoice(message: Message, state: FSMContext):
    dict_invoice[message.from_user.id] = []
    await message.answer(text="Введите описание груза")
    await state.set_state(FSMUserInvoice.weight)


# Вес груза
@router.message(StateFilter(FSMUserInvoice.weight))
async def create_invoice(message: Message, state: FSMContext):
    dict_invoice[message.from_user.id].append(message.text)
    await message.answer(text="Введите вес груза в килограммах")
    await state.set_state(FSMUserInvoice.cargo_dimensions)


# Габариты груза
@router.message(StateFilter(FSMUserInvoice.cargo_dimensions))
async def create_invoice(message: Message, state: FSMContext):
    dict_invoice[message.from_user.id].append(message.text)
    await message.answer(text="Введите габариты груза в формате ДхШхВ в метрах.")
    await state.set_state(FSMUserInvoice.shipping_address)


# Адрес отправки груза
@router.message(StateFilter(FSMUserInvoice.shipping_address))
async def create_invoice(message: Message, state: FSMContext):
    dict_invoice[message.from_user.id].append(message.text)
    await message.answer(text="Адрес отправки (Город и точный адрес).")
    await state.set_state(FSMUserInvoice.receiving_address)


# Адрес получения груза
@router.message(StateFilter(FSMUserInvoice.receiving_address))
async def create_invoice(message: Message, state: FSMContext):
    dict_invoice[message.from_user.id].append(message.text)
    await message.answer(text="Адрес получения (Город и точный адрес).")
    await state.set_state(FSMUserInvoice.payment_method)


# Метод оплаты
@router.message(StateFilter(FSMUserInvoice.payment_method))
async def create_invoice(message: Message, state: FSMContext):
    dict_invoice[message.from_user.id].append(message.text)
    await message.answer(text="Метод оплаты?")
    await state.set_state(FSMUserInvoice.finish_state)


# Создание накладной
@router.message(StateFilter(FSMUserInvoice.finish_state))
async def create_invoice(message: Message, state: FSMContext):
    dict_invoice[message.from_user.id].append(message.text)
    await state.set_state(FSMUser.default_user)
    # сохранение накладной в БД
    await save_invoice(description=dict_invoice[message.from_user.id][0],
                       weight=dict_invoice[message.from_user.id][1],
                       dimension=dict_invoice[message.from_user.id][2],
                       shipping_address=dict_invoice[message.from_user.id][3],
                       receiving_address=dict_invoice[message.from_user.id][4],
                       payment_method=dict_invoice[message.from_user.id][5])
    await update_user_invoices(message.from_user.id)
    # возвращаем PDF накладной
    await create_pdf_invoice(message.from_user.id, dict_invoice[message.from_user.id])
    filename = f'{message.from_user.id} invoice.pdf'
    file_path = "C:\InCodeWeTrust_test\\" + filename
    print(file_path)
    await message.answer_document(document=types.FSInputFile(path=file_path))
    del dict_invoice[message.from_user.id]


# Создание претензии


# Команда создания претензии
@router.message(Command(commands="new_claim"), StateFilter(FSMUser.default_user))
async def create_invoice(message: Message, state: FSMContext):
    dict_claim[message.from_user.id] = []
    await message.answer(text="Введите номер накладной")
    await state.set_state(FSMUserClaim.number_invoice)


# Номер накладной
@router.message(StateFilter(FSMUserClaim.number_invoice))
async def create_invoice(message: Message, state: FSMContext):
    dict_claim[message.from_user.id].append(message.text)
    await message.answer(text="Email для ответа на претензию")
    await state.set_state(FSMUserClaim.email)


# Ввод email
@router.message(StateFilter(FSMUserClaim.email))
async def create_invoice(message: Message, state: FSMContext):
    dict_claim[message.from_user.id].append(message.text)
    await message.answer(text="Описание проблемы")
    await state.set_state(FSMUserClaim.description)


# Ввод описания претензии
@router.message(StateFilter(FSMUserClaim.description))
async def create_invoice(message: Message, state: FSMContext):
    dict_claim[message.from_user.id].append(message.text)
    await message.answer(text="Сумма для возврата")
    await state.set_state(FSMUserClaim.amount)


# Ввод требуемой суммы
@router.message(StateFilter(FSMUserClaim.amount))
async def create_invoice(message: Message, state: FSMContext):
    dict_claim[message.from_user.id].append(message.text)
    await message.answer(text="Прикрепите файл")
    await state.set_state(FSMUserClaim.save_file)


# Сохранение файла претензии
@router.message(StateFilter(FSMUserClaim.save_file), )
async def create_invoice(message: Message, state: FSMContext, bot: Bot):
    destination = rf"C:\InCodeWeTrust_test\middleware\claims\{message.from_user.id}claim.pdf"
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, destination=destination)
    # Сохранение претензии в БД
    dict_claim[message.from_user.id].append(destination)
    await save_claim(user_name=message.from_user.username,
                     id_invoice=dict_claim[message.from_user.id][0],
                     email=dict_claim[message.from_user.id][1],
                     description=dict_claim[message.from_user.id][2],
                     required_amount=dict_claim[message.from_user.id][3],
                     photo=dict_claim[message.from_user.id][4])
    await message.answer(text="Спасибо, вам скоро ответит менеджер.")
    await state.set_state(FSMUser.default_user)
    # отправляем сообщение менеджеру
    user_name = message.from_user.username
    m_chat_id = await manager_chat_id(message.from_user.id)
    await bot.send_message(m_chat_id, text=f'{user_name} cоздал новую претензию')
