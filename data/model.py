import urllib.parse as urlparse

import psycopg2
from settings import DATABASE_URL, ID_ADMIN, logger

from data.err_mess import send_error_message


def create_connection():
    try:
        url = urlparse.urlparse(DATABASE_URL)
        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port
        return psycopg2.connect(
                    dbname=dbname,
                    user=user,
                    password=password,
                    host=host,
                    port=port
        )
    except psycopg2.Error as error:
        send_error_message(ID_ADMIN, f'ошибка в connection SQL - {error}')
        logger.error(error, exc_info=True)


def make_request(text, variables=None, fetch=None):
    """ Функция делает запрос к БД с параметрами:
        1 text - тест запрос,
        2 variables - переменные в запросе,
        3 fetch - извлечение из БД (all, one)."""
    try:
        conn = create_connection()
        cur = conn.cursor()
        result = '!', 200

        if variables is None:
            cur.execute(text)
        else:
            cur.execute(text, variables)

        if fetch == 'all':
            result = cur.fetchall()
        elif fetch == 'one':
            result = cur.fetchone()
        conn.commit()

        return result

    except psycopg2.errors.DuplicateTable as error:
        logger.info(error)
    except psycopg2.Error as error:
        send_error_message(ID_ADMIN, f'ошибка в cursor SQL - {error}')
        logger.error(error, exc_info=True)
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def drop_table():
    make_request("""DROP TABLE requests;""")


make_request(
    """ CREATE TABLE users (
        user_id integer PRIMARY KEY,
        user_first text,
        user_last text
    );"""
)
make_request(
    """ CREATE TABLE requests (
        id serial PRIMARY KEY,
        date bigint NOT NULL,
        user_id integer NOT NULL,
        chat_id text NOT NULL,
        message_id integer NOT NULL
    );"""
)
make_request(
    """ CREATE TABLE tasks (
        id serial PRIMARY KEY,
        date text NOT NULL,
        time text,
        type text,
        task text NOT NULL,
        user_id integer NOT NULL
    );"""
)
make_request(
    """ CREATE TABLE geolocation (
        id serial PRIMARY KEY,
        date_id bigint NOT NULL,
        user_id integer NOT NULL,
        longitude text NOT NULL,
        latitude text NOT NULL
    );
    """
)
