import difflib
import re
import time
from datetime import date as dt
from datetime import datetime, timedelta

from data.config import bot
from data.sql import conn, cur


def similarity(s1: str, s2: str) -> float:
    """Сравнение записей в модуле difflib
       [https://docs.python.org/3/library/difflib.html]."""
    normalized1 = s1.lower()
    normalized2 = s2.lower()
    matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
    return matcher.ratio()


class Messege:
    """Создаем объкт напоминания."""
    __slots__ = ('date', 'message', 'time', 'type_note')

    def __init__(self,
                 date: str,
                 message: str,
                 time: str,
                 type_note: str,
                 ) -> None:
        self.date = date
        self.message = message
        self.time = time
        self.type_note = type_note

    def add_todo(self, user_id: int) -> bool:
        """Добавляем задачу в БД."""
        cur.execute(
            """ SELECT id, date, time, task
                FROM tasks
                WHERE date=?;
            """,
            (self.date,)
        )
        tasks = cur.fetchall()

        if len(tasks) > 0:
            for item in tasks:
                simil = similarity(item[3], self.message)
                if simil > 0.618:
                    return False
        id = round(time.time() * 100000)
        new_tasks = (id, self.date, self.time,
                     self.type_note, self.message, user_id)

        cur.execute(
            """INSERT INTO tasks VALUES(?, ?, ?, ?, ?, ?);""",
            new_tasks
        )
        conn.commit()
        return True


def getter_data_for_parsing_messege(message) -> list[str]:
    """Создаем список для класса."""
    type_note = 'todo'

    if re.search(r'\d+[./-]\d+[./-]\d+', message):
        date_found = re.search(
            r'\d+[./-]\d+[./-]\d+',
            message
        ).group()
        date_found = re.sub(r'[/-]', '.', date_found)

        if len(date_found.split(".")[2]) == 2:
            year = f'20{date_found.split(".")[2]}'
        else:
            year = date_found.split(".")[2]

        date = datetime(
            int(year),
            int(date_found.split(".")[1]),
            int(date_found.split(".")[0])
        )
        date_str = datetime.strftime(date, '%d.%m.%Y')

    elif re.search(r'\d+[./-]\d+', message):
        date_found = re.search(r'\d+[./-]\d+', message).group()
        date = datetime(
            2000,
            int(date_found.split(".")[1]),
            int(date_found.split(".")[0])
        )
        date_str = datetime.strftime(date, '%d.%m')
        type_note = 'birthday'

    elif re.search(r'[Сс]егодня|[Зз]автра', message):
        date_found = re.search(r'[Сс]егодня|[Зз]автра', message).group()
        today = datetime.strftime(dt.today(), '%d.%m.%Y')
        tomorrow = datetime.strftime(
            dt.today() + timedelta(days=1),
            '%d.%m.%Y'
            )
        near_future = {
            'сегодня': today,
            'завтра': tomorrow,
            }
        date_str = near_future[date_found.lower()]
    else:
        date_found = ''
        date_str = None

    if re.search(r'\d+[:]\d{2}', message):
        time_found = re.search(r'\d+[:]\d{2}', message).group()
        time = datetime(
            2000,
            1,
            1,
            int(time_found.split(":")[0]),
            int(time_found.split(":")[1])
        )
        time_str = datetime.strftime(time, '%H:%M')
    else:
        time_str = '07:15'

    message_without_date = re.sub(date_found, '', message)
    message_without_date = re.sub(
        r'\s+',
        ' ',
        message_without_date
    ).strip()

    return [date_str, message_without_date, time_str, type_note]


def add_notes(message):
    """Добавление записи в БД."""
    try:
        data = getter_data_for_parsing_messege(message.text)
        pars_mess = Messege(*data)
        date = pars_mess.date
        t_time = pars_mess.time
        type_note = pars_mess.type_note
        task = pars_mess.message
        user_id = message.from_user.id

        if date is None:
            text_send = (
                f'Дата в запросе *<{message.text}>* '
                'не найдена, напоминание не записано'
            )
            bot.send_message(
                message.chat.id,
                text_send,
                parse_mode='Markdown'
            )

        elif pars_mess.add_todo(user_id) is False:
            text_send = (
                'Есть более чем на 61% схожая запись на дату'
                f' *{date}*,\nсообщение *<{task}>* не добавлено'
            )
            bot.send_message(
                message.chat.id,
                text_send,
                parse_mode='Markdown'
            )
        else:
            if type_note == 'todo':
                text_send = (
                    f'{message.from_user.first_name}, напоминание, *<{task}>* '
                    f'добавлена на дату <{date}> на время <{t_time}>'
                )
                bot.send_message(
                    message.chat.id,
                    text_send, parse_mode='Markdown'
                    )
            elif type_note == 'birthday':
                text_send = (
                    f'{message.from_user.first_name}, ежегодное '
                    f'напоминание о *<{task}>* добавлена на дату <{date}>'
                )
                bot.send_message(
                    message.chat.id,
                    text_send, parse_mode='Markdown'
                )

        cur.execute(
            """ SELECT MAX(dateid), chatid, messegeid
                FROM requests
                WHERE userid=? and chatid=?;
            """,
            (user_id, message.chat.id)
        )
        question_id = cur.fetchall()
        bot.delete_message(question_id[0][1], question_id[0][2])

        message_id = message.message_id
        bot.delete_message(message.chat.id, message_id)

    except Exception as exc:
        bot.send_message(message.chat.id, f'ошибочка вышла - {exc}')


