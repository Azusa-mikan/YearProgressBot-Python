from telebot.async_telebot import AsyncTeleBot
from telebot import types
import asyncio
from datetime import datetime
from ypb.src.log import logger
from ypb.src.config import token, schedule_time, admin_id, chat_id, tz, progress_bar_length
from ypb.src.year_progress import YearProgress

yp = YearProgress(tz=tz, bar_length=progress_bar_length)

class TelegramBot:
    def __init__(self):
        self.bot = AsyncTeleBot(token)  # type: ignore
        self.commands = [
            types.BotCommand("/status", "Show the current year progress"),
            types.BotCommand("/test", "Test send message"),
        ]
        self.bot.register_message_handler(self._progress_status, commands=["status"])
        self.bot.register_message_handler(self._test, commands=["test"])

    async def start_bot(self) -> None:
        """
        运行 Telegram 机器人
        """
        logger.info("Running Telegram bot")
        await self.bot.set_my_commands(self.commands)
        while True:
            try:
                await self.bot.polling()
            except Exception as e:
                logger.error(f"Telegram bot polling error: {e}")
                await asyncio.sleep(3)  # 等待 3 秒后重试
            else:
                break
    
    async def send_message(self, msg: str) -> bool:
        """向配置的 chat_id（可以是多个）发送消息"""
        if not chat_id:
            logger.warning("chat_id is not set")
            return False
        chat_id_list = chat_id.split(",")
        # 并行发送消息
        tasks = [self.bot.send_message(id, msg) for id in chat_id_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # 检查是否有异常
        for chatid, result in zip(chat_id_list, results):
            if isinstance(result, Exception):
                logger.error(f"Error sending message to {chatid}: {result}")
            else:
                logger.debug(f"Successfully sent message to {chatid}")
        return True  # 只要逻辑执行到这里，就认为发送动作成功触发

    async def _progress_status(self, message):
        """
        处理 /status 命令，返回当前时间和年份进度
        """
        _, progress_percentage = await yp.progress_bar()
        final_msg = (
            f"Current time: {datetime.now(tz=tz).strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
            f"Year progress: {progress_percentage}%\n"
        )
        if not schedule_time:
            final_msg += "Next send year progress at: increase 1%"
        else:
            final_msg += f"Next send year progress at: {schedule_time}"
        await self.bot.send_message(message.chat.id, f"{final_msg}")

    async def _test(self, message):
        """
        处理 /test 命令，测试发送一次当前进度（需要管理员）
        """
        if str(message.from_user.id) != admin_id:
            await self.bot.send_message(message.chat.id, "You are not authorized to use this command.")
            return
        if await self.send_message("Test message"):
            await self.bot.send_message(message.chat.id, "Test message sent successfully.")
        else:
            await self.bot.send_message(message.chat.id, "Test message failed to send.")

    async def stop_bot(self) -> None:
        """
        停止 Telegram 机器人
        """
        logger.info("Stopping Telegram bot")
        await self.bot.close_session()