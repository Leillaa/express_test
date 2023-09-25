import os
import requests
import sqlite3
import time
from datetime import datetime, timezone
from dotenv import load_dotenv

from cities import cities_str

load_dotenv()
API_KEY = os.getenv("API_KEY")


def create_table(current_datetime):
    con = sqlite3.connect('weather_data/weather_data.db')
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS '%s' (
        city TEXT PRIMARY KEY, 
        temp REAL, 
        humidity INTEGER,
        pressure INTEGER );    
        """
        % current_datetime
        )
    con.commit()
    con.close()


def get_weather_data(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&appid={API_KEY}&units=metric"
    response = requests.get(url)
    return response.json()


def save_to_db(table_name, city, temp, humidity, pressure):
    con = sqlite3.connect('weather_data/weather_data.db')
    cur = con.cursor()
    cur.execute("INSERT INTO '%s' VALUES (?, ?, ?, ?)" % table_name, (city, temp, humidity, pressure))
    con.commit()
    con.close()


cities_list = sorted(cities_str.split())


while True:
    now = datetime.now(timezone.utc)
    current_datetime = now.strftime("%Y-%m-%d_%H:%M")
    create_table(current_datetime)
    try:
        for city in cities_list:
            data = get_weather_data(city).get('main')
            temp = data.get('temp')
            humidity = data.get('humidity')
            pressure = data.get('pressure')
            save_to_db(current_datetime, city, temp, humidity, pressure)
            print(f"Добавлен {city}")
        print("Данные успешно получены! Повторю через час")
        time.sleep(3600)  # Пауза на 1 час
    except Exception as e:
        print(f"Ошибка {e}, пробую снова, необходимо немного подождать")
        time.sleep(7)
        continue
