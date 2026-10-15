"""Refresh scheduling and stale-data state."""


class AppState:
    def __init__(self, refresh_seconds=60, backoff_seconds=(60, 120, 300)):
        self.refresh_ms = int(refresh_seconds * 1000)
        self.backoff_ms = tuple(int(value * 1000) for value in backoff_seconds)
        self.next_refresh_ms = 0
        self.failures = 0
        self.last_success_ms = None
        self.last_error = ""
        self.board = None

    def is_due(self, now_ms, ticks_diff):
        return ticks_diff(now_ms, self.next_refresh_ms) >= 0

    def record_success(self, board, now_ms, ticks_add):
        self.board = board
        self.failures = 0
        self.last_error = ""
        self.last_success_ms = now_ms
        self.next_refresh_ms = ticks_add(now_ms, self.refresh_ms)

    def record_failure(self, error, now_ms, ticks_add):
        index = min(self.failures, len(self.backoff_ms) - 1)
        self.failures += 1
        self.last_error = str(error)
        self.next_refresh_ms = ticks_add(now_ms, self.backoff_ms[index])

    def age_seconds(self, now_ms, ticks_diff):
        if self.last_success_ms is None:
            return None
        return max(0, ticks_diff(now_ms, self.last_success_ms) // 1000)
