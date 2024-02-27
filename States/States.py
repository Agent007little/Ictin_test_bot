# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
from aiogram.fsm.state import StatesGroup, State


class FSMUser(StatesGroup):
    default_user = State()  # обычное состояние юзера


class FSMUserInvoice(FSMUser):
    weight = State()
    cargo_dimensions = State()
    shipping_address = State()
    receiving_address = State()
    payment_method = State()
    finish_state = State()


class FSMUserClaim(FSMUser):
    number_invoice = State()
    email = State()
    description = State()
    amount = State()
    save_file = State()


class FSMManager(StatesGroup):
    default_manager = State()  # обычное состояние менеджера
    wait_user_name = State()
    chat_with_user = State()

# class FSMManagerUser(FSMManager):
#     def __init__(self, user_chat_id: int):
#         self.user_chat_id = user_chat_id
#
#     def get_user_chat_id(self):
#         return self.user_chat_id


