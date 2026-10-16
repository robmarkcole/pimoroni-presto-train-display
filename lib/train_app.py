"""Pimoroni Presto live departure display application."""

import gc
import time

from lib.app_state import AppState
from lib.board_view import BoardView
from lib.departures import normalise_board
from lib.rail_api import RailApi
from lib.uk_time import format_clock


DEPARTURE_TOP = 96
DEPARTURE_HEIGHT = 104
DEPARTURE_COUNT = 3


def departure_index_at(x, y, service_count=DEPARTURE_COUNT):
    if x < 0 or x >= 480 or y < DEPARTURE_TOP:
        return None
    index = (y - DEPARTURE_TOP) // DEPARTURE_HEIGHT
    if index < 0 or index >= min(service_count, DEPARTURE_COUNT):
        return None
    return index


def is_tap(start_x, start_y, end_x, end_y):
    return abs(end_x - start_x) <= 12 and abs(end_y - start_y) <= 12


def load_settings():
    try:
        import config
        import secrets
    except ImportError as exc:
        raise RuntimeError("Copy config.py.example and secrets.py.example to the device") from exc
    return config, secrets


def run():
    from presto import Presto

    presto = Presto(full_res=True)
    view = BoardView(presto)
    view.render_loading()

    try:
        config, secrets = load_settings()
        if hasattr(presto, "set_backlight"):
            presto.set_backlight(getattr(config, "SCREEN_BRIGHTNESS", 0.85))
        presto.connect()
        try:
            import ntptime

            ntptime.settime()
        except Exception:
            pass
        api = RailApi(config.RDM_BASE_URL, secrets.RDM_CONSUMER_KEY)
    except Exception as exc:
        view.render_error("Configuration error", str(exc))
        return

    state = AppState(getattr(config, "REFRESH_SECONDS", 60))
    selected_index = None
    touch = presto.touch
    touch_was_down = False
    touch_start_x = 0
    touch_start_y = 0

    def render_current():
        stale_age = None
        now = time.ticks_ms()
        if state.last_success_ms is not None and state.last_error:
            stale_age = state.age_seconds(now, time.ticks_diff)
        station_name = getattr(config, "STATION_NAME", config.ORIGIN_CRS)
        destination_name = getattr(config, "DESTINATION_NAME", "Departures")
        if selected_index is None:
            view.render_board(state.board, station_name, destination_name, stale_age, format_clock())
        else:
            view.render_journey(state.board, station_name, destination_name, selected_index, stale_age, format_clock())

    while True:
        now = time.ticks_ms()
        if state.is_due(now, time.ticks_diff):
            try:
                payload = api.get_departures(
                    config.ORIGIN_CRS,
                    getattr(config, "DESTINATION_CRS", None),
                    getattr(config, "NUM_ROWS", 10),
                    getattr(config, "TIME_WINDOW_MINUTES", 120),
                )
                board = normalise_board(payload)
                state.record_success(board, now, time.ticks_add)
                render_current()
                del payload
                gc.collect()
            except Exception as exc:
                state.record_failure(exc, now, time.ticks_add)
                if state.board:
                    render_current()
                else:
                    view.render_error("Live data unavailable", str(exc))

        touch.poll()
        if touch.state and not touch_was_down:
            touch_start_x = touch.x
            touch_start_y = touch.y
        elif not touch.state and touch_was_down and state.board:
            if is_tap(touch_start_x, touch_start_y, touch.x, touch.y):
                if selected_index is None:
                    tapped_index = departure_index_at(
                        touch.x,
                        touch.y,
                        len(state.board.get("services", [])),
                    )
                    if tapped_index is not None:
                        selected_index = tapped_index
                        render_current()
                else:
                    selected_index = None
                    render_current()
        touch_was_down = touch.state
        time.sleep_ms(100)
