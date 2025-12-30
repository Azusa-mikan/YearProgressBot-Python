import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ypb.src.telegrambot import TelegramBot, yp
from ypb.src.config import schedule_time, tz

tg_bot = TelegramBot()

async def send_year_progress() -> None:
    bar, progress = await yp.progress_bar()
    progress_percent = round(progress, 2)
    progress_int = int(progress)
    if progress_int == 0:
        final_msg = f"{bar} - {progress_percent}%\nHappy New Year!"
    else:
        final_msg = f"{bar} - {progress_percent}%"
    await tg_bot.send_message(final_msg)

async def check_year_progress() -> None:
    bar, progress = await yp.progress_bar()
    progress_int = int(progress)
    if progress_int == 0:
        final_msg = f"{bar} - {progress_int}%\nHappy New Year!"
    else:
        final_msg = f"{bar} - {progress_int}%"
    if await yp.check_change_year_progress():
        await tg_bot.send_message(final_msg)

async def main() -> None:
    scheduler = AsyncIOScheduler(timezone=tz)

    if not schedule_time:
        scheduler.add_job(
            check_year_progress,
            "interval",
            seconds=5,
            max_instances=1,
            misfire_grace_time=90,
            coalesce=True,
        )
    else:
        hour, minute = map(int, schedule_time.split(":"))
        scheduler.add_job(
            send_year_progress,
            "cron",
            hour=hour,
            minute=minute,
            max_instances=1,
            coalesce=True
        )

    scheduler.start()

    try:
        await tg_bot.start_bot()
    finally:
        scheduler.shutdown()
        await tg_bot.stop_bot()

if __name__ == "__main__":
    asyncio.run(main())
