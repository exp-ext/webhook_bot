from random import choice

import requests
from bs4 import BeautifulSoup
from settings import ID_CHILDREN, bot


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
