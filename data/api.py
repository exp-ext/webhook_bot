import time
from datetime import date as dt
from datetime import datetime, timedelta
from math import asin, cos, radians, sin, sqrt

import requests
from settings import bot, logger

from data.geoservice import get_geo_coordinates


def get_cat_image(message):
    try:
        url = 'https://api.thecatapi.com/v1/images/search'
        response = requests.get(url)
    except Exception as error:
        logger.error(error, exc_info=True)
        url = 'https://randomfox.ca/floof/'
        response = requests.get(url)

    response = response.json()
    random_cat = response[0].get('url')
    bot.send_photo(message.chat.id, random_cat)


def haversine(lat1, lon1, lat2, lon2):
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


def find_closest_lat_lon(data, v):
    try:
        return min(
            data,
            key=lambda p: haversine(p['lat'], p['lon'], v['lat'], v['lon'])
        )
    except TypeError as error:
        logger.error(error, exc_info=True)


def where_to_go(message):
    """Опрос api kudago.com с формированием списка событий."""
    try:
        date_today_int = dt.today()

        date_yesterday = date_today_int - timedelta(days=1)
        date_yesterday = time.mktime(date_yesterday.timetuple())

        date_tomorrow = date_today_int + timedelta(days=1)
        date_tomorrow = time.mktime(date_tomorrow.timetuple())

        city_list = requests.get(
            'https://kudago.com/public-api/v1.2/locations/?',
            {
                'lang': 'ru',
                'fields': 'slug,name,coords',
            }
        ).json()
        city_geo_list = []
        for city in city_list:
            if city['coords']['lat']:
                city_geo_list.append(city['coords'])

        coordinates = get_geo_coordinates(message.from_user.id)
        current_geo = {
            'lat': float(coordinates[1]),
            'lon': float(coordinates[0])
        }
        nearest_city_geo = find_closest_lat_lon(city_geo_list, current_geo)

        for city in city_list:
            if city['coords'] == nearest_city_geo:
                nearest_city = city['slug']
                city_name = city['name']

        resp = requests.get(
            'https://kudago.com/public-api/v1.4/events/',
            {
                'actual_since': date_yesterday,
                'actual_until': date_tomorrow,
                'location': nearest_city,
                'is_free': True,
            }
        )

        next_data = resp.json()

        date_today = datetime.strftime(date_today_int, '%Y-%m-%d')
        text = (
            '[BCЕ МЕРОПРИЯТИЯ НА СЕГОДНЯ \n'
            f'в ближайшем от Вас городе {city_name}]'
            '(https://kudago.com/spb/festival/'
            f'?date={date_today}&hide_online=y&only_free=y)\n\n'
        )
        # лист с рекламмой
        excluded_list = ['197880', '198003', '187745', '187466', '187745']

        for item in next_data['results']:
            if item['id'] not in excluded_list:
                text += (
                    f"- {item['title'].capitalize()} [>>>]"
                    f"(https://kudago.com/spb/event/{item['slug']}/)\n"
                )
                text += '-------------\n'

        bot.send_message(message.chat.id, text, parse_mode='Markdown')

    except Exception as error:
        logger.error(error, exc_info=True)


# def data_numbers_api(date):
#     listdate = date.split('.')
#     url = f'http://numbersapi.com/{listdate[1]}/{listdate[0]}/date'
