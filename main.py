#!/opt/bin python3
# -*- coding: utf-8 -*-
import os
import pickle
import sys
import time
from datetime import date as dt
from datetime import datetime, timedelta
from multiprocessing.context import Process

import holidays
import pytz
import schedule
import telebot
from flask import Flask, request
# from flask_sslify import SSLify

from data.config import CHAT_ID, DOMEN, ID_ADMIN, TOKEN, bot
from data.menu import callback_inline, help, help_location, location
from data.methods import send_message
from data.sql import conn, cur

server = Flask(__name__)
# sslif = SSLify(server)

PATH_BOT = f'{os.path.dirname(sys.argv[0])}'
APP_URL = f'{DOMEN}/{TOKEN}'


class ScheduleMessage():
    def try_send_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)

    def start_process():
        p1 = Process(target=ScheduleMessage.try_send_schedule, args=())
        p1.start()


def read_file() -> float:
    """Считываем время из файла для проверки."""
    try:
        with open(f'{PATH_BOT}/check_time.pickle', 'rb') as fb:
            return pickle.load(fb)
    except OSError:
        return 0


def write_file(check_time: float) -> None:
    """Записываем текущее время в файл для проверки на следующем цикле."""
    with open(f'{PATH_BOT}/check_time.pickle', 'wb') as fb:
        pickle.dump(check_time, fb)


def check_note_and_send_message():
    """Основной модуль оповещающий о собыниях в чатах."""
    # проверка на пропуск минут в случаях отказов оборудования
    cur_time_tup = time.mktime(
        datetime.now().replace(second=0, microsecond=0).timetuple()
    )

    last_time_to_check = read_file()

    if cur_time_tup - 60 > last_time_to_check:

        hour_start = datetime.fromtimestamp(
            last_time_to_check
        ).strftime('%H:%M')

        hour_end = datetime.fromtimestamp(
            cur_time_tup
        ).strftime('%H:%M')

        send_message(
            ID_ADMIN,
            f"пропуск врмени с {hour_start} до {hour_end}"
        )

    write_file(cur_time_tup)

    # поиск в базе событий для вывода в текущую минуту
    date_today = dt.today()
    date_today_str = datetime.strftime(date_today, '%d.%m.%Y')
    date_birthday = datetime.strftime(date_today, '%d.%m')
    date_delta_birth = datetime.strftime(
        date_today + timedelta(days=7),
        '%d.%m'
    )
    cur.execute(
        """ SELECT date, time, type, task, id
            FROM tasks
            WHERE date=? OR date=? OR date=?
            ;""", (date_today_str, date_birthday, date_delta_birth)
    )
    tasks = cur.fetchall()

    del_id = []
    time_zone = pytz.timezone('Europe/Moscow')

    time_for_warning = datetime.strftime(
        datetime.now(time_zone) + timedelta(hours=4),
        '%H:%M'
    )
    send_flag = False
    text_note = '*Напоминаю, что через 4 часа запланировано:*\n'

    if time_for_warning != '07:15':
        for item in tasks:
            if date_today_str and time_for_warning in item:
                text_note += f'- {item[3]}\n'
                send_flag = True
                del_id.append(item[4])
        if send_flag:
            send_message(CHAT_ID, text_note, parse_mode='Markdown')

    cur_time_msk = datetime.strftime(datetime.now(time_zone), '%H:%M')

    if cur_time_msk == '07:15':
        send_flag_note = False
        send_flag_birth = False
        send_flag_birth_ahead = False
        text_note = '*На сегодня в планах:*\n'
        text_birthday = f'*Не забудьте что, ежегодно {date_birthday}-ого:*\n'
        text_birthday_ahead = '*Не забудьте что, через 7 дней*\n'

        for item in tasks:
            if date_today_str in item and cur_time_msk in item:
                send_flag_note = True
                text_note += f'- {item[3]}\n'
                del_id.append(item[4])

            if date_birthday in item and cur_time_msk in item:
                send_flag_birth = True
                text_birthday += f'- {item[3]}\n'

            if date_delta_birth in item and cur_time_msk in item:
                if '🎁' in item[3]:
                    send_flag_birth_ahead = True
                    text_birthday_ahead += f'- {item[3]}\n'

        if send_flag_note:
            send_message(
                CHAT_ID,
                text_note,
                parse_mode='Markdown'
            )
        if send_flag_birth:
            send_message(
                CHAT_ID,
                text_birthday,
                parse_mode='Markdown'
            )
        if send_flag_birth_ahead:
            send_message(
                CHAT_ID,
                text_birthday_ahead,
                parse_mode='Markdown'
            )

        ru_holidays = holidays.RU()
        if date_today in ru_holidays:
            hd = ru_holidays.get(date_today)
            send_message(
                CHAT_ID,
                f'Господа, поздравляю вас с праздником - {hd}'
            )

    if len(del_id) > 0:
        tuple_del_id = tuple(del_id) if len(del_id) > 1 else f'({del_id[0]})'
        cur.execute(
            """DELETE FROM tasks WHERE id IN %(list)s ;""" %
            {"list": tuple_del_id}
        )
        conn.commit()


@server.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(
        url=APP_URL,
        drop_pending_updates=True
    )


@server.route('/' + TOKEN, methods=['POST'])
def index():
    if request.method == 'POST':
        message = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(message)
        bot.process_new_updates([update])
        return '!', 200


@bot.message_handler(commands=['help'])
def handler_help(message):
    help(message)


@bot.message_handler(content_types=['location'])
def handler_location(message):
    location(message)


@bot.message_handler(commands=['help_locatoin'])
def handler_help_location(message):
    help_location(message)


@bot.callback_query_handler(func=lambda call: True)
def handler_callback(call):
    callback_inline(call)


schedule.every(1).minutes.do(check_note_and_send_message)


if __name__ == '__main__':
    ScheduleMessage.start_process()
    try:
        server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    except Exception as exc:
        send_message(ID_ADMIN, f'ошибочка polling - {exc}')
