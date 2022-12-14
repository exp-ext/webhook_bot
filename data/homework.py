import requests
from dotenv import load_dotenv
from settings import ID_ADMIN, PRACTICUM_TOKEN, bot, logger

from data.exceptions import (BedRequestError, IncorrectDataError,
                             StatusHomeworkError)

load_dotenv()

LAST_STATUSES = {}

ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(message):
    """Sends a message to Telegram chat."""
    try:
        bot.send_message(ID_ADMIN, message)
        logger.info(f'Сообщение "{message}" успешно отправлено.')

    except Exception as error:
        logger.error(f'Ошибка при отправке сообщения -> {error}')
        raise KeyError(error)


def get_api_answer(current_timestamp):
    """Makes a request to the only endpoint of the API service."""
    params = {'from_date': current_timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
    except requests.exceptions.ConnectionError as error:
        logger.error('Ошибка подключения:', error)
        raise KeyError(error)
    except requests.exceptions.InvalidJSONError as error:
        logger.error('Произошла ошибка JSON', error)
        raise KeyError(error)
    except requests.exceptions.RequestException as error:
        logger.error(error)
        raise KeyError(error)

    if response.status_code != 200:
        rise_msg = (
            f'Эндпоинт {ENDPOINT} недоступен. '
            'Код ответа API: '
        )
        logger.error(f'{rise_msg} {response.status_code}')
        raise BedRequestError(rise_msg, response)

    try:
        return response.json()
    except Exception as error:
        logger.error(f'Ошибка преобразования в JSON формат -> {error}')
        raise KeyError(error)


def check_response(response):
    """Checks the API response for correctness."""
    global LAST_STATUSES
    logger.info('Получен JSON-формат')
    list_homeworks = response['homeworks']
    if not isinstance(response, dict) and not response:
        rise_msg = 'Некорректный словарь.'
        logger.error(rise_msg)
        raise IncorrectDataError(rise_msg)
    elif not isinstance(list_homeworks, list):
        rise_msg = 'Под ключом `homeworks` домашки приходят не в виде списка.'
        logger.error(rise_msg)
        raise IncorrectDataError(rise_msg)
    elif not list_homeworks:
        return None
    elif not LAST_STATUSES:
        LAST_STATUSES = list_homeworks
        return None

    for homework in list_homeworks:
        if homework not in LAST_STATUSES:
            LAST_STATUSES = list_homeworks
            return homework


def parse_status(homework):
    """Extracts the status from the homework."""
    try:
        homework_name = homework.get('homework_name')
        homework_status = homework.get('status')
    except Exception as error:
        logger.error(error)
        raise KeyError(error)

    if homework_name is None or homework_status is None:
        rise_msg = 'Отсутствие ожидаемых ключей в ответе API.'
        logger.error(rise_msg)
        raise IncorrectDataError(rise_msg)

    verdict = HOMEWORK_STATUSES.get(homework_status)

    if verdict is None:
        rise_msg = 'Недокументированный статус домашней работы.'
        logger.error(rise_msg)
        raise StatusHomeworkError(homework_status)

    logger.info('Получен новый статус')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main_yandex_practicum():
    """Основная логика работы модуля."""
    timestamp = 0
    try:
        response = get_api_answer(timestamp)

        homework = check_response(response)

        if homework:
            message = parse_status(homework)
            send_message(message)

    except Exception as error:
        message = f'Сбой в работе модуля Homework: {error}'
        send_message(message)
