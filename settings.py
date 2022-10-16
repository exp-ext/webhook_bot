import logging
import os
import sys

from telebot import TeleBot

# токен телеграмм бота, получить можно
# https://tlgg.ru/BotFather
TOKEN = os.getenv('TOKEN')

# ID telegram семейного группового чата
CHAT_ID = os.getenv('CHAT_ID')

# ID на сайте предоставления прогноза погоды
# https://home.openweathermap.org/api_keys
OW_API_ID = os.getenv('OW_API_ID')

# ID на https://yandex.ru/dev/maps/geocoder/
YANDEX_GEO_API = os.getenv('YANDEX_GEO_API')

# ID детей для предоставления только детских анекдотов
ID_CHILDREN = list(os.getenv('ID_CHILDREN').split())

# ID admin in Telegram, куда будут приходить уведомлеия о пропуске времени
ID_ADMIN = os.getenv('ID_ADMIN')

# домен webhook
DOMEN = os.getenv('DOMEN')

# подключение к postgres
DATABASE_URL = os.getenv('DATABASE_URL')

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')

bot = TeleBot(TOKEN)

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    filename='logs.log',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

logger.addHandler(logging.StreamHandler(sys.stdout))


def check_tokens():
    """Checks the availability of environment variables."""
    env_vars = {
        'TOKEN': TOKEN,
        'CHAT_ID': CHAT_ID,
        'OW_API_ID': OW_API_ID,
        'ID_ADMIN': ID_ADMIN,
        'DOMEN': DOMEN,
        'DATABASE_URL': DATABASE_URL,
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
    }
    for key, value in env_vars.items():
        if value is None or value == '':
            logger.critical(
                'Отсутствие обязательной переменной окружения '
                f'<{key}> или её значения, во время запуска бота!'
            )
            return False
    logger.info('Проверка токенов прошла успешно.')
    return True
