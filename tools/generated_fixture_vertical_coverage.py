#!/usr/bin/env python3

from __future__ import annotations

import math
from typing import Callable


ACTIVE_VERTICAL_MIN = 0.0
ACTIVE_VERTICAL_MAX = 16.0
REQUIRED_LOWER_MARGIN = 1.0
REQUIRED_UPPER_MARGIN = 0.75


def surface_coverage(
    *,
    label: str,
    height_function: Callable[[int, int], float],
    origin: tuple[int, int, int],
    dimensions: tuple[int, int, int],
) -> dict[str, float | str]:
    min_height = math.inf
    max_height = -math.inf
    min_x = origin[0]
    max_x = origin[0] + dimensions[0] - 1
    min_z = origin[2]
    max_z = origin[2] + dimensions[2] - 1
    for z in range(min_z, max_z + 1):
        for x in range(min_x, max_x + 1):
            height = float(height_function(x, z))
            if not math.isfinite(height):
                raise RuntimeError(f"{label} height field produced non-finite value at {x},{z}: {height}")
            min_height = min(min_height, height)
            max_height = max(max_height, height)
    return {
        "label": label,
        "surface_min_y": min_height,
        "surface_max_y": max_height,
        "active_vertical_min_y": ACTIVE_VERTICAL_MIN,
        "active_vertical_max_y": ACTIVE_VERTICAL_MAX,
        "lower_margin": min_height - ACTIVE_VERTICAL_MIN,
        "upper_margin": ACTIVE_VERTICAL_MAX - max_height,
        "required_lower_margin": REQUIRED_LOWER_MARGIN,
        "required_upper_margin": REQUIRED_UPPER_MARGIN,
    }


def assert_surface_within_active_vertical_chunk(coverage: dict[str, float | str]) -> dict[str, float | str]:
    lower_margin = float(coverage["lower_margin"])
    upper_margin = float(coverage["upper_margin"])
    if lower_margin < REQUIRED_LOWER_MARGIN or upper_margin < REQUIRED_UPPER_MARGIN:
        raise RuntimeError(
            "generated fixture surface leaves active vertical chunk safety margins: "
            f"{coverage}"
        )
    return coverage
