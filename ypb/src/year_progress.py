import datetime
import pickle
from datetime import tzinfo

class YearProgress:
    def __init__(
            self,
            tz: tzinfo | None = None,
            bar_length: int = 20
        ) -> None:
        self.tz: tzinfo | None = tz
        self.bar_length: int = bar_length
        self.year_progress_cache: tuple[str, float] = self._year_progress_cache
    
    @property
    def _year_progress_cache(self) -> tuple[str, float]:
        """
        获取年份进度缓存
        返回：缓存元组 (进度条 进度百分比)
        """
        try:
            with open("year_progress.cache", "rb") as f:
                year_progress_cache = pickle.load(f)
        except FileNotFoundError:
            year_progress_cache = ("", 0.0)
        return year_progress_cache

    def is_leap_year(self, year: int) -> bool:
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

    async def progress(self) -> float:
        """
        返回当前年份的进度的百分比（0-100）
        """
        now = datetime.datetime.now(tz=self.tz)
        day_of_year = now.timetuple().tm_yday
        seconds_today = now.hour * 3600 + now.minute * 60 + now.second
        year = now.year
        if self.is_leap_year(year):
            total_seconds = 366 * 24 * 3600
        else:
            total_seconds = 365 * 24 * 3600
        progress_seconds = (day_of_year - 1) * 24 * 3600 + seconds_today
        return (progress_seconds / total_seconds) * 100

    async def progress_bar(self) -> tuple[str, float]:
        """
        返回当前年份的进度条和进度
        """
        progress = await self.progress()
        filled = int(self.bar_length * progress / 100)
        blank = self.bar_length - filled
        bar = "▓" * filled + "░" * blank
        return bar, progress

    async def _save_year_progress_cache(self, bar: str, progress: float) -> None:
        """
        保存年份进度缓存
        """
        with open("year_progress.cache", "wb") as f:
            pickle.dump((bar, progress), f)
        self.year_progress_cache = bar, progress

    async def check_change_year_progress(self) -> bool:
        """
        检查年份进度是否有变化（按整数百分比）
        返回：True 有变化 False 无变化
        """
        bar, progress = await self.progress_bar()
        progress_int = int(progress)
        _, cached_progress = self.year_progress_cache
        cached_progress_int = int(cached_progress)
        if progress_int != cached_progress_int:
            await self._save_year_progress_cache(bar, progress)
            return True
        return False
