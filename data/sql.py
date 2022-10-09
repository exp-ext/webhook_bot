import os
import sqlite3
import sys

PATH_BOT = f'{os.path.dirname(sys.argv[0])}'

conn = sqlite3.connect(
    f'{PATH_BOT}/data_for_notebot.db', check_same_thread=False
)

cur = conn.cursor()

cur.executescript(
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
conn.commit()
