import logging
import os
import sys

from telebot import TeleBot


TOKEN = os.getenv('TOKEN')

CHAT_ID = os.getenv('CHAT_ID')

OW_API_ID = os.getenv('OW_API_ID')

YANDEX_GEO_API = os.getenv('YANDEX_GEO_API')

ID_CHILDREN = list(os.getenv('ID_CHILDREN').split())

ID_ADMIN = os.getenv('ID_ADMIN')

DOMEN = os.getenv('DOMEN')

DATABASE_URL = os.getenv('DATABASE_URL')

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    filename='logs.log',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

logger.addHandler(logging.StreamHandler(sys.stdout))


def check_tokens():
    """Проверка доступности переменных среды.."""
    env_vars = {
        'TOKEN': TOKEN,
        'OW_API_ID': OW_API_ID,
        'ID_ADMIN': ID_ADMIN,
        'DOMEN': DOMEN,
        'DATABASE_URL': DATABASE_URL,
    }
    for key, value in env_vars.items():
        if not value or value == '':
            logger.critical(
                'Отсутствие обязательной переменной окружения '
                f'<{key}> или её значения, во время запуска бота!'
            )
            raise SystemExit
    logger.info('Проверка токенов прошла успешно.')


bot = TeleBot(TOKEN)
