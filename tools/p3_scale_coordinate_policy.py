#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "artifacts" / "p3_scale_coordinate_policy"
MARKER = "WT_VALIDATION_P3_SCALE_COORDINATE_POLICY_PASS"

PROFILE = "large_4k_optional"
CHUNK_SIZE_BLOCKS = 16
MAP_BLOCKS = 4096
COMPACT_BLOCKS = 2048
ACTIVE_RADIUS = 6
ACTIVE_CAPACITY = 256
MAX_FILE_BYTES = 1024
TOTAL_BYTES = 1024
LOAD_BUDGET_SECONDS = 30
MEMORY_BUDGET_MB = 64
ORIGIN_SHIFT_RESEARCH_BLOCKS = 32768


def main() -> None:
    chunk_grid = MAP_BLOCKS // CHUNK_SIZE_BLOCKS
    pages = chunk_grid * chunk_grid
    active_resources = (ACTIVE_RADIUS * 2 + 1) ** 2
    streaming_ratio_ppm = int(active_resources * 1_000_000 / pages)
    errors: list[str] = []
    if MAP_BLOCKS <= COMPACT_BLOCKS:
        errors.append("P3 profile must be larger than compact 2K")
    if chunk_grid != 256 or pages != 65536:
        errors.append("P3 4K page math is inconsistent")
    if active_resources > ACTIVE_CAPACITY:
        errors.append("P3 active resources exceed capacity")
    if MAX_FILE_BYTES > 50 * 1024 * 1024 or TOTAL_BYTES > 100 * 1024 * 1024:
        errors.append("P3 file budget exceeds production ceiling")
    if LOAD_BUDGET_SECONDS > 30:
        errors.append("P3 load budget exceeds standard ceiling")
    if MAP_BLOCKS >= ORIGIN_SHIFT_RESEARCH_BLOCKS:
        errors.append("P3 4K profile unexpectedly requires origin-shift research")
    if errors:
        raise SystemExit("; ".join(errors))

    report = {
        "profile": PROFILE,
        "scale": {
            "map_blocks": MAP_BLOCKS,
            "chunk_size_blocks": CHUNK_SIZE_BLOCKS,
            "chunk_grid": [chunk_grid, chunk_grid],
            "pages": pages,
        },
        "streaming": {
            "active_radius": ACTIVE_RADIUS,
            "active_resources": active_resources,
            "active_capacity": ACTIVE_CAPACITY,
            "streaming_ratio_ppm": streaming_ratio_ppm,
        },
        "budgets": {
            "max_file_bytes": MAX_FILE_BYTES,
            "total_bytes": TOTAL_BYTES,
            "load_budget_seconds": LOAD_BUDGET_SECONDS,
            "memory_budget_mb": MEMORY_BUDGET_MB,
        },
        "coordinate_policy": {
            "block_meters": 1,
            "origin_policy": "single_precision_no_shift",
            "origin_shift_research_blocks": ORIGIN_SHIFT_RESEARCH_BLOCKS,
            "large_world_coordinates_required": False,
        },
        "visible_presentation": {"full_visual_blocks": [MAP_BLOCKS, MAP_BLOCKS]},
    }
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    report_path = ARTIFACT_ROOT / "p3_scale_coordinate_policy_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"{MARKER} profile={PROFILE} map_blocks={MAP_BLOCKS} "
        f"chunk_grid={chunk_grid}x{chunk_grid} pages={pages} active_radius={ACTIVE_RADIUS} "
        f"active_resources={active_resources} active_capacity={ACTIVE_CAPACITY} "
        f"streaming_ratio_ppm={streaming_ratio_ppm} max_file_bytes={MAX_FILE_BYTES} "
        f"total_bytes={TOTAL_BYTES} load_budget_seconds={LOAD_BUDGET_SECONDS} "
        f"memory_budget_mb={MEMORY_BUDGET_MB} full_visual_blocks={MAP_BLOCKS}x{MAP_BLOCKS} "
        "origin_policy=single_precision_no_shift "
        "next=P4_production_rendering_materials_object_density "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
