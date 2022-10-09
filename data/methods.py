import json

import requests

from settings import TOKEN

URL = (
    'https://api.telegram.org/bot'
    + TOKEN
)


def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def send_message(chat_id, text, parse_mode=None):
    url = URL + '/sendMessage'
    answer = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode,

    }
    response = requests.post(url, json=answer)
    return response.json()


def delete_message(chat_id, message_id):
    url = URL + '/deleteMessage'
    answer = {
        'chat_id': chat_id,
        'message_id': message_id,
    }
    response = requests.post(url, json=answer)
    return response.json()
