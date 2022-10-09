import time
from datetime import date as dt
from datetime import datetime, timedelta
from random import choice

import requests
from bs4 import BeautifulSoup

from data.config import ID_CHILDREN, bot


def where_to_go(message):
    """Опрос api kudago.com с формированием списка событий в СПб."""
    try:
        date_today_int = dt.today()
        date_yesterday = date_today_int - timedelta(days=1)
        date_tomorrow = date_today_int + timedelta(days=1)
        date_yesterday = time.mktime(date_yesterday.timetuple())
        date_tomorrow = time.mktime(date_tomorrow.timetuple())

        resp = requests.get(
            'https://kudago.com/public-api/v1.4/events/',
            {
                'actual_since': date_yesterday,
                'actual_until': date_tomorrow,
                'location': 'spb',
                'is_free': True,
            }
        )

        next_data = resp.json()

        date_today = datetime.strftime(date_today_int, '%Y-%m-%d')
        text = (
            '[BCЕ МЕРОПРИЯТИЯ НА СЕГОДНЯ](https://kudago.com/spb/festival/'
            f'?date={date_today}&hide_online=y&only_free=y)\n\n'
        )

        excluded_list = ['197880', '198003', '187745', '187466', '187745']

        for item in next_data['results']:
            if item['id'] not in excluded_list:
                text += (
                    f"- {item['title'].capitalize()} [>>>]"
                    f"(https://kudago.com/spb/event/{item['slug']}/)\n"
                )
                text += '-------------\n'

        bot.send_message(message.chat.id, text, parse_mode='Markdown')

    except Exception as exc:
        bot.send_message(message.chat.id, f'ошибочка вышла - {exc}')


def joke_parsing(id_user: int, all: bool = False) -> str | list[str]:
    """Парсинг сайта с анекдотами."""
    try:
        if id_user in ID_CHILDREN:
            resp = requests.get('https://anekdotbar.ru/dlya-detey/')
        else:
            resp = requests.get('https://anekdotbar.ru/')

        bs_data = BeautifulSoup(resp.text, "html.parser")
        an_text = bs_data.select('.tecst')
        response_list = []
        for x in an_text:
            joke = x.getText().strip().split('\n')[0]
            response_list.append(joke)
            response_all = ''
        if not all:
            return choice(response_list)
        else:
            for x in response_list:
                response_all += f'~ {x} \n\n'
            return response_all

    except Exception as exc:
        return f'ошибочка вышла - {exc}'


def show_joke(message):
    """Показать анекдот."""
    id_user = message.chat.id
    bot.send_message(message.chat.id, joke_parsing(id_user))
