import unittest

from lib.rail_api import RailApi, RailApiError, build_departure_url


class Response:
    def __init__(self, status=200):
        self.status_code = status
        self.closed = False

    def json(self):
        return {"trainServices": []}

    def close(self):
        self.closed = True


class Requests:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get(self, url, headers):
        self.calls.append((url, headers))
        return self.response


class RailApiTest(unittest.TestCase):
    def test_builds_filtered_https_url(self):
        url = build_departure_url("https://example.invalid/ldb", "wcp", "wat", 8, 90)
        self.assertEqual(url, "https://example.invalid/ldb/GetDepBoardWithDetails/WCP?numRows=8&timeWindow=90&filterCrs=WAT&filterType=to")

    def test_rejects_invalid_configuration(self):
        with self.assertRaises(ValueError):
            build_departure_url("http://example.invalid", "WCP")
        with self.assertRaises(ValueError):
            build_departure_url("https://example.invalid", "WC1")

    def test_closes_response_and_sends_required_headers(self):
        response = Response()
        requests = Requests(response)
        api = RailApi("https://example.invalid", "secret", requests)
        self.assertEqual(api.get_departures("WCP"), {"trainServices": []})
        headers = requests.calls[0][1]
        self.assertEqual(headers["x-apikey"], "secret")
        self.assertEqual(headers["accept"], "application/json")
        self.assertEqual(headers["user-agent"], "pimoroni-presto-train-display/0.1")
        self.assertTrue(response.closed)

    def test_http_error_is_sanitised_and_response_is_closed(self):
        response = Response(401)
        api = RailApi("https://example.invalid", "secret", Requests(response))
        with self.assertRaisesRegex(RailApiError, "HTTP 401"):
            api.get_departures("WCP")
        self.assertTrue(response.closed)
