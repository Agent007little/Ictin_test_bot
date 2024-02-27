from dataclasses import dataclass

from environs import Env


# Сохраняем токен к телеграм боту и ID администраторов
@dataclass
class TgBot:
    token: str  # токен для доступа к телеграм-боту
    admin_ids: list[int]  # список id админов бота


# Сохраняем имя пользователя БД и его пароль
@dataclass
class DataBase:
    user_db: str
    user_password: str
    name_db: str


@dataclass
class Config:
    tg_bot: TgBot


# Создаем функцию, которая будет читать файл .env и возвращать
# экземпляр класса Config с заполненными полями token и admin_ids
def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(
        token=env("BOT_TOKEN"),
        admin_ids=list(map(int, env.list('ADMIN_IDS')))))


def load_database(path: str | None = None) -> DataBase:
    env = Env()
    env.read_env(path)
    return DataBase(
            user_db=env("USER_DB"),
            user_password=env("PASSWORD_DB"),
            name_db=env("DATABASE")
        )