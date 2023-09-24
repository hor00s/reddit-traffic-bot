import unittest
from .bot import Bot
import datetime as dt


class TestBot(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_get_time(self) -> None:
        bot = Bot("", 24)
        keys = list(bot.data.keys())
        time = dt.datetime(year=1970, month=1, day=1, hour=5)
        key = bot._find_index(time)
        value = keys[key]
        self.assertEqual(value, "05:00")

        bot = Bot("", 24)
        keys = list(bot.data.keys())
        time = dt.datetime(year=1970, month=1, day=1, hour=12)
        key = bot._find_index(time)
        value = keys[key]
        self.assertEqual(value, "12:00")

        bot = Bot("", 24)
        keys = list(bot.data.keys())
        time = dt.datetime(year=1970, month=1, day=1, hour=0)
        key = bot._find_index(time)
        value = keys[key]
        self.assertEqual(value, "00:00")

        bot = Bot("", 12)
        keys = list(bot.data.keys())
        time = dt.datetime(year=1970, month=1, day=1, hour=5)
        key = bot._find_index(time)
        value = keys[key]
        self.assertEqual(value, "05:00 AM")

        bot = Bot("", 12)
        keys = list(bot.data.keys())
        time = dt.datetime(year=1970, month=1, day=1, hour=18)
        key = bot._find_index(time)
        value = keys[key]
        self.assertEqual(value, "06:00 PM")
