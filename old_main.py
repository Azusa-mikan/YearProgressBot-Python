import os  # 操作系统相关功能（读取环境变量等）
import telebot  # Telegram 机器人主库
import telebot.types as types  # Telegram 机器人相关类型（命令等）
from dotenv import load_dotenv  # 从 .env 文件中加载环境变量
import datetime  # 处理日期和时间
import pytz  # 处理时区
import time  # 时间相关函数（时间戳、sleep 等）
import logging  # 日志模块
import schedule  # 定时任务调度库
import threading  # 多线程
import sys  # 退出程序等
import re  # 正则表达式
import pickle  # 序列化缓存到文件

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
# 配置基础日志格式和日志等级

load_dotenv()  # 从 .env 文件中加载环境变量

token = os.getenv("TELEGRAM_TOKEN")  # Telegram 机器人 Token
if token is None:
    raise ValueError("TELEGRAM_TOKEN is not set")  # 必须配置 Token，没配置就直接报错

schedule_time = os.getenv("SCHEDULE_TIME")  # 每天定时发送的时间，例如 "09:00"
if schedule_time is None or not re.match(r"^\d{2}:\d{2}$", schedule_time):
    # 未设置或格式错误（不是 HH:MM）则退回到“按进度变化发送”的模式
    logging.warning(f"Invalid schedule time: {schedule_time}, default to update year progress")
    schedule_time = ""  # 为空表示按进度变动（每增加 1% 时）发送

year_progress_cache = ""  # 用于缓存最近一次发送的整型进度条字符串

tz = os.getenv("TZ")  # 例如 "Asia/Shanghai" 等
if tz is None:
    # 如果没设置 TZ，就使用系统本地时区
    logging.warning("TZ is not set, default to system time zone")

chat_id = os.getenv("TELEGRAM_CHAT_ID")  # 可以是单个 chat id，也可以是用逗号分隔的多个 chat id
if chat_id is None:
    # 没配置 chat id 的话，机器人就不知道发给谁，只能打印警告
    logging.warning("TELEGRAM_CHAT_ID is not set, messages will not be sent")

bot = telebot.TeleBot(token)  # 创建 Telegram 机器人实例

commands = [
    # /status 命令：查看当前年份进度
    types.BotCommand("/status", "Show the current year progress"),
    # /test 命令：测试群发/私发消息是否正常
    types.BotCommand("/test", "Test send message"),
]
bot.set_my_commands(commands)  # 在 Telegram 中设置机器人的命令菜单

def is_leap_year(year: int) -> bool:
    # 判断某年是否为闰年
    if year % 4 != 0:
        return False
    elif year % 100 != 0:
        return True
    elif year % 400 != 0:
        return False
    else:
        return True

def get_year_progress() -> tuple[str, float]:
    # 计算当前时间在本年中所占的百分比（精确到秒）
    if tz is None:
        # 如果没有指定时区，就使用系统当前时间
        current_date = datetime.datetime.now()
    else:
        # 指定了时区，则使用该时区的当前时间
        unix_time = time.time()
        current_date = datetime.datetime.fromtimestamp(unix_time, tz=pytz.timezone(tz))
    year = current_date.year  # 当前年份
    day_of_year = current_date.timetuple().tm_yday  # 今天是本年的第几天（1~365/366）
    # 今天从 00:00 到现在已经过去的秒数
    seconds_today = current_date.hour * 3600 + current_date.minute * 60 + current_date.second
    if is_leap_year(year):
        total_seconds = 366 * 24 * 3600  # 闰年总秒数
    else:
        total_seconds = 365 * 24 * 3600  # 平年总秒数
    # 从年初 00:00 到当前时间的总秒数
    progress = (day_of_year - 1) * 24 * 3600 + seconds_today
    # 计算当前进度对应的百分比
    progress_percentage = (progress / total_seconds) * 100
    # 返回（当前时间字符串，年份进度百分比）
    return current_date.strftime("%Y-%m-%d %H:%M:%S"), progress_percentage

def send_message() -> bool:
    # 向配置的 chat_id（可以是多个）发送当前年份进度条
    msg_float = generate_progress_bar(get_year_progress()[1])[0]  # 使用保留两位小数的进度条
    if chat_id is None:
        # 没有配置 chat id，发送失败
        return False
    chat_id_list = chat_id.split(",")  # 支持多个 chat id，用逗号分隔
    for id in chat_id_list:
        bot.send_message(id, msg_float)  # 向每个 chat 发送同一条消息
    return True  # 只要逻辑执行到这里，就认为发送动作成功触发

