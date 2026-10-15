"""480x480 platform-style renderer for Pimoroni Presto."""


class BoardView:
    WIDTH = 480
    HEIGHT = 480

    def __init__(self, presto):
        self.presto = presto
        self.display = presto.display
        self.black = self.display.create_pen(3, 8, 6)
        self.panel = self.display.create_pen(17, 25, 20)
        self.amber = self.display.create_pen(255, 176, 0)
        self.cream = self.display.create_pen(255, 247, 220)
        self.green = self.display.create_pen(84, 220, 139)
        self.red = self.display.create_pen(255, 93, 89)
        self.muted = self.display.create_pen(165, 179, 169)
        self.dim_amber = self.display.create_pen(85, 69, 12)
        self.display.set_font("bitmap8")

    def _clear(self):
        self.display.set_pen(self.black)
        self.display.clear()

    def _text(self, text, x, y, pen, scale=2, wrap=0):
        self.display.set_pen(pen)
        self.display.text(str(text), x, y, wrap, scale)

    def _rule(self, y, pen=None):
        self.display.set_pen(pen or self.amber)
        self.display.rectangle(0, y, self.WIDTH, 2)

    def _platform(self, value, y):
        value = value or "–"
        self.display.set_pen(self.cream)
        self.display.rectangle(422, y, 42, 42)
        self._text(value, 433 if len(value) == 1 else 426, y + 8, self.black, 3)

    def render_loading(self, message="Connecting to live departures"):
        self._clear()
        self._text("WORCESTER PARK", 28, 50, self.amber, 3)
        self._text(message, 28, 210, self.cream, 2, 420)
        self._text("National Rail Darwin", 28, 420, self.muted, 2)
        self.presto.update()

    def render_error(self, title, detail=""):
        self._clear()
        self._text(title, 28, 70, self.red, 3, 420)
        self._text(detail, 28, 175, self.cream, 2, 420)
        self._text("Tap reset or check configuration", 28, 420, self.muted, 2)
        self.presto.update()

    def render_board(self, board, station_name, destination_name, stale_age=None, clock=""):
        self._clear()
        self._text(station_name.upper(), 24, 22, self.amber, 2)
        self._text(destination_name, 24, 51, self.cream, 3, 390)
        self._text("STALE" if stale_age is not None else "LIVE", 400, 29, self.red if stale_age is not None else self.green, 2)
        if clock:
            self._text(clock, 400, 62, self.cream, 2)
        self._rule(91)

        services = board.get("services", [])[:3]
        if not services:
            self._text("No departures found", 24, 200, self.cream, 3)
        for index, service in enumerate(services):
            y = 104 + index * 104
            if index == 0:
                self.display.set_pen(self.panel)
                self.display.rectangle(0, y - 8, self.WIDTH, 96)
            status_pen = self.green
            if service.get("status_kind") == "delayed":
                status_pen = self.amber
            elif service.get("status_kind") == "cancelled":
                status_pen = self.red
            self._text(service.get("scheduled") or "--:--", 24, y, self.amber, 4)
            self._text(service.get("destination", ""), 152, y + 2, self.cream, 2, 245)
            self._text(service.get("status", ""), 336, y + 54, status_pen, 1, 78)
            self._platform(service.get("platform"), y + 4)
            points = service.get("calling_points", [])
            if points:
                names = " · ".join(point["name"] for point in points[:2])
                self._text("via " + names, 152, y + 34, self.muted, 1, 250)
            self._rule(y + 88, self.dim_amber)

        if stale_age is None:
            footer = "Updated just now"
        else:
            footer = "Last update %d min ago" % max(1, stale_age // 60)
        self._text(footer, 24, 438, self.muted, 2)
        self._text("Data: National Rail", 284, 438, self.muted, 2)
        self.presto.update()
