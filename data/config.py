from telebot import TeleBot

# токен телеграмм бота, получить можно
# https://tlgg.ru/BotFather
TOKEN = '5395922222:AAGVENnG3cYEqiBvE4G_y5sALE7KkyaFuY8'

# ID telegram семейного группового чата
CHAT_ID = '-1001777599892'

# ID на сайте предоставления прогноза погоды
# https://home.openweathermap.org/api_keys
OW_API_ID = '46bcbd1d671a980f039b66823a1b3e94'

# ID на https://yandex.ru/dev/maps/geocoder/
YANDEX_GEO_API = 'dfbc282b-38dd-4d50-953b-d549bd437432'

# ID детей для предоставления только детских анекдотов
ID_CHILDREN = ['2018237767']

# ID admin in Telegram, куда будут приходить уведомлеия о пропуске времени
ID_ADMIN = '225429268'

DOMEN = 'https://my-webhook-bot.herokuapp.com/'

# DOMEN = 'https://f08e-178-67-245-148.eu.ngrok.io'

bot = TeleBot(TOKEN)


"""
setWebhook
https://api.telegram.org/bot5586724882:AAFh3utxGM8-_PvYpnVP5szWRPj1YMMyz2I/setWebhook?url=https://my-webhook-bot.herokuapp.com/

deleteWebhook
https://api.telegram.org/bot5586724882:AAFh3utxGM8-_PvYpnVP5szWRPj1YMMyz2I/deleteWebhook?url=https://f08e-178-67-245-148.eu.ngrok.io

"""
