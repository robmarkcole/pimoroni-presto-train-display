"""Render README screenshots through the production BoardView implementation."""

from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.board_view import BoardView  # noqa: E402
from lib.train_app import DEFAULT_STATIONS  # noqa: E402


class ScreenshotDisplay:
    def __init__(self):
        self.image = Image.new("RGB", (480, 480))
        self.draw = ImageDraw.Draw(self.image)
        self.pen = (255, 255, 255)

    def create_pen(self, red, green, blue):
        return red, green, blue

    def set_font(self, _font):
        pass

    def set_pen(self, pen):
        self.pen = pen

    def clear(self):
        self.draw.rectangle((0, 0, 479, 479), fill=self.pen)

    def rectangle(self, x, y, width, height):
        self.draw.rectangle((x, y, x + width - 1, y + height - 1), fill=self.pen)

    def text(self, value, x, y, wrap, scale):
        font = ImageFont.load_default(size=8 * scale)
        words = str(value).split(" ")
        lines = []
        line = ""
        for word in words:
            candidate = word if not line else line + " " + word
            width = self.draw.textbbox((0, 0), candidate, font=font)[2]
            if wrap and line and width > wrap:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
        self.draw.multiline_text((x, y), "\n".join(lines), fill=self.pen, font=font, spacing=2)


class ScreenshotPresto:
    def __init__(self):
        self.display = ScreenshotDisplay()

    def update(self):
        pass


BOARD = {
    "services": [
        {
            "scheduled": "10:42",
            "destination": "London Waterloo",
            "status": "On time",
            "status_kind": "on_time",
            "platform": "2",
            "calling_points": [{"name": "Wimbledon"}, {"name": "Clapham Jn"}],
            "journey_minutes": 28,
            "arrival": "11:10",
        },
        {
            "scheduled": "10:57",
            "destination": "London Waterloo",
            "status": "Exp 10:59",
            "status_kind": "delayed",
            "platform": "2",
            "calling_points": [{"name": "Wimbledon"}, {"name": "Clapham Jn"}],
            "journey_minutes": 30,
            "arrival": "11:27",
        },
        {
            "scheduled": "11:12",
            "destination": "London Waterloo",
            "status": "On time",
            "status_kind": "on_time",
            "platform": "2",
            "calling_points": [{"name": "Wimbledon"}, {"name": "Clapham Jn"}],
            "journey_minutes": 28,
            "arrival": "11:40",
        },
        {
            "scheduled": "11:27",
            "destination": "London Waterloo",
            "status": "On time",
            "status_kind": "on_time",
            "platform": "2",
            "calling_points": [{"name": "Wimbledon"}, {"name": "Clapham Jn"}],
            "journey_minutes": 28,
            "arrival": "11:55",
        },
    ]
}


def render(filename, method, *args):
    presto = ScreenshotPresto()
    view = BoardView(presto)
    getattr(view, method)(*args)
    presto.display.image.save(ROOT / "docs" / "images" / filename)


render(
    "presto-station-picker.png",
    "render_station_picker",
    DEFAULT_STATIONS,
    "London Waterloo",
)
render(
    "presto-platform-board.png",
    "render_board",
    BOARD,
    "Worcester Park",
    "London Waterloo",
    None,
    "10:36",
)
render(
    "presto-journey-focus.png",
    "render_journey",
    BOARD,
    "Worcester Park",
    "London Waterloo",
    0,
    None,
    "10:36",
)
