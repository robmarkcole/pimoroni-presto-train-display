import calendar
import datetime
import unittest

from lib.uk_time import is_bst_utc, uk_localtime


def epoch(year, month, day, hour, minute=0):
    return calendar.timegm(datetime.datetime(year, month, day, hour, minute).timetuple())


class UkTimeTest(unittest.TestCase):
    def test_bst_boundaries_2026(self):
        self.assertFalse(is_bst_utc(2026, 3, 29, 0))
        self.assertTrue(is_bst_utc(2026, 3, 29, 1))
        self.assertTrue(is_bst_utc(2026, 10, 25, 0))
        self.assertFalse(is_bst_utc(2026, 10, 25, 1))

    def test_local_time_applies_the_correct_offset(self):
        self.assertEqual(uk_localtime(epoch(2026, 7, 1, 12))[:5], (2026, 7, 1, 13, 0))
        self.assertEqual(uk_localtime(epoch(2026, 12, 1, 12))[:5], (2026, 12, 1, 12, 0))
