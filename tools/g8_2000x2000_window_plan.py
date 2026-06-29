#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "artifacts" / "g8_2000x2000_window_plan"
MARKER = "WT_VALIDATION_G8_WINDOW_PLAN_PASS"

MAP_BLOCKS = 2000
CHUNK_SIZE = 16
CHUNK_GRID = 125
WINDOW_RADIUS_CHUNKS = 2
ACTIVE_CHUNK_BUDGET = 256

PATH_BLOCKS = (
    (8, 8),
    (496, 496),
    (1000, 1000),
    (1504, 496),
    (1991, 1991),
)


def chunk_coordinate(block_coordinate: int) -> int:
    if block_coordinate < 0 or block_coordinate >= MAP_BLOCKS:
        raise ValueError(f"block coordinate outside 2000x2000 map: {block_coordinate}")
    return block_coordinate // CHUNK_SIZE


def active_window(center_x: int, center_z: int) -> list[tuple[int, int]]:
    chunks: list[tuple[int, int]] = []
    for z in range(center_z - WINDOW_RADIUS_CHUNKS, center_z + WINDOW_RADIUS_CHUNKS + 1):
        for x in range(center_x - WINDOW_RADIUS_CHUNKS, center_x + WINDOW_RADIUS_CHUNKS + 1):
            if 0 <= x < CHUNK_GRID and 0 <= z < CHUNK_GRID:
                chunks.append((x, z))
    return chunks


def validate_path() -> dict[str, object]:
    if (MAP_BLOCKS + CHUNK_SIZE - 1) // CHUNK_SIZE != CHUNK_GRID:
        raise RuntimeError("chunk grid does not cover the 2000 block map")
    samples: list[dict[str, object]] = []
    max_window_columns = 0
    union: set[tuple[int, int]] = set()
    for block_x, block_z in PATH_BLOCKS:
        chunk_x = chunk_coordinate(block_x)
        chunk_z = chunk_coordinate(block_z)
        window = active_window(chunk_x, chunk_z)
        max_window_columns = max(max_window_columns, len(window))
        union.update(window)
        if not window:
            raise RuntimeError(f"empty active window at {(block_x, block_z)}")
        if len(window) > ACTIVE_CHUNK_BUDGET:
            raise RuntimeError(f"active window exceeds budget at {(block_x, block_z)}")
        samples.append(
            {
                "block": [block_x, block_z],
                "chunk": [chunk_x, chunk_z],
                "window_columns": len(window),
                "first_column": list(window[0]),
                "last_column": list(window[-1]),
            }
        )
    if max_window_columns != (WINDOW_RADIUS_CHUNKS * 2 + 1) ** 2:
        raise RuntimeError("center window did not exercise the full radius-2 shape")
    return {
        "map_blocks": MAP_BLOCKS,
        "meters_per_block": 1,
        "area_m2": MAP_BLOCKS * MAP_BLOCKS,
        "area_km2": 4,
        "chunk_size": CHUNK_SIZE,
        "chunk_grid": [CHUNK_GRID, CHUNK_GRID],
        "window_radius_chunks": WINDOW_RADIUS_CHUNKS,
        "max_window_columns": max_window_columns,
        "active_chunk_budget": ACTIVE_CHUNK_BUDGET,
        "path": samples,
        "path_union_columns": len(union),
    }


def main() -> None:
    report = validate_path()
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    report_path = ARTIFACT_ROOT / "g8_2000x2000_window_plan_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"{MARKER} map_blocks={MAP_BLOCKS} "
        f"chunk_grid={CHUNK_GRID}x{CHUNK_GRID} "
        f"max_window_columns={report['max_window_columns']} "
        f"active_budget={ACTIVE_CHUNK_BUDGET} "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
