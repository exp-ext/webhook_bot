import requests
from settings import TOKEN, logger

URL = (
    'https://api.telegram.org/bot'
    + TOKEN
)


def send_error_message(chat_id, text):
    url = URL + '/sendMessage'
    answer = {
        'chat_id': chat_id,
        'text': text
    }
    try:
        response = requests.post(url, json=answer)
        return response.json()
    except Exception as error:
        logger.error(error, exc_info=True)
