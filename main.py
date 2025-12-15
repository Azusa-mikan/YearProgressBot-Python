import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.year_progress import check_year_progress
from src.config import schedule_time
from src.telegram import bot, send_year_progress

async def main():
    scheduler = AsyncIOScheduler()

    if not schedule_time:
        scheduler.add_job(
            check_year_progress,
            "interval",
            seconds=100,
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

    await bot.polling()

if __name__ == "__main__":
    asyncio.run(main())
