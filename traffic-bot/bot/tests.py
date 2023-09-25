import unittest
from .bot import Bot
import datetime as dt


class TestBot(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def check_result_24f(self, time: int) -> None:
        bot = Bot("", 24)
        keys = list(bot.data.keys())
        _time = dt.datetime(year=1970, month=1, day=1, hour=time)
        key = bot._find_index(_time)
        value = keys[key]
        time_to_str = f"{time}:00" if len(str(time)) == 2 else f"0{time}:00"        
        self.assertEqual(value, time_to_str)

    def check_result_12f(self, time: int) -> None:
        bot = Bot("", 12)
        keys = list(bot.data.keys())
        _time = dt.datetime(year=1970, month=1, day=1, hour=time)
        key = bot._find_index(_time)
        value = keys[key]
        if time < 12:
            mid = 'AM'
        else:
            mid = 'PM'
            time = time - 12
        time_to_str = f"{time}:00 {mid}" if len(str(time)) == 2 else f"0{time}:00 {mid}"        
        self.assertEqual(value, time_to_str)

    def test_get_time(self) -> None:
        for i in range(24):
            self.check_result_24f(i)

        for i in range(1, 11):
            self.check_result_12f(i)
