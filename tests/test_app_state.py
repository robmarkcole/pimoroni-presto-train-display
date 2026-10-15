import unittest

from lib.app_state import AppState


def add(now, delta):
    return now + delta


def diff(left, right):
    return left - right


class AppStateTest(unittest.TestCase):
    def test_success_and_bounded_backoff(self):
        state = AppState(refresh_seconds=60, backoff_seconds=(60, 120, 300))
        state.record_success({"services": []}, 1000, add)
        self.assertEqual(state.next_refresh_ms, 61000)
        self.assertEqual(state.age_seconds(61000, diff), 60)

        state.record_failure("one", 61000, add)
        self.assertEqual(state.next_refresh_ms, 121000)
        state.record_failure("two", 121000, add)
        self.assertEqual(state.next_refresh_ms, 241000)
        state.record_failure("three", 241000, add)
        self.assertEqual(state.next_refresh_ms, 541000)
        state.record_failure("four", 541000, add)
        self.assertEqual(state.next_refresh_ms, 841000)
