import os
import telebot
from dotenv import load_dotenv
import datetime
import pytz
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

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

def get_year_progress() -> float:
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
    progress = (day_of_year / days_in_year) * 100
    return progress

def generate_progress_bar(percentage, length=20):
    filled = int(length * percentage / 100)
    blank = length - filled
    bar = "▓" * filled + "░" * blank
    return f"{bar} {int(percentage)}%"

def send_message(msg: str):
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if chat_id is None:
        raise ValueError("TELEGRAM_CHAT_ID is not set")
    chat_id_list = chat_id.split(",")
    for id in chat_id_list:
        bot.send_message(id, msg)

@bot.message_handler(commands=["get"])
def progress(message):
    progress = get_year_progress()
    progress_bar = generate_progress_bar(progress)
    bot.send_message(message.chat.id, f"{progress_bar}")

if __name__ == "__main__":
    logging.info("YearProgressBot is running")
    bot.infinity_polling()

