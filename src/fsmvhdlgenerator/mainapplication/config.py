"""A module for storing configuration constants."""

import pathlib
from typing import Any, Dict, Union

Literal = Union[int, float, str]

ICON_PATH = pathlib.Path(__file__).parents[1] / "static/icon_unix.xbm"

GRID = {'fill': '#AAAAAA'}

DRAWING_AREA_SIZE = (3000, 2000)

STATE: Dict['str', Any] = {
    'radius': 60,
    'preview': {
        'fill': '#EEEEEE'
    },
    'normal': {
        'width': 2,
        'fill': 'white'
    }
}

TRANSITION: Dict['str', Any] = {
    'arrow': {
        "width": 3,
        "arrow": "last",
        "arrowshape": (12, 15, 5)
    },
    'radius': STATE['radius']
}

CLICK_HALO = 4