def generate_progress_bar(percentage: float | int, length = os.getenv("PROGRESS_BAR_LENGTH")) -> tuple[str, str]:
    # 根据百分比生成进度条字符串
    # 返回：(带两位小数的进度条字符串，取整后的进度条字符串)
    try:
        if length is None:
            length = 20  # 默认进度条长度为 20
        else:
            length = int(length)  # 从环境变量中读取并转为整数
    except ValueError:
        # 如果读取的长度非法，则回退到默认值 20
        logging.warning(f"Invalid progress bar length: {length}, default to 20")
        length = 20
    filled = int(length * percentage / 100)  # 已完成的格子数
    blank = length - filled  # 未完成的格子数
    bar = "▓" * filled + "░" * blank  # 使用方块字符绘制进度条
    final_msg_float = f"{bar} - {percentage:.2f}%"  # 保留两位小数
    final_msg_int = f"{bar} - {int(percentage)}%"  # 只取整数部分
    return final_msg_float, final_msg_int

def check_year_progress():
    # 检查年份进度是否有变化（按整数百分比）
    # 当进度整数部分变化时，才发送消息，避免刷屏
    global year_progress_cache
    progress_percentage = get_year_progress()[1]  # 当前百分比（浮点）
    final_msg_int = generate_progress_bar(progress_percentage)[1]  # 只取整数显示的进度条字符串

    def check_diff() -> str:
        # 把当前进度缓存到本地文件，并发送到 Telegram
        with open("year_progress.cache", "wb") as f:
            pickle.dump(final_msg_int, f)
        if chat_id is None:
            # 没配置 chat id，只是更新本地缓存
            return final_msg_int
        chat_id_list = chat_id.split(",")
        for id in chat_id_list:
            bot.send_message(id, f"{final_msg_int}")  # 向每个 chat 发送消息
        return final_msg_int
    
    if year_progress_cache != final_msg_int:
        # 只有当当前进度和缓存不一致时，才触发发送（即进度整数部分发生变化）
        year_progress_cache = check_diff()
    else:
        # 没变化就什么都不做
        return

@bot.message_handler(commands=["status"])
def progress(message):
    # 处理 /status 命令，返回当前时间和年份进度
    date, progress_percentage = get_year_progress()
    final_msg = (
        f"Current time: {date}\n"
        f"Year progress: {progress_percentage}%\n"  # 这里保留原始浮点（如果想只显示整数可以再处理）
    )
    # 根据是否配置 schedule_time，提示下一次发送时间的模式
    if schedule_time == "":
        final_msg += "Next send year progress at: increase 1%"
    else:
        final_msg += f"Next send year progress at: {schedule_time}"
    bot.send_message(message.chat.id, f"{final_msg}")

@bot.message_handler(commands=["test"])
def test(message):
    # 处理 /test 命令，测试发送一次当前进度
    success = send_message()
    if success:
        bot.send_message(message.chat.id, f"Test message sent.")
    else:
        bot.send_message(message.chat.id, f"Test message failed.")

def main_loop():
    # 第二个线程的主循环：负责定时检查或发送年份进度
    global year_progress_cache
    if schedule_time == "":
        # 如果没有设置固定时间，就按“每增加 1% 时发送”的模式
        try:
            with open("year_progress.cache", "rb") as f:
                year_progress_cache = pickle.load(f)  # 读取上一次缓存的进度
        except FileNotFoundError:
            # 第一次运行时缓存文件可能不存在，忽略异常
            pass
        while True:
            check_year_progress()  # 检查进度是否有变化
            time.sleep(100)  # 每 100 秒检查一次
    else:
        # 如果配置了固定时间，就每天在指定时间发送一次
        schedule.every().day.at(schedule_time).do(send_message)  # type: ignore
        while True:
            schedule.run_pending()  # 运行到期的任务
            time.sleep(1)  # 每秒检查一次

def main():
    # 第一个线程的主函数：启动 Telegram 机器人轮询
    logging.info("YearProgressBot is running")
    bot.infinity_polling()  # 无限轮询接收消息

if __name__ == "__main__":
    # 程序入口：启动两个后台线程
    # 1. Telegram 机器人消息轮询线程
    threadtg = threading.Thread(target=main, daemon=True)
    threadtg.start()
    # 2. 定时发送/检查年份进度的线程
    threadsc = threading.Thread(target=main_loop, daemon=True)
    threadsc.start()
    try:
        # 主线程只负责“挂起”等待，保持程序不退出
        while threadsc.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        # 捕获 Ctrl+C，优雅地退出程序
        logging.info("YearProgressBot is stopped")
        sys.exit(0)
