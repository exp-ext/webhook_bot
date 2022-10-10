import os

import psycopg2
from settings import ID_ADMIN, PATH_BOT

from data.methods import send_message


def create_connection():
    try:
        DATABASE_URL = os.environ[f'{PATH_BOT}/db.sqlite3']
        connection = psycopg2.connect(DATABASE_URL)
        return connection
    except psycopg2.DatabaseError as exc:
        send_message(ID_ADMIN, f'ошибочка SQL - {exc}')


def make_request(request, text, variables=None, fetch=None):
    """ Функция делает запрос к БД с параметрами:
        1 request - метод запроса,
        2 text - тест запрос,
        3 variables - переменные в запросе,
        4 fetch - извлечение из БД (all, one)."""
    conn = create_connection()
    cur = conn.cursor()
    result = '!', 200
    if request == 'executescript':
        cur.executescript(text)
    elif request == 'execute':
        if variables is None:
            qwerty = cur.execute(text)
        else:
            qwerty = cur.execute(text, variables)

        if fetch == 'all':
            result = qwerty.fetchall()
        elif fetch == 'one':
            result = qwerty.fetchone()

    conn.commit()
    conn.close()
    return result


make_request(
    'executescript',
    """CREATE TABLE IF NOT EXISTS users(
        userid INT PRIMARY KEY,
        fname TEXT,
        lname TEXT
    );
    CREATE TABLE IF NOT EXISTS requests(
        dateid INT PRIMARY KEY,
        userid INT UNIQUE,
        chatid INT,
        messegeid INT
    );
    CREATE TABLE IF NOT EXISTS tasks(
        id INT PRIMARY KEY,
        date TEXT,
        time TEXT,
        type TEXT,
        task TEXT,
        userid INT
    );
    CREATE TABLE IF NOT EXISTS geolocation(
        iddate INT PRIMARY KEY,
        userid INT,
        longitude TEXT,
        latitude TEXT
    );
    CREATE TABLE IF NOT EXISTS reactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT,
        answer TEXT
    );
    """
)
