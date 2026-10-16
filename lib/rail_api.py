"""Small MicroPython-friendly client for the RDM Live Departure Board API."""


USER_AGENT = "pimoroni-presto-train-display/0.1"


class RailApiError(Exception):
    pass


def validate_crs(value):
    value = (value or "").upper()
    if len(value) != 3 or not all("A" <= character <= "Z" for character in value):
        raise ValueError("CRS codes must be three ASCII letters")
    return value


def build_departure_url(
    base_url,
    origin_crs,
    destination_crs=None,
    num_rows=10,
    time_window=120,
):
    origin_crs = validate_crs(origin_crs)
    if not base_url or not base_url.startswith("https://"):
        raise ValueError("RDM_BASE_URL must be an HTTPS URL")
    if not 1 <= int(num_rows) <= 100:
        raise ValueError("num_rows must be between 1 and 100")
    if not 1 <= int(time_window) <= 1440:
        raise ValueError("time_window must be between 1 and 1440 minutes")

    url = "%s/GetDepBoardWithDetails/%s?numRows=%d&timeWindow=%d" % (
        base_url.rstrip("/"),
        origin_crs,
        int(num_rows),
        int(time_window),
    )
    if destination_crs:
        url += "&filterCrs=%s&filterType=to" % validate_crs(destination_crs)
    return url


class RailApi:
    def __init__(self, base_url, consumer_key, requests_module=None):
        if not consumer_key:
            raise ValueError("RDM_CONSUMER_KEY is missing")
        self.base_url = base_url
        self.consumer_key = consumer_key
        if requests_module is None:
            import urequests as requests_module
        self.requests = requests_module

    def get_departures(
        self,
        origin_crs,
        destination_crs=None,
        num_rows=10,
        time_window=120,
    ):
        url = build_departure_url(
            self.base_url,
            origin_crs,
            destination_crs,
            num_rows,
            time_window,
        )
        response = None
        try:
            response = self.requests.get(
                url,
                headers={
                    "x-apikey": self.consumer_key,
                    "accept": "application/json",
                    # RDM rejects clients that omit a User-Agent with HTTP 403.
                    "user-agent": USER_AGENT,
                },
            )
            status = getattr(response, "status_code", 0)
            if status < 200 or status >= 300:
                raise RailApiError("RDM request failed with HTTP %s" % status)
            return response.json()
        except RailApiError:
            raise
        except Exception as exc:
            raise RailApiError("RDM request failed: %s" % exc)
        finally:
            if response is not None:
                response.close()
