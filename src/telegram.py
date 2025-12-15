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

async def send_message() -> bool:
    """向配置的 chat_id（可以是多个）发送当前年份进度条"""
    # 异步获取当前年份进度
    _, progress_percentage = await get_year_progress()
    msg_float, _ = await generate_progress_bar(progress_percentage)
    if chat_id is None:
        return False
    chat_id_list = chat_id.split(",")
    # 并行发送消息
    tasks = [bot.send_message(id, msg_float) for id in chat_id_list]
    await asyncio.gather(*tasks)
    logger.debug(f"Sent message to {chat_id_list}")
    return True  # 只要逻辑执行到这里，就认为发送动作成功触发

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
    if schedule_time == "":
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
    