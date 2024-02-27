import psycopg2

from config_data.config import load_database, DataBase

# Загружаем данные БД
db: DataBase = load_database()
# Переменная для установки соединения с БД
connection = psycopg2.connect(
    user=db.user_db,
    password=db.user_password,
    database=db.name_db)
# Автоматическое сохранение запросов к БД.
connection.autocommit = True


def init_db(force: bool = False):
    """Создаём нужные таблицы если их ещё нет.
    Параметр force в значении True создаст таблицы в базе данных
    или очистит их если они уже созданы и заполнены данными."""
    with connection.cursor() as c:
        if force:
            c.execute("DROP TABLE IF EXISTS users, invoice, manager, claim, manager_user CASCADE")

            c.execute("CREATE TABLE invoice("
                      "id serial PRIMARY KEY,"
                      "description varchar NOT NULL,"
                      "weight float NOT NULL,"
                      "dimension varchar NOT NULL,"
                      "shipping_address varchar NOT NULL,"
                      "receiving_address varchar NOT NULL,"
                      "payment_method varchar NOT NULL);")

            c.execute("CREATE TABLE claim("
                      "id serial PRIMARY KEY,"
                      "user_name varchar NOT NULL, "
                      "id_invoice integer,"
                      "email varchar NOT NULL,"
                      "description varchar NOT NULL,"
                      "required_amount int,"
                      "photo varchar);")

            c.execute("CREATE TABLE users("
                      "id serial PRIMARY KEY, "
                      "tg_id integer NOT NULL UNIQUE,  "
                      "chat_id integer NOT NULL, "
                      "user_name varchar NOT NULL, "
                      "id_invoice integer REFERENCES invoice(id),"
                      "id_claim integer REFERENCES claim(id));")

            c.execute("CREATE TABLE manager("
                      "id serial PRIMARY KEY,"
                      "tg_id integer NOT NULL UNIQUE,"
                      "chat_id integer NOT NULL);")

            c.execute("CREATE TABLE manager_user("
                      "user_tg_id integer REFERENCES users(tg_id),"
                      "manager_tg_id integer REFERENCES manager(tg_id));")


async def save_user(telegram_id: int, chat_id: int, user_name: str):
    """Функция сохраняющая нового пользователя в БД. Таблица users. """
    with connection.cursor() as c:
        c.execute("INSERT INTO users(tg_id, chat_id, user_name)"
                  "SELECT %s, %s, %s "
                  "WHERE NOT EXISTS (SELECT 1 FROM users WHERE tg_id = (%s));", (telegram_id, chat_id, user_name,
                                                                                 telegram_id))


async def save_manager(telegram_id: int, chat_id: int):
    """Функция сохраняющая нового менеджера в БД. Таблица manager. """
    with connection.cursor() as c:
        c.execute("INSERT INTO manager(tg_id, chat_id)"
                  "SELECT %s, %s "
                  "WHERE NOT EXISTS (SELECT 1 FROM users WHERE tg_id = (%s));", (telegram_id, chat_id, telegram_id))


async def save_invoice(description: str, weight: float, dimension: str,
                       shipping_address: str, receiving_address: str, payment_method: str):
    """Функция сохраняющая новую накладную. """
    with connection.cursor() as c:
        c.execute("INSERT INTO invoice(description, weight, dimension, "
                  "shipping_address, receiving_address, payment_method)"
                  "SELECT %s, %s, %s, %s, %s, %s;", (description, weight, dimension, shipping_address,
                                                     receiving_address, payment_method))


async def save_claim(user_name, id_invoice, email, description, required_amount, photo):
    """Функция сохраняющая новую претензию. """
    with connection.cursor() as c:
        c.execute("INSERT INTO claim(user_name, id_invoice, email, description, required_amount, photo)"
                  "SELECT %s, %s, %s, %s, %s, %s;", (user_name, id_invoice, email, description, required_amount,
                                                     photo))


async def get_claim_list():
    """Функция возвращает словарь с именами пользователей у которых есть дествующие претензии"""
    with connection.cursor() as c:
        c.execute("SELECT user_name "
                  "FROM claim;")
        fetchall = c.fetchall()
        return fetchall


async def update_user_invoices(tg_id):
    """Запись новой накладной у пользователя"""
    with connection.cursor() as c:
        c.execute("UPDATE users "
                  "SET id_invoice = (SELECT id FROM invoice ORDER BY id DESC LIMIT 1) "
                  "WHERE tg_id = %s", (tg_id,))


async def get_id_last_invoices():
    """Возвращает номер последней накладной"""
    with connection.cursor() as c:
        c.execute("SELECT id FROM invoice ORDER BY id DESC LIMIT 1;")
        fetchone = c.fetchone()[0]
        return int(fetchone)


async def get_free_manager_tg_id():
    """Возвращает id менеджера у которого меньше 200 пользователей"""
    with connection.cursor() as c:
        c.execute(
            "SELECT m.tg_id as manager_id "
            "FROM manager m "
            "LEFT JOIN ("
            "SELECT manager_tg_id, COUNT(*) as count_users "
            "FROM manager_user "
            "GROUP BY manager_tg_id"
            ") um ON m.tg_id = um.manager_tg_id "
            "WHERE um.manager_tg_id IS NULL OR um.count_users < 200 "
            "LIMIT 1;"
        )
        fetchone = c.fetchone()[0]
        return int(fetchone)


async def save_user_to_manager(user_tg_id: int):
    """Связь пользователя с менеджером на котором меньше 200 пользователей"""
    free_manager_tg_id = await get_free_manager_tg_id()
    with connection.cursor() as c:
        c.execute(
            "INSERT INTO manager_user (user_tg_id, manager_tg_id) "
            "VALUES (%s, %s);", (user_tg_id, free_manager_tg_id,))


async def manager_chat_id(user_tg_id: int):
    """Возвращает chat_id менеджера"""
    with connection.cursor() as c:
        c.execute(
            "SELECT m.chat_id "
            "FROM manager_user mu "
            "JOIN users u ON mu.user_tg_id = u.tg_id "
            "JOIN manager m ON mu.manager_tg_id = m.tg_id "
            "WHERE u.tg_id = %s;", (user_tg_id,))
        fetchone = c.fetchone()[0]
        return int(fetchone)


async def get_user_chat_id(user_name: str):
    """Возвращает chat_id пользователя"""
    with connection.cursor() as c:
        c.execute(
            "SELECT chat_id "
            "FROM users "
            "WHERE user_name = %s;", (user_name,))
        fetchone = c.fetchone()[0]
        return fetchone
