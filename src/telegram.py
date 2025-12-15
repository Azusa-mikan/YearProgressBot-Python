import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from .log import logger
from .config import token, schedule_time, admin_id, chat_id
from .year_progress import get_year_progress, generate_progress_bar

bot = AsyncTeleBot(token)
commands = [
    types.BotCommand("/status", "Show the current year progress"),
    types.BotCommand("/test", "Test send message"),
]

bot.set_my_commands(commands)

async def send_message(msg: str) -> bool:
    """向配置的 chat_id（可以是多个）发送当前年份进度条"""
    if not chat_id:
        return False
    chat_id_list = chat_id.split(",")
    # 并行发送消息
    tasks = [bot.send_message(id, msg) for id in chat_id_list]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # 检查是否有异常
    for chatid, result in zip(chat_id_list, results):
        if isinstance(result, Exception):
            logger.error(f"Error sending message to {chatid}: {result}")
        else:
            logger.debug(f"Successfully sent message to {chatid}")
    return True  # 只要逻辑执行到这里，就认为发送动作成功触发

async def send_year_progress():
    """
    发送当前年份进度条
    """
    _, progress_percentage = await get_year_progress()
    msg_float, _ = await generate_progress_bar(progress_percentage)
    await send_message(msg_float)

@bot.message_handler(commands=["status"])
async def progress_status(message):
    """
    处理 /status 命令，返回当前时间和年份进度
    """
    date, progress_percentage = await get_year_progress()
    final_msg = (
        f"Current time: {date}\n"
        f"Year progress: {progress_percentage}%\n"
    )
    if not schedule_time:
        final_msg += "Next send year progress at: increase 1%"
    else:
        final_msg += f"Next send year progress at: {schedule_time}"
    await bot.send_message(message.chat.id, f"{final_msg}")

@bot.message_handler(commands=["test"])
async def test(message):
    """
    处理 /test 命令，测试发送一次当前进度（需要管理员）
    """
    if str(message.from_user.id) != admin_id:
        await bot.send_message(message.chat.id, "You are not authorized to use this command.")
        return
    if await send_message("Test message"):
        await bot.send_message(message.chat.id, "Test message sent successfully.")
    else:
        await bot.send_message(message.chat.id, "Test message failed to send.")

