import asyncio
import logging

from aiogram import Bot, Dispatcher

from config_data.set_menu import set_main_menu
from database.database import init_db

from config_data.config import Config, load_config
from handlers import commands_handlers, user_handlers, manager_handlers

# Инициализируем логгер
logger = logging.getLogger(__name__)


async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот, диспетчер
    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher()

    # Настраиваем кнопку Меню.
    await set_main_menu(bot)

    # Инициализация базы данных.
    init_db(force=False)

    # Регистриуем роутеры в диспетчере
    dp.include_router(commands_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(manager_handlers.router)
    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
