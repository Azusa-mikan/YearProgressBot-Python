import datetime
import time
import pytz
import pickle
from .config import tz, progress_bar_length, chat_id
from .log import logger

year_progress_cache = ""

def is_leap_year(year: int) -> bool:
    """
    判断是否为闰年
    返回：True 闰年 False 非闰年
    """
    if year % 4 != 0:
        return False
    elif year % 100 != 0:
        return True
    elif year % 400 != 0:
        return False
    else:
        return True

async def get_year_progress() -> tuple[str, float]:
    """
    获取当前年份的进度
    返回：(当前日期时间字符串，当前年份进度百分比)
    """
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

async def generate_progress_bar(percentage: float | int, length = progress_bar_length) -> tuple[str, str]:
    """
    根据百分比生成进度条字符串
    返回：(带两位小数的进度条字符串，取整后的进度条字符串)
    """
    filled = int(length * percentage / 100)
    blank = length - filled
    bar = "▓" * filled + "░" * blank
    final_msg_float = f"{bar} - {percentage:.2f}%"
    final_msg_int = f"{bar} - {int(percentage)}%"
    return final_msg_float, final_msg_int

async def check_year_progress():
    """
    检查年份进度是否有变化（按整数百分比）
    当进度整数部分变化时，才发送消息，避免刷屏
    """
    global year_progress_cache
    _, progress_percentage = await get_year_progress()
    _, final_msg_int = await generate_progress_bar(progress_percentage)

    async def check_diff() -> str:
        """把当前进度缓存到本地文件，并发送到 Telegram"""
        with open("year_progress.cache", "wb") as f:
            pickle.dump(final_msg_int, f)
        return final_msg_int
    
    if year_progress_cache != final_msg_int:
        year_progress_cache = await check_diff()
    else:
        return