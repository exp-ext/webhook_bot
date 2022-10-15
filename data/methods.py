import json
import pickle

import requests
from settings import PATH_BOT, TOKEN, logger

URL = (
    'https://api.telegram.org/bot'
    + TOKEN
)


def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def send_error_message(chat_id, text):
    url = URL + '/sendMessage'
    answer = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, json=answer)
    return response.json()


def read_file() -> float:
    """Считываем время из файла для проверки."""
    try:
        with open(f'{PATH_BOT}/check_time.pickle', 'rb') as fb:
            return pickle.load(fb)
    except Exception as error:
        logger.error(error, exc_info=True)


def write_file(check_time: float) -> None:
    """Записываем текущее время в файл для проверки на следующем цикле."""
    try:
        with open(f'{PATH_BOT}/check_time.pickle', 'wb') as fb:
            pickle.dump(check_time, fb)
    except Exception as error:
        logger.error(error, exc_info=True)
