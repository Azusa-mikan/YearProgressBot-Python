import os
import re
from dotenv import load_dotenv
from .log import logger

load_dotenv()

token = os.getenv("TELEGRAM_TOKEN")
if token is None:
    raise ValueError("TELEGRAM_TOKEN is not set")

schedule_time = os.getenv("SCHEDULE_TIME")
if schedule_time is None or not re.match(r"^\d{2}:\d{2}$", schedule_time):
    logger.warning(f"Invalid schedule time: {schedule_time}, default to update year progress")
    schedule_time = ""

tz = os.getenv("TZ")
if tz is None:
    logger.warning("TZ is not set, default to system time zone")

chat_id = os.getenv("TELEGRAM_CHAT_ID")
if chat_id is None:
    logger.warning("TELEGRAM_CHAT_ID is not set, messages will not be sent")

admin_id = os.getenv("TELEGRAM_ADMIN_ID")
if admin_id is None:
    logger.warning("TELEGRAM_ADMIN_ID is not set, admin commands will not be available")

try:
    progress_bar_length = int(os.getenv("PROGRESS_BAR_LENGTH"))
except Exception:
    logger.warning(f"Invalid progress bar length: {os.getenv('PROGRESS_BAR_LENGTH')}, default to 20")
    progress_bar_length = 20
