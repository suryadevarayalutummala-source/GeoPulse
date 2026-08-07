"""
PLACEHOLDER until data teammate drops their real file here.

Expected call (named kwargs; parameter order is longitude, then latitude):

    AIContextBuilder().build_context(longitude=lon, latitude=lat)

Never pass positional args — named kwargs avoid lon/lat swaps.
"""

from __future__ import annotations

from typing import Any


class AIContextBuilder:
    def build_context(self, *, longitude: float, latitude: float) -> dict[str, Any]:
        raise NotImplementedError(
            "Replace this file with the data teammate's AIContextBuilder implementation."
        )
