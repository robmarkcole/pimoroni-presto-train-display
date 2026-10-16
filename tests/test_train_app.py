import unittest

from lib.train_app import is_view_toggle_tap


class TrainAppTest(unittest.TestCase):
    def test_view_button_tap(self):
        self.assertTrue(is_view_toggle_tap(410, 440, 413, 443))

    def test_drag_or_tap_elsewhere_does_not_toggle(self):
        self.assertFalse(is_view_toggle_tap(100, 440, 100, 440))
        self.assertFalse(is_view_toggle_tap(410, 440, 380, 440))


if __name__ == "__main__":
    unittest.main()
