from datetime import datetime
from math import asin, cos, radians, sin, sqrt
from typing import Tuple

import requests
from settings import CHAT_ID, OW_API_ID, YANDEX_GEO_API, bot, logger

from data.model import make_request


def get_address_from_coords(coords: str):
    """Опрос api geocode-maps.yandex для получения адреса местонахождения."""
    params = {
        "apikey": YANDEX_GEO_API,
        "format": "json",
        "lang": "ru_RU",
        "kind": "house",
        "geocode": coords,
    }
    try:
        r = requests.get(
            url="https://geocode-maps.yandex.ru/1.x/",
            params=params
        )
        json_data = r.json()

        return (
            json_data["response"]["GeoObjectCollection"]["featureMember"]
            [0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]
            ["AddressDetails"]["Country"]["AddressLine"]
        )

    except Exception as error:
        logger.error(error, exc_info=True)


def status_weather(description_weather: str) -> str:
    """Добавление картинки в описание."""
    try:
        dict_weather = {
            'ясно': ' ☀️ ясно',
            'переменная облачность': ' 🌤 переменная облачность',
            'небольшая облачность': ' 🌤 переменная облачность',
            'облачно с прояснениями': ' ⛅️ облачно с прояснениями',
            'пасмурно': ' ☁️ пасмурно',
            'небольшой дождь': ' 🌦 небольшой дождь',
            'сильный дождь': ' ⛈ сильный дождь',
            'дождь': ' 🌧 дождь',
        }
        return dict_weather[description_weather]

    except Exception:
        return description_weather


def get_geo_coordinates(user_id: int) -> Tuple[int, str, str]:
    """Считывание последних геокоординат User из БД."""
    return make_request(
        """ SELECT longitude, latitude, date_id
            FROM geolocation
            WHERE user_id=%s
            ORDER BY id DESC
            LIMIT 1;
        """,
        (user_id,),
        fetch='all'
    )[0]


def my_current_geoposition(message):
    """Вывод адреса местонахождения в группу."""
    coordinates = get_geo_coordinates(message.from_user.id)
    geo = f"{coordinates[0]},{coordinates[1]}"

    send_text = (
        "Согласно полученных геокоординат, "
        f"{message.from_user.first_name} находится:\n"
        f"[{get_address_from_coords(geo)}]"
        "(https://yandex.ru/maps/?whatshere[point]="
        f"{geo}&whatshere[zoom]=17&z=17)\n"
    )
    bot.send_message(CHAT_ID, send_text, parse_mode='Markdown')


def current_weather(message):
    """Вывод погоды по текущим геокоординатам."""
    coordinates = get_geo_coordinates(message.from_user.id)
    try:
        res = requests.get(
            "http://api.openweathermap.org/data/2.5/weather",
            params={
                'lat': coordinates[1],
                'lon': coordinates[0],
                'units': 'metric',
                'lang': 'ru',
                'APPID': OW_API_ID
            }
        )
        data = res.json()

        wind_directions = (
            "Сев",
            "Сев-Вост",
            "Вост",
            "Юго-Вост",
            "Южный",
            "Юго-Зап",
            "Зап",
            "Сев-Зап"
        )
        wind_speed = int(data['wind']['speed'])
        direction = int((wind_speed + 22.5) // 45 % 8)
        pressure = round(int(data['main']['pressure']*0.750063755419211))

        weather = [
            f" *{status_weather(data['weather'][0]['description'])}*",
            f" 💧 влажность: *{data['main']['humidity']}*%",
            f" 🌀 давление:   *{pressure}*мм рт.ст",
            f" 💨 ветер: *{wind_speed}м/сек ⤗ {wind_directions[direction]}*",
            f" 🌡 текущая: *{'{0:+3.0f}'.format(data['main']['temp'])}*°C",
            f" 🥶 мин:  *{'{0:+3.0f}'.format(data['main']['temp_min'])}*°C",
            f" 🥵 макс: *{'{0:+3.0f}'.format(data['main']['temp_max'])}*°C"
        ]

        st = "По данным ближайшего метеоцентра сейчас на улице:\n"
        max_len = max(len(x) for x in weather)
        for item in weather:
            st += f'{item.rjust(max_len, "~")}\n'

        bot.send_message(message.chat.id, st, parse_mode='Markdown')

    except Exception as error:
        logger.error(error, exc_info=True)


def weather_forecast(message):
    """Вывод прогноза погоды на 4 дня по последним User геокоординатам."""
    coordinates = get_geo_coordinates(message.from_user.id)

    try:
        res = requests.get(
            "http://api.openweathermap.org/data/2.5/forecast?",
            params={
                'lat': coordinates[1],
                'lon': coordinates[0],
                'units': 'metric',
                'lang': 'ru',
                'APPID': OW_API_ID
            }
        )
        data = res.json()

        time_zone = int(data['city']['timezone'])

        sunrise_time = datetime.utcfromtimestamp(
            int(data['city']['sunrise']) + time_zone
        )
        sunset_time = datetime.utcfromtimestamp(
            int(data['city']['sunset']) + time_zone
        )
        city = data['city']['name']
        text_weather = f"Прогноз в месте с названием\n*{city}*:\n"

        for record in range(0, 40, 8):
            temp_max_min_day = []
            temp_max_min_night = []

            date_j = data['list'][record]['dt_txt'][:10]
            text_weather += f"*{date_j}*\n".rjust(25, '~')

            description = status_weather(
                data['list'][record]['weather'][0]['description']
            )
            text_weather += f"*{description}*\n"

            for i in range(40):
                if (data['list'][i]['dt_txt'][:10]
                        == data['list'][record]['dt_txt'][:10]):

                    if (sunset_time.hour
                            > int(data['list'][i]['dt_txt'][11:13])
                            > sunrise_time.hour):

                        temp_max_min_day.append(
                            data['list'][i]['main']['temp_min']
                        )
                        temp_max_min_day.append(
                            data['list'][i]['main']['temp_max']
                        )
                    else:
                        temp_max_min_night.append(
                            data['list'][i]['main']['temp_min']
                        )
                        temp_max_min_night.append(
                            data['list'][i]['main']['temp_max']
                        )

            if len(temp_max_min_day) > 0:
                text_weather += (
                    f"🌡🌞 *{'{0:+3.0f}'.format(max(temp_max_min_day))}* "
                    f"... *{'{0:+3.0f}'.format(min(temp_max_min_day))}*°C\n"
                )

            if len(temp_max_min_night) > 0:
                text_weather += (
                    f"      🌙 *{'{0:+3.0f}'.format(max(temp_max_min_night))}* "
                    f"... *{'{0:+3.0f}'.format(min(temp_max_min_night))}*°C\n"
                )
            coeff_celsia = 0.750063755419211
            pressure_c = int(
                data['list'][record]['main']['pressure']*coeff_celsia
            )
            text_weather += f"давление *{pressure_c}*мм рт.ст\n"

        text_weather += "-\n".rjust(30, '-')
        text_weather += f"      ВОСХОД в *{sunrise_time.strftime('%H:%M')}*\n"
        text_weather += f"      ЗАКАТ     в *{sunset_time.strftime('%H:%M')}*"
        bot.send_message(message.chat.id, text_weather, parse_mode='Markdown')

    except Exception as error:
        logger.error(error, exc_info=True)


def get_distance(lat1, lon1, lat2, lon2):
    """
        Вычисляет расстояние в километрах между двумя точками,
        учитывая окружность Земли.
        https://en.wikipedia.org/wiki/Haversine_formula
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, (lon1, lat1, lon2, lat2))

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km
