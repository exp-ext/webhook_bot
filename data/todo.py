import difflib
import re
from datetime import date as dt
from datetime import datetime, timedelta

from settings import bot
from data.model import make_request


def similarity(s1: str, s2: str) -> float:
    """Сравнение записей в модуле difflib
       [https://docs.python.org/3/library/difflib.html]."""
    normalized1 = s1.lower()
    normalized2 = s2.lower()
    matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
    return matcher.ratio()


class Messege:
    """Создаем объект напоминания."""
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
        tasks = make_request(
            """ SELECT id, date, time, task
                FROM tasks
                WHERE date=%s;
            """,
            (self.date,),
            fetch='all'
        )
        if len(tasks) > 0:
            for item in tasks:
                simil = similarity(item[3], self.message)
                if simil > 0.618:
                    return False

        new_tasks = (
            self.date, self.time, self.type_note, self.message, user_id
        )

        make_request(
            """INSERT INTO tasks (date, time, type, task, user_id)
               VALUES(%s, %s, %s, %s, %s);
            """,
            new_tasks
        )
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
        question_id = make_request(
            """ SELECT chat_id, message_id
                FROM requests
                WHERE user_id=%s AND chat_id=%s;
            """,
            (user_id, str(message.chat.id)),
            fetch='one'
        )
        bot.delete_message(question_id[0], question_id[1])

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
            tasks = make_request(
                """ SELECT id, task
                    FROM tasks
                    WHERE date=%s AND task LIKE %s;
                """,
                (date, '%' + task + '%'),
                fetch='one'
            )
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
                make_request(
                    """DELETE FROM tasks WHERE id=%s;""",
                    (tasks[0],)
                )
                send_text = (
                    f"{message.from_user.first_name}, "
                    f"запись *<{tasks[1]}>* на дату {date} удалена"
                )
                bot.send_message(
                    message.chat.id,
                    send_text,
                    parse_mode='Markdown'
                )

        question_id = make_request(
            """ SELECT chat_id, message_id
                FROM requests
                WHERE user_id=%s AND chat_id=%s;
            """,
            (message.from_user.id, str(message.chat.id)),
            fetch='one'
        )
        bot.delete_message(question_id[0], question_id[1])

        message_id = message.message_id
        bot.delete_message(message.chat.id, int(message_id))

    except Exception as exc:
        bot.send_message(message.chat.id, f'ошибка - {exc}')
        pass


def show_note_on_date(message):
    """Вывод записей из БД на конкретную дату."""
    data = getter_data_for_parsing_messege(message.text)
    date = data[0]
    date_every_year = '.'.join([date.split('.')[0], date.split('.')[1]])

    if date is None:
        send_text = (
            f'*{message.from_user.first_name}*, '
            'не удалось разобрать что это за дата 🧐. Попробуйте снова 🙄'
        )
        bot.send_message(
            message.chat.id,
            send_text,
            parse_mode='Markdown'
        )
    else:
        tasks = make_request(
            """ SELECT date, type, task
                FROM tasks
                WHERE date=%s or date=%s;
            """,
            (date_every_year, date),
            fetch='all'
        )
        text_notes = (
            f'*{message.from_user.first_name}, '
            f'на {date} запланировано 📜:*\n'
        )
        send_note = False
        text_birthday = (
            f'*{message.from_user.first_name}, '
            f'на выбранную дату {date} найдено ежегодное напоминание 🎉:*\n'
        )
        send_birthday = False

        for item in tasks:
            if item[1] == 'todo':
                text_notes += f'- {item[2]}\n'
                send_note = True
            if item[1] == 'birthday':
                text_birthday += f'- {item[2]}\n'
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
    question_id = make_request(
            """ SELECT chat_id, message_id
                FROM requests
                WHERE user_id=%s AND chat_id=%s;
            """,
            (message.from_user.id, str(message.chat.id)),
            fetch='one'
        )
    bot.delete_message(question_id[0], question_id[1])

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
    tasks = make_request(
        """ SELECT date, task
            FROM tasks
            WHERE type='todo' AND task NOT LIKE ('%' || 'с апогеем' || '%');
        """,
        fetch='all'
    )
    for item in tasks:
        note.append(f'{item[0]} - {item[1]}')

    note.sort(key=sort_date)
    if tasks:
        note_sort = (
            f'*{message.from_user.first_name}, '
            'в наших планах есть записи 📜:*\n'
        )
    else:
        note_sort = (
            f'*{message.from_user.first_name}, '
            'у нас нет никаких планов 👌*\n'
        )
    for n in note:
        note_sort = note_sort + f'{n}\n'

    bot.send_message(message.chat.id, note_sort, parse_mode='Markdown')


def show_all_birthdays(message):
    """Показать все дни рождения."""
    note = []
    tasks = make_request(
        """ SELECT date, task
            FROM tasks
            WHERE type='birthday';
        """,
        fetch='all'
    )
    for item in tasks:
        note.append(f'{item[0]} - {item[1]}')

    note.sort(key=lambda x: int(f'{x[:5].split(".")[1]}{x[:5].split(".")[0]}'))
    if tasks:
        note_sort = (
            f'*{message.from_user.first_name}, '
            'найдены ежегодные напоминания 🎉:*\n'
        )
    else:
        note_sort = (
            f'*{message.from_user.first_name}, '
            'похоже что у вас нет ежегодных напоминания 🫤:*\n'
        )
    for n in note:
        note_sort = note_sort + f'{n}\n'

    bot.send_message(message.chat.id, note_sort, parse_mode='Markdown')
