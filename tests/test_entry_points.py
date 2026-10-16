import runpy
import sys
import types
import unittest
from unittest.mock import Mock, patch


class EntryPointTest(unittest.TestCase):
    def _fake_train_app(self):
        module = types.ModuleType("lib.train_app")
        module.run = Mock()
        return module

    def test_direct_boot_entry_runs_as_main(self):
        train_app = self._fake_train_app()
        with patch.dict(sys.modules, {"lib.train_app": train_app}):
            runpy.run_path("main.py", run_name="__main__")
        train_app.run.assert_called_once_with()

    def test_carousel_entry_runs_when_imported(self):
        train_app = self._fake_train_app()
        with patch.dict(sys.modules, {"lib.train_app": train_app}):
            runpy.run_path("train_display.py", run_name="train_display")
        train_app.run.assert_called_once_with()

    def test_carousel_entry_has_launcher_metadata(self):
        with open("train_display.py") as entry_point:
            header = [entry_point.readline().strip() for _ in range(3)]
        self.assertEqual(
            header,
            [
                "# ICON travel",
                "# NAME Train display",
                "# DESC Live Worcester Park departures",
            ],
        )


if __name__ == "__main__":
    unittest.main()
