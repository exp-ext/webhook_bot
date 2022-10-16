import time
from datetime import date as dt
from datetime import datetime, timedelta

import requests
from data.exceptions import BedRequestError
from settings import bot, logger

from data.geoservice import get_geo_coordinates, get_distance


def get_cat_image(message):
    try:
        url = 'https://api.thecatapi.com/v1/images/search'
        response = requests.get(url).json()
    except Exception as error:
        logger.error(error, exc_info=True)

    random_cat = response[0].get('url')

    bot.send_photo(message.chat.id, random_cat)


def find_closest_lat_lon(data, v):
    try:
        return min(
            data,
            key=lambda p: get_distance(p['lat'], p['lon'], v['lat'], v['lon'])
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

        categories = (
            'yarmarki-razvlecheniya-yarmarki,festival,'
            'entertainment,exhibition,holiday,kids'
        )
        try:
            response = requests.get(
                'https://kudago.com/public-api/v1.4/events/',
                {
                    'actual_since': date_yesterday,
                    'actual_until': date_tomorrow,
                    'location': nearest_city,
                    'is_free': True,
                    'categories': categories,
                }
            )
        except requests.exceptions.ConnectionError as error:
            raise logger.error('Ошибка подключения:', error)
        except requests.exceptions.InvalidJSONError as error:
            raise logger.error('Произошла ошибка JSON', error)
        except requests.exceptions.RequestException as error:
            raise logger.error(error)

        if response.status_code != 200:
            rise_msg = (
                'Эндпоинт kudago.com недоступен. '
                'Код ответа API: '
            )
            logger.error(f'{rise_msg} {response.status_code}')
            raise BedRequestError(rise_msg, response)

        next_data = response.json()

        date_today = datetime.strftime(date_today_int, '%Y-%m-%d')
        text = (
            '[BCЕ МЕРОПРИЯТИЯ НА СЕГОДНЯ \n'
            f'в ближайшем от Вас городе {city_name}]'
            '(https://kudago.com/spb/festival/'
            f'?date={date_today}&hide_online=y&only_free=y)\n\n'
        )

        for item in next_data['results']:
            text += (
                f"- {item['title'].capitalize()} [>>>]"
                f"(https://kudago.com/spb/event/{item['slug']}/)\n"
            )
            text += '-------------\n'

        bot.send_message(message.chat.id, text, parse_mode='Markdown')

    except Exception as error:
        logger.error(error, exc_info=True)
