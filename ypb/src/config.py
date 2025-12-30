import os
import re
import pytz
from dotenv import load_dotenv
from pathlib import Path
from ypb.src.log import logger

env_path = Path(__file__).parents[2] / ".env"

load_dotenv(env_path)

token = os.getenv("TELEGRAM_TOKEN")
if not token:
    raise ValueError("TELEGRAM_TOKEN is not set")

schedule_time = os.getenv("SCHEDULE_TIME")
if not schedule_time or not re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", schedule_time):
    logger.warning(f"Invalid schedule time: {schedule_time}, default to update year progress")
    schedule_time = ""

tz_env = os.getenv("TZ")
if not tz_env:
    logger.warning("TZ is not set, default to system time zone")
    tz = None
else:
    try:
        tz = pytz.timezone(tz_env)
    except pytz.UnknownTimeZoneError:
        logger.warning(f"Unknown time zone: {tz_env}, default to system time zone")
        tz = None

chat_id = os.getenv("TELEGRAM_CHAT_ID")
if not chat_id:
    logger.warning("TELEGRAM_CHAT_ID is not set, messages will not be sent")

admin_id = os.getenv("TELEGRAM_ADMIN_ID")
if not admin_id:
    logger.warning("TELEGRAM_ADMIN_ID is not set, admin commands will not be available")

try:
    progress_bar_length = int(os.getenv("PROGRESS_BAR_LENGTH")) # type: ignore
except Exception:
    logger.warning(f"Invalid progress bar length: {os.getenv('PROGRESS_BAR_LENGTH')}, default to 20")
    progress_bar_length = 20
