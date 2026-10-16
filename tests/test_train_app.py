import unittest

from lib.train_app import (
    DEFAULT_STATIONS,
    departure_index_at,
    is_tap,
    sleep_is_due,
    station_index_at,
)


class TrainAppTest(unittest.TestCase):
    def test_departure_rows_map_to_service_indexes(self):
        self.assertEqual(departure_index_at(200, 120, 3), 0)
        self.assertEqual(departure_index_at(200, 200, 4), 1)
        self.assertEqual(departure_index_at(200, 290, 4), 2)
        self.assertEqual(departure_index_at(200, 380, 4), 3)

    def test_taps_outside_available_rows_are_ignored(self):
        self.assertIsNone(departure_index_at(200, 80, 3))
        self.assertIsNone(departure_index_at(200, 330, 2))
        self.assertIsNone(departure_index_at(200, 450, 4))

    def test_drag_is_not_a_tap(self):
        self.assertTrue(is_tap(200, 120, 205, 125))
        self.assertFalse(is_tap(200, 120, 240, 120))

    def test_screen_sleep_timeout(self):
        ticks_diff = lambda now, then: now - then
        self.assertFalse(sleep_is_due(299999, 0, 300, ticks_diff))
        self.assertTrue(sleep_is_due(300000, 0, 300, ticks_diff))
        self.assertFalse(sleep_is_due(999999, 0, 0, ticks_diff))

    def test_station_rows_map_to_picker_indexes(self):
        self.assertEqual(station_index_at(200, 150), 0)
        self.assertEqual(station_index_at(200, 210), 1)
        self.assertEqual(station_index_at(200, 290), 2)
        self.assertEqual(station_index_at(200, 370), 3)
        self.assertIsNone(station_index_at(10, 150))
        self.assertIsNone(station_index_at(200, 440))

    def test_default_station_codes(self):
        self.assertEqual(
            DEFAULT_STATIONS,
            (
                ("WCP", "Worcester Park"),
                ("MAL", "Malden Manor"),
                ("MOT", "Motspur Park"),
                ("NEM", "New Malden"),
            ),
        )


if __name__ == "__main__":
    unittest.main()
