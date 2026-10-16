"""Run with `mpremote run tools/presto_smoke.py` to test the display only."""

import sys

sys.path.insert(0, ".")

from presto import Presto

from lib.board_view import BoardView


presto = Presto(full_res=True)
view = BoardView(presto)
view.render_board(
    {
        "services": [
            {"scheduled": "10:42", "destination": "London Waterloo", "status": "On time", "status_kind": "on_time", "platform": "2", "calling_points": [{"name": "Wimbledon"}, {"name": "Clapham Jn"}]},
            {"scheduled": "10:57", "destination": "London Waterloo", "status": "Exp 10:59", "status_kind": "delayed", "platform": "2", "calling_points": []},
            {"scheduled": "11:12", "destination": "London Waterloo", "status": "Cancelled", "status_kind": "cancelled", "platform": "", "calling_points": []},
        ]
    },
    "Worcester Park",
    "London Waterloo",
)
