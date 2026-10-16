"""Pimoroni Presto live departure display application."""

import gc
import time

from presto import Presto

from lib.app_state import AppState
from lib.board_view import BoardView
from lib.departures import normalise_board
from lib.rail_api import RailApi
from lib.uk_time import format_clock


def load_settings():
    try:
        import config
        import secrets
    except ImportError as exc:
        raise RuntimeError("Copy config.py.example and secrets.py.example to the device") from exc
    return config, secrets


def run():
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
                view.render_board(
                    board,
                    getattr(config, "STATION_NAME", config.ORIGIN_CRS),
                    getattr(config, "DESTINATION_NAME", "Departures"),
                    clock=format_clock(),
                )
                del payload
                gc.collect()
            except Exception as exc:
                state.record_failure(exc, now, time.ticks_add)
                if state.board:
                    view.render_board(
                        state.board,
                        getattr(config, "STATION_NAME", config.ORIGIN_CRS),
                        getattr(config, "DESTINATION_NAME", "Departures"),
                        state.age_seconds(now, time.ticks_diff),
                        format_clock(),
                    )
                else:
                    view.render_error("Live data unavailable", str(exc))
        time.sleep_ms(100)
