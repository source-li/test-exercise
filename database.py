# -*- coding: utf-8 -*-
import sqlite3
import configparser as cp

config = cp.ConfigParser()
config.read("settings.ini")
database_path = config["Settings"]["database_path"]


def connect_db():
    connect = sqlite3.connect(database_path)
    cursor = connect.cursor()
    return connect, cursor


def update_city_from_db(city, update_date, data):
    conn, cursor = connect_db()
    if not get_city(city):
        cursor.execute("INSERT INTO weather VALUES(?, ?, ?);", (city, update_date, data))
    else:
        cursor.execute("UPDATE weather SET update_date=?, data=? WHERE city=?", (update_date, data, city))
    conn.commit()


def get_full_db():
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM weather")
    exist = cursor.fetchone()
    conn.commit()
    if not exist:
        return False
    else:
        return exist


def get_city(city):
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM weather WHERE city=?", (city,))
    exist = cursor.fetchone()
    conn.commit()
    if not exist:
        return False
    else:
        return exist


def create_db():
    conn, cursor = connect_db()
    cursor.execute("""CREATE TABLE if not exists weather(
            city TEXT,
            update_date REAL,
            data TEXT
        )""")
    conn.commit()


create_db()
