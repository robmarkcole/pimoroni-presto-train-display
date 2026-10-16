"""Europe/London daylight-saving conversion without zoneinfo."""

import time


def _last_sunday(year, month):
    # Sakamoto's algorithm, where Sunday is zero. March and October have 31 days.
    offsets = (0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4)
    adjusted_year = year - (1 if month < 3 else 0)
    weekday = (
        adjusted_year
        + adjusted_year // 4
        - adjusted_year // 100
        + adjusted_year // 400
        + offsets[month - 1]
        + 31
    ) % 7
    return 31 - weekday


def is_bst_utc(year, month, day, hour):
    if month < 3 or month > 10:
        return False
    if 3 < month < 10:
        return True
    boundary_day = _last_sunday(year, month)
    if month == 3:
        return day > boundary_day or (day == boundary_day and hour >= 1)
    return day < boundary_day or (day == boundary_day and hour < 1)


def uk_localtime(epoch=None):
    if epoch is None:
        epoch = time.time()
    utc = time.gmtime(epoch)
    offset = 3600 if is_bst_utc(utc[0], utc[1], utc[2], utc[3]) else 0
    return time.gmtime(epoch + offset)


def format_clock(epoch=None):
    local = uk_localtime(epoch)
    return "%02d:%02d" % (local[3], local[4])
