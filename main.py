import os
import telebot
from dotenv import load_dotenv
import datetime
import pytz
import time

load_dotenv()

token = os.getenv("TELEGRAM_TOKEN")
if token is None:
    raise ValueError("TELEGRAM_TOKEN is not set")

bot = telebot.TeleBot(token)

def is_leap_year(year: int) -> bool:
    if year % 4 != 0:
        return False
    elif year % 100 != 0:
        return True
    elif year % 400 != 0:
        return False
    else:
        return True

def get_year_progress():
    tz = os.getenv("TZ")
    if tz is None:
        current_date = datetime.datetime.now()
    else:
        unix_time = time.time()
        current_date = datetime.datetime.fromtimestamp(unix_time, tz=pytz.timezone(tz))
    year = current_date.year
    day_of_year = current_date.timetuple().tm_yday
    if is_leap_year(year):
        days_in_year = 366
    else:
        days_in_year = 365
    progress = int((day_of_year / days_in_year) * 100)
    return progress



def send_message(msg: str):
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if chat_id is None:
        raise ValueError("TELEGRAM_CHAT_ID is not set")
    chat_id_list = chat_id.split(",")
    for id in chat_id_list:
        bot.send_message(id, msg)
