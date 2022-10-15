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

PATH_BOT = f'{os.path.dirname(sys.argv[0])}'

bot = TeleBot(TOKEN)

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    filename='logs.log',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

logger.addHandler(logging.StreamHandler(sys.stdout))
