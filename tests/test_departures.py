import json
import unittest
from pathlib import Path

from lib.departures import normalise_board


def sample_payload():
    path = Path(__file__).parent / "fixtures" / "sample_rdm.json"
    return json.loads(path.read_text())


class DeparturesTest(unittest.TestCase):
    def test_normalises_services_and_calling_points(self):
        board = normalise_board(sample_payload())
        self.assertEqual(board["station"], "Worcester Park")
        self.assertEqual(len(board["services"]), 3)
        self.assertEqual(board["services"][0]["status"], "On time")
        self.assertEqual(board["services"][0]["calling_points"][0]["name"], "Motspur Park")
        self.assertEqual(board["services"][0]["arrival"], "10:52")
        self.assertEqual(board["services"][0]["journey_minutes"], 10)
        self.assertEqual(board["services"][1]["status"], "Exp 10:59")
        self.assertEqual(board["services"][1]["status_kind"], "delayed")
        self.assertEqual(board["services"][2]["status"], "Cancelled")
        self.assertEqual(board["services"][2]["platform"], "")

    def test_accepts_wrapped_single_service_shape(self):
        payload = {
            "GetDepBoardWithDetailsResult": {
                "locationName": "Worcester Park",
                "trainServices": {"service": {"std": "12:00", "etd": "On time", "destination": {"locationName": "London Waterloo"}}},
            }
        }
        board = normalise_board(payload)
        self.assertEqual(board["services"][0]["destination"], "London Waterloo")
