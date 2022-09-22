# -*- coding: utf-8 -*-
from functools import lru_cache
from fastapi import FastAPI
from time import time
import requests as req
import configparser as cp
import database
import json

app = FastAPI()
config = cp.ConfigParser()
config.read("settings.ini")

@lru_cache(maxsize=1)
def open_weather(city):
    print("Новый кэш")
    params = {
        'q': city,
        'appid': config["Settings"]["api_token"],
        'units': 'metric'
    }

    try:
        answer_openweather = req.post(
            url='https://api.openweathermap.org/data/2.5/weather',
            params=params
        )
        return answer_openweather.text, answer_openweather.status_code

    except Exception as ex:
        print(ex)
        return False, 503


def auxiliary_func(city, answer_openweather, status_code):
    if status_code == 200:
        answer_openweather = json.loads(answer_openweather)
        database.update_city_from_db(city, time(), json.dumps(answer_openweather))
    elif status_code == 503:
        answer_openweather = {"WARNING: 503 Server invalid!"}
    else:
        answer_openweather = {f"WARNING: status[{answer_openweather['cod']}] - {answer_openweather['message']}"}

    return answer_openweather


@app.get('/city={city}')
def get_user_item(city: str):
    city_data = database.get_city(city)
    if not city_data:
        print(f'Новый запрос для города: {city}')
        open_weather.cache_clear()
        answer_openweather, status_code = open_weather(city)
        answer_openweather = auxiliary_func(city, answer_openweather, status_code)
    else:
        print(f'Беру {city} из базы данных')
        if float((time() - city_data[1])/60) >= float(config["Settings"]["cache_time_min"]):
            print(f'Время города вышло, новый запрос для: {city}')
            open_weather.cache_clear()
            answer_openweather, status_code = open_weather(city)
            answer_openweather = auxiliary_func(city, answer_openweather, status_code)
        else:
            print(f'Возвращаю старый запрос для {city} так как он создался {((time() - city_data[1])/60)}с назад')
            answer_openweather = city_data[2]

    return answer_openweather


"""
if __name__ == "__main__":
    list_ = ['Novosibirsk', 'Barnaul', 'Moscow', 'Zarinsk', 'Moscow', 'Zarinsk']
    for city in list_:
        answer = get_user_item(city)
        print(f'*{city} - {answer}\n\n')
"""