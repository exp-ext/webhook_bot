#!/usr/bin python3
# -*- coding: utf-8 -*-
import os
from threading import Thread
import time
from datetime import date as dt
from datetime import datetime, timedelta
from multiprocessing import Process

import holidays
import pytz
import telebot
from flask import Flask, request

from data.homework import main_yandex_practicum
from data.menu import callback_inline, help, help_location, location
from data.err_mess import send_error_message
from data.model import make_request
from settings import (CHAT_ID, DOMEN, ID_ADMIN, PRACTICUM_TOKEN, TOKEN, bot,
                      check_tokens, logger)
from data.other_api import get_forismatic_quotes

server = Flask(__name__)

APP_URL = f'{DOMEN}/{TOKEN}'
LAST_TIME = 0


class ScheduleProcess():
    """Дополнительный процесс для main_process_distributor."""
    def try_check():
        start_time = time.sleep(1)
        if start_time % 60 == 0:
            while True:
                try:
                    time.sleep(60)
                    cur_time = int(time.time())

                    t1 = Thread(
                        group=None,
                        target=main_process_distributor,
                        args=(cur_time,)
                    )
                    t1.start()

                    if cur_time % 600 == 0 and PRACTICUM_TOKEN:
                        t1 = Thread(
                            group=None,
                            target=main_yandex_practicum,
                            args=()
                        )
                        t1.start()

                except Exception as exc:
                    send_error_message(
                        ID_ADMIN, f'ошибка главного процесса - {exc}'
                    )
                    logger.exception(f'ошибка главного процесса - {exc}')

    def start_process():
        p1 = Process(target=ScheduleProcess.try_check, args=())
        p1.start()


def main_process_distributor(cur_time_tup):
    """Основной модуль оповещающий о событиях в чатах."""
    # проверка на пропуск минут
    global LAST_TIME
    last_time_to_check = LAST_TIME

    if cur_time_tup - 60 > last_time_to_check:
        hour_start = datetime.fromtimestamp(
            last_time_to_check
        ).strftime('%H:%M')
        hour_end = datetime.fromtimestamp(
            cur_time_tup
        ).strftime('%H:%M')

        bot.send_message(
            ID_ADMIN,
            f"пропуск времени с {hour_start} до {hour_end}"
        )
    LAST_TIME = cur_time_tup

    # поиск в базе событий для вывода в текущую минуту
    date_today = dt.today()
    date_today_str = datetime.strftime(date_today, '%d.%m.%Y')
    date_birthday = datetime.strftime(date_today, '%d.%m')
    date_delta_birth = datetime.strftime(
        date_today + timedelta(days=7),
        '%d.%m'
    )
    tasks = make_request(
        """ SELECT date, time, type, task, id
            FROM tasks
            WHERE date=%s OR date=%s OR date=%s
            ;""",
        (date_today_str, date_birthday, date_delta_birth),
        fetch='all'
    )
    del_id = []
    time_zone = pytz.timezone('Europe/Moscow')

    time_for_warning = datetime.strftime(
        datetime.now(time_zone) + timedelta(hours=4),
        '%H:%M'
    )
    cur_time_msk = datetime.strftime(datetime.now(time_zone), '%H:%M')

    if cur_time_msk == '10:00':
        msg = '*Цитата на злобу дня:*\n' + get_forismatic_quotes()
        bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
    elif cur_time_msk == '08:00':
        ru_holidays = holidays.RU()
        if date_today in ru_holidays:
            hd = ru_holidays.get(date_today)
            bot.send_message(
                CHAT_ID,
                f'Господа, поздравляю вас с праздником - *{hd}*',
                parse_mode='Markdown'
            )
    elif cur_time_msk == '07:15':
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
            bot.send_message(
                CHAT_ID,
                text_note,
                parse_mode='Markdown'
            )
        if send_flag_birth:
            bot.send_message(
                CHAT_ID,
                text_birthday,
                parse_mode='Markdown'
            )
        if send_flag_birth_ahead:
            bot.send_message(
                CHAT_ID,
                text_birthday_ahead,
                parse_mode='Markdown'
            )

    if time_for_warning != '07:15':
        send_flag = False
        text_note = '*Напоминаю, что у вас есть планы 🧾:*\n'
        for item in tasks:
            if date_today_str and time_for_warning in item:
                text_note += f'- {item[3]}\n'
                send_flag = True
                del_id.append(item[4])
        if send_flag:
            bot.send_message(CHAT_ID, text_note, parse_mode='Markdown')

    if len(del_id) > 0:
        if len(del_id) == 1:
            make_request(
                    """DELETE FROM tasks WHERE id=%s;""",
                    (del_id[0],)
                )
        else:
            make_request(
                """DELETE FROM tasks WHERE id IN %(list)s ;""",
                {"list": tuple(del_id)}
            )


@bot.message_handler(commands=['help'])
def handler_help(message):
    help(message)


@bot.message_handler(content_types=['location'])
def handler_location(message):
    location(message)


@bot.message_handler(commands=['help_location'])
def handler_help_location(message):
    help_location(message)


@bot.callback_query_handler(func=lambda call: True)
def handler_callback(call):
    callback_inline(call)


@server.route('/test', methods=['GET'])
def test():
    return 'alive'


@server.route('/' + TOKEN, methods=['POST'])
def index():
    if request.method == 'POST':
        message = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(message)
        bot.process_new_updates([update])
        return '!', 200


def start():
    """Запуск бота."""
    if check_tokens() is False:
        raise SystemExit

    ScheduleProcess.start_process()
    try:
        bot.remove_webhook()
        bot.set_webhook(
            url=APP_URL,
            drop_pending_updates=True
        )
        server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    except Exception as error:
        send_error_message(ID_ADMIN, f'ошибка webhook - {error}')
        logger.error(error, exc_info=True)


if __name__ == '__main__':
    start()
