import os
import telebot
import telebot.types as types
from dotenv import load_dotenv
import datetime
import pytz
import time
import logging
import schedule
import threading
import sys
import re
import pickle

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

load_dotenv()

token = os.getenv("TELEGRAM_TOKEN")
if token is None:
    raise ValueError("TELEGRAM_TOKEN is not set")

schedule_time = os.getenv("SCHEDULE_TIME")
if schedule_time is None or not re.match(r"^\d{2}:\d{2}$", schedule_time):
    logging.warning(f"Invalid schedule time: {schedule_time}, default to update year progress")
    schedule_time = ""

year_progress_cache = ""

tz = os.getenv("TZ")
if tz is None:
    logging.warning("TZ is not set, default to system time zone")

chat_id = os.getenv("TELEGRAM_CHAT_ID")
if chat_id is None:
    logging.warning("TELEGRAM_CHAT_ID is not set, messages will not be sent")

bot = telebot.TeleBot(token)

commands = [
    types.BotCommand("/status", "Show the current year progress"),
    types.BotCommand("/test", "Test send message"),
]
bot.set_my_commands(commands)

def is_leap_year(year: int) -> bool:
    if year % 4 != 0:
        return False
    elif year % 100 != 0:
        return True
    elif year % 400 != 0:
        return False
    else:
        return True

def get_year_progress() -> tuple[str, float]:
    if tz is None:
        current_date = datetime.datetime.now()
    else:
        unix_time = time.time()
        current_date = datetime.datetime.fromtimestamp(unix_time, tz=pytz.timezone(tz))
    year = current_date.year
    day_of_year = current_date.timetuple().tm_yday
    seconds_today = current_date.hour * 3600 + current_date.minute * 60 + current_date.second
    if is_leap_year(year):
        total_seconds = 366 * 24 * 3600
    else:
        total_seconds = 365 * 24 * 3600
    progress = (day_of_year - 1) * 24 * 3600 + seconds_today
    progress_percentage = (progress / total_seconds) * 100
    return current_date.strftime("%Y-%m-%d %H:%M:%S"), progress_percentage

def send_message() -> bool:
    msg_float = generate_progress_bar(get_year_progress()[1])[0]
    if chat_id is None:
        return False
    chat_id_list = chat_id.split(",")
    for id in chat_id_list:
        bot.send_message(id, msg_float)
    return True

def generate_progress_bar(percentage: float | int, length = os.getenv("PROGRESS_BAR_LENGTH")) -> tuple[str, str]:
    try:
        if length is None:
            length = 20
        else:
            length = int(length)
    except ValueError:
        logging.warning(f"Invalid progress bar length: {length}, default to 20")
        length = 20
    filled = int(length * percentage / 100)
    blank = length - filled
    bar = "▓" * filled + "░" * blank
    final_msg_float = f"{bar} - {percentage:.2f}%"
    final_msg_int = f"{bar} - {int(percentage)}%"
    return final_msg_float, final_msg_int

def check_year_progress():
    global year_progress_cache
    progress_percentage = get_year_progress()[1]
    final_msg_int = generate_progress_bar(progress_percentage)[1]

    def check_diff() -> str:
        with open("year_progress.cache", "wb") as f:
            pickle.dump(final_msg_int, f)
        if chat_id is None:
            return final_msg_int
        chat_id_list = chat_id.split(",")
        for id in chat_id_list:
            bot.send_message(id, f"{final_msg_int}")
        return final_msg_int
    
    if year_progress_cache != final_msg_int:
        year_progress_cache = check_diff()
    else:
        return

@bot.message_handler(commands=["status"])
def progress(message):
    date, progress_percentage = get_year_progress()
    final_msg = (
        f"Current time: {date}\n"
        f"Year progress: {progress_percentage}%\n" # 不要保留小数
    )
    if schedule_time == "":
        final_msg += "Next send year progress at: increase 1%"
    else:
        final_msg += f"Next send year progress at: {schedule_time}"
    bot.send_message(message.chat.id, f"{final_msg}")

@bot.message_handler(commands=["test"])
def test(message):
    success = send_message()
    if success:
        bot.send_message(message.chat.id, f"Test message sent.")
    else:
        bot.send_message(message.chat.id, f"Test message failed.")

def main_loop():
    global year_progress_cache
    if schedule_time == "":
        try:
            with open("year_progress.cache", "rb") as f:
                year_progress_cache = pickle.load(f)
        except FileNotFoundError:
            pass
        while True:
            check_year_progress()
            time.sleep(100)
    else:
        schedule.every().day.at(schedule_time).do(send_message) # type: ignore
        while True:
            schedule.run_pending()
            time.sleep(1)

def main():
    logging.info("YearProgressBot is running")
    bot.infinity_polling()

if __name__ == "__main__":
    threadtg = threading.Thread(target=main, daemon=True)
    threadtg.start()
    threadsc = threading.Thread(target=main_loop, daemon=True)
    threadsc.start()
    try:
        while threadsc.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("YearProgressBot is stopped")
        sys.exit(0)
