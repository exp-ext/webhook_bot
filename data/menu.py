import time

from telebot import types

from settings import bot
from data.geoservice import (current_weather, my_current_geoposition,
                             weather_forecast)
from data.parsing import show_joke, where_to_go
from data.model import make_request
from data.todo import (add_notes, del_note, show_all_birthdays, show_all_notes,
                       show_note_on_date)


def replace_messege_id(user_id: int, messege_id: int, chat_id: int) -> None:
    """Заменяем последний ID сообщения user в БД."""
    iddate = round(time.time() * 100000)
    new_request = (iddate, user_id, chat_id, messege_id)

    make_request(
        'execute',
        """REPLACE INTO requests VALUES(?, ?, ?, ?);""",
        new_request
    )


def help(message):
    """Выводим кнопки основного меню на экран."""
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    add_note = types.InlineKeyboardButton(
        text="💬 добавить запись",
        callback_data='add'
    )
    del_note = types.InlineKeyboardButton(
        text="❌ удалить запись",
        callback_data='del'
    )
    get_all_birthdays = types.InlineKeyboardButton(
        "🚼 календарь рождений",
        callback_data='birthdays'
    )
    get_note_on_date = types.InlineKeyboardButton(
        "📅 планы на дату",
        callback_data='show'
    )
    get_all_note = types.InlineKeyboardButton(
        "📝 все планы",
        callback_data='show_all'
    )
    get_joke = types.InlineKeyboardButton(
        "🎭 анекдот",
        callback_data='joke'
    )
    where_to_go = types.InlineKeyboardButton(
        "🏄 список мероприятий в СПб",
        callback_data='where_to_go'
    )

    keyboard.add(add_note, del_note, get_all_birthdays,
                 get_note_on_date, get_all_note, get_joke)
    keyboard.add(where_to_go)

    menu_text = (
        "* 💡  ГЛАВНОЕ МЕНЮ  💡 *".center(28, "~")
        + "\n"
        + f"для пользователя {message.from_user.first_name}".center(28, "~")
    )

    menu_id = bot.send_message(
        message.chat.id,
        menu_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    ).message_id

    replace_messege_id(message.from_user.id, menu_id, message.chat.id)

    message_id = message.message_id
    bot.delete_message(message.chat.id, message_id)

    add_new_user = (
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.last_name
    )

    make_request(
        'execute',
        """REPLACE INTO users VALUES(?, ?, ?);""",
        add_new_user
    )


def location(message):
    """Кнопки меню погоды в только личном чате с ботом"""
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    weather_per_day = types.InlineKeyboardButton(
        text="🌈 погода сейчас",
        callback_data='weather_per_day'
    )
    get_weather_for_4_day = types.InlineKeyboardButton(
        text="☔️ прогноз погоды на 4 дня",
        callback_data='weather'
    )
    get_my_position = types.InlineKeyboardButton(
        text="🛰 моя позиция для группы",
        callback_data='my_position'
    )
    keyboard.add(weather_per_day, get_weather_for_4_day, get_my_position)

    menu_text = "* 💡  МЕНЮ ПОГОДЫ  💡 *".center(28, "~")

    menu_id = bot.send_message(
        message.chat.id,
        menu_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    ).message_id

    chat_id = message.chat.id
    lat = message.location.latitude
    lon = message.location.longitude

    replace_messege_id(message.from_user.id, menu_id, chat_id)

    iddate = round(time.time() * 100000)
    geo = (iddate, message.from_user.id, lon, lat)

    make_request(
        'execute',
        """INSERT INTO geolocation VALUES(?, ?, ?, ?);""",
        geo
    )

    message_id = message.message_id
    bot.delete_message(message.chat.id, message_id)


def callback_inline(call):
    """Распределяем функции согласно нажатой кнопки."""
    message = call.message

    menu_id = make_request(
        'execute',
        """ SELECT MAX(dateid), chatid, messegeid
            FROM requests
            WHERE userid=? and chatid=?
        ;""",
        (call.from_user.id,  message.chat.id),
        fetch='all'
    )

    bot.delete_message(menu_id[0][1], menu_id[0][2])

    if call.data == 'birthdays':
        message.from_user.first_name = call.from_user.first_name
        show_all_birthdays(message)
    elif call.data == 'show_all':
        message.from_user.first_name = call.from_user.first_name
        show_all_notes(message)
    elif call.data == 'joke':
        show_joke(message)
    elif call.data == 'add':
        req_text = (
            f'*{call.from_user.first_name}*,'
            'введите текст заметки с датой и временем'
        )
        msg = bot.send_message(
            message.chat.id,
            req_text,
            parse_mode='Markdown'
        )
        replace_messege_id(call.from_user.id, msg.message_id, message.chat.id)

        bot.register_next_step_handler(msg, add_notes)
    elif call.data == 'del':
        req_text = (
            f'*{call.from_user.first_name}*,'
            ' введите дату и фрагмент текста заметки для её удаления'
        )
        msg = bot.send_message(
            message.chat.id,
            req_text,
            parse_mode='Markdown'
        )
        replace_messege_id(call.from_user.id, msg.message_id, message.chat.id)

        bot.register_next_step_handler(msg, del_note)
    elif call.data == 'show':
        req_text = (
            f'*{call.from_user.first_name}*,'
            ' введите нужную дату для отображения заметок'
        )
        msg = bot.send_message(
            message.chat.id,
            req_text,
            parse_mode='Markdown'
            )
        replace_messege_id(call.from_user.id, msg.message_id, message.chat.id)
        bot.register_next_step_handler(msg, show_note_on_date)
    elif call.data == 'where_to_go':
        where_to_go(message)
    elif call.data == 'weather':
        message.from_user.id = call.from_user.id
        weather_forecast(message)
    elif call.data == 'weather_per_day':
        message.from_user.id = call.from_user.id
        current_weather(message)
    elif call.data == 'my_position':
        message.from_user.first_name = call.from_user.first_name
        message.from_user.id = call.from_user.id
        my_current_geoposition(message)


def help_location(message):
    """Создаём кнопку для получения геокоординат в его личном чате."""
    keyboard = types.ReplyKeyboardMarkup(
        row_width=1,
        resize_keyboard=True
    )
    button_geo = types.KeyboardButton(
        text="☀️ получить погоду и 👣 моё местоположение",
        request_location=True
    )
    keyboard.add(button_geo)
    bot.send_message(
        message.chat.id,
        'появилась кнопочка погоды по Вашим координатам',
        reply_markup=keyboard
    )
    message_id = message.message_id
    bot.delete_message(message.chat.id, int(message_id))