def del_note(message):
    """Удаление записи из БД."""
    try:
        data = getter_data_for_parsing_messege(message.text)
        pars_mess = Messege(*data)
        date = pars_mess.date
        task = pars_mess.message

        if date is None:
            send_text = (
                f'*{message.from_user.first_name}*, '
                'дата в запросе не найдена! Начните операцию заново.'
            )
            bot.send_message(
                message.chat.id,
                send_text, parse_mode='Markdown'
            )
        else:
            cur.execute(
                """ SELECT id, task
                    FROM tasks
                    WHERE date=? AND task LIKE ('%' || ? || '%');
                """,
                (date, task)
            )
            tasks = cur.fetchone()

            if tasks is None:
                send_text = (
                    f'{message.from_user.first_name}, '
                    f'нет заметок с текстом *<{task}>* на эту дату!'
                )
                bot.send_message(
                    message.chat.id,
                    send_text, parse_mode='Markdown'
                )
            else:
                cur.execute(
                    """DELETE FROM tasks WHERE id=?""",
                    (tasks[0],)
                )
                conn.commit()
                send_text = (
                    f"{message.from_user.first_name}, "
                    f"запись *<{tasks[1]}>* на дату {date} удалена"
                )
                bot.send_message(
                    message.chat.id,
                    send_text,
                    parse_mode='Markdown'
                )

        cur.execute(
            """ SELECT MAX(dateid), chatid ,messegeid
                FROM requests
                WHERE userid=? and chatid=?;
            """,
            (message.from_user.id, message.chat.id)
            )
        question_id = cur.fetchone()
        bot.delete_message(question_id[1], question_id[2])

        message_id = message.message_id
        bot.delete_message(message.chat.id, int(message_id))

    except Exception as exc:
        bot.send_message(message.chat.id, f'ошибочка вышла - {exc}')
        pass


def show_note_on_date(message):
    """Вывод записей из БД на конкретую дату."""
    command_text = re.sub(r'/show ', '', message.text)
    pars_mess = Messege(command_text)
    date = pars_mess.date
    date_every_year = '.'.join([date.split('.')[0], date.split('.')[1]])

    if date is None:
        send_text = (
            f'*{message.from_user.first_name}*, '
            'дата в запросе не найдена! Начните операцию сначала.'
        )
        bot.send_message(
            message.chat.id,
            send_text,
            parse_mode='Markdown'
        )
    else:
        cur.execute(
            """ SELECT date, type, task
            FROM tasks
            WHERE date=? or date=?;
            """,
            (date_every_year, date)
        )
        tasks = cur.fetchall()

        text_notes = (
            f'*{message.from_user.first_name}, '
            'на {date} запланировано:*\n'
        )
        send_note = False
        text_birthday = (
            f'*{message.from_user.first_name}, '
            'на выбранную дату {date} найдено ежегодное напоминание:*\n'
        )
        send_birthday = False

        for item in tasks:
            if item[1] == 'todo':
                text_notes += f'- {item[2]}'
                send_note = True
            if item[1] == 'birthday':
                text_birthday += f'- {item[2]}'
                send_birthday = True

        if send_note:
            bot.send_message(
                message.chat.id,
                text_notes,
                parse_mode='Markdown'
            )
        if send_note and send_birthday:
            bot.send_message(
                message.chat.id,
                'и ешё,',
                parse_mode='Markdown'
            )
        if send_birthday:
            bot.send_message(
                message.chat.id,
                text_birthday,
                parse_mode='Markdown'
            )
    cur.execute(
        """ SELECT MAX(dateid), chatid, messegeid
            FROM requests
            WHERE userid=? and chatid=?;
        """,
        (message.from_user.id, message.chat.id)
    )
    question_id = cur.fetchone()
    bot.delete_message(question_id[1], question_id[2])

    message_id = message.message_id
    bot.delete_message(message.chat.id, int(message_id))


def sort_date(x: int) -> int:
    """Ключ фильтра для сортировки."""
    d = x.split(" - ")[0]
    sort_val = f'{d.split(".")[2]}{d.split(".")[1]}{d.split(".")[1]}'
    return int(sort_val)


def show_all_notes(message):
    """Вывод всех записей из БД."""
    note = []
    cur.execute(
        """ SELECT date, task
            FROM tasks
            WHERE type='todo' AND task NOT LIKE ('%' || 'с апогеем' || '%');
        """
    )
    tasks = cur.fetchall()

    for item in tasks:
        note.append(f'{item[0]} - {item[1]}')

    note.sort(key=sort_date)
    note_sort = (
        f'*{message.from_user.first_name}, '
        'согласно запроса, в базе найдено:*\n'
    )
    for n in note:
        note_sort = note_sort + f'{n}\n'

    bot.send_message(message.chat.id, note_sort, parse_mode='Markdown')


def show_all_birthdays(message):
    """Показать все дни рождения."""
    note = []
    cur.execute(
        """ SELECT date, task
            FROM tasks
            WHERE type='birthday';
        """
    )
    tasks = cur.fetchall()

    for item in tasks:
        note.append(f'{item[0]} - {item[1]}')

    note.sort(key=lambda x: int(f'{x[:5].split(".")[1]}{x[:5].split(".")[0]}'))
    note_sort = (
        f'*{message.from_user.first_name}, '
        'согласно Вашего запроса, найдены ежегодные напоминания:*\n'
    )
    for n in note:
        note_sort = note_sort + f'{n}\n'

    bot.send_message(message.chat.id, note_sort, parse_mode='Markdown')
