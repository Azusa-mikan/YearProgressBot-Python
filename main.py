import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.year_progress import check_year_progress
from src.config import schedule_time, tz
from src.telegram import bot, send_year_progress
from src.log import logger

async def main():
    scheduler = AsyncIOScheduler(timezone=tz)

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

    while True:
        try:
            await bot.polling(non_stop=True,skip_pending=True)
        except Exception:
            logger.exception("Error in polling")
            await asyncio.sleep(3)
        else:
            break

if __name__ == "__main__":
    asyncio.run(main())
