import unittest

from lib.train_app import departure_index_at, is_tap


class TrainAppTest(unittest.TestCase):
    def test_departure_rows_map_to_service_indexes(self):
        self.assertEqual(departure_index_at(200, 120, 3), 0)
        self.assertEqual(departure_index_at(200, 220, 3), 1)
        self.assertEqual(departure_index_at(200, 330, 3), 2)

    def test_taps_outside_available_rows_are_ignored(self):
        self.assertIsNone(departure_index_at(200, 80, 3))
        self.assertIsNone(departure_index_at(200, 330, 2))
        self.assertIsNone(departure_index_at(200, 430, 3))

    def test_drag_is_not_a_tap(self):
        self.assertTrue(is_tap(200, 120, 205, 125))
        self.assertFalse(is_tap(200, 120, 240, 120))


if __name__ == "__main__":
    unittest.main()
