import time
import datetime as dt
from logger import get_color
from core import (
    log,
    _Data,
    _TimeFormat,
    TimeFormatError,
)
from praw.reddit import (  # type: ignore
    Reddit,
)

__all__ = (
    "Bot",
    "TimeFormatError",
)


class Bot:
    def __init__(self, reddit: Reddit, time_format: _TimeFormat) -> None:
        self.reddit = reddit
        self.data = self._init_data(time_format)
        self.time_format = time_format

    def _init_data(self, time_format: _TimeFormat) -> _Data:
        data: _Data = {}
        if time_format == 12:
            for i in range(1, 13):
                num = str(i)
                time = "%s:00 PM" % (num if len(num) == 2 else f"0{num}")
                data[time] = []
            for i in range(1, 13):
                num = str(i)
                time = "%s:00 AM" % (num if len(num) == 2 else f"0{num}")
                data[time] = []
        elif time_format == 24:
            for i in range(24):
                num = str(i)
                time = "%s:00" % (num if len(num) == 2 else f"0{num}")
                data[time] = []
        else:
            raise TimeFormatError(
                f"Invalid time format '{time_format}'. Valid options: 12, 24"
            )

        return data

    def _find_index(self, time: dt.datetime) -> int:
        if self.time_format == 12:
            index = time.hour - 13  # 12 for the hour and 1 for 0 based index
        elif self.time_format == 24:
            index = time.hour
        return index

    def harvest(self, sub_name: str, cicles: int, minute: int) -> None:
        log.success(f"Connected to subreddit '{sub_name}'")
        keys = list(self.data.keys())
        total = 0

        while True:
            sub = self.reddit.subreddit(sub_name)
            time_now = dt.datetime.now()
            minutes = time_now.minute
            if minutes == minute:
                active_users = sub.active_user_count
                if self.time_format == 12:
                    key = keys[self._find_index(time_now)]
                else:
                    key = keys[self._find_index(time_now)]
                log.info(f"Added result for {key}")
                self.data[key].append(active_users)

                total += 1
                log.success(f"Cicle finished. {total}/{cicles}")

            if total == cicles:
                break

            time.sleep(60)
