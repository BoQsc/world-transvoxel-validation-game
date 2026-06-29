#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
G19_REPORT = (
    ROOT
    / "artifacts"
    / "g19_compact_2k_on_demand"
    / "g19_compact_2k_on_demand_report.json"
)
G18_REPORT = (
    ROOT
    / "artifacts"
    / "g18_world_budget_guard"
    / "g18_world_budget_guard_report.json"
)
G19_MARKER = "WT_VALIDATION_G19_COMPACT_2K_ON_DEMAND_PASS"
MARKER = "WT_VALIDATION_G20_COMPACT_TERRAIN_RESOLUTION_PASS"
MAX_GENERATED_FILE_BYTES = 50 * 1024 * 1024
MAX_GENERATED_TOTAL_BYTES = 100 * 1024 * 1024
MAX_LOAD_TO_PLAY_SECONDS = 30.0


def load_json(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise RuntimeError(f"missing required report: {path.relative_to(ROOT).as_posix()}")
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def marker_value(marker: str, key: str) -> str:
    prefix = f"{key}="
    for token in marker.split():
        if token.startswith(prefix):
            return token[len(prefix):]
    return ""


def validate_g19_report(report: dict[str, object]) -> dict[str, int]:
    require(
        report.get("implementation") == "compact_2k_on_demand_procedural_streaming",
        f"G19 report implementation mismatch: {report.get('implementation')}",
    )
    budget = report.get("budget", {})
    require(isinstance(budget, dict), "G19 report missing budget dictionary")
    require(
        budget.get("dense_source_artifacts") is False
        and budget.get("dense_world_artifacts") is False,
        f"G19 dense artifact flags are not false: {budget}",
    )
    require(
        float(budget.get("max_load_to_play_seconds", -1.0)) <= MAX_LOAD_TO_PLAY_SECONDS,
        f"G19 report has wrong load-to-play budget: {budget}",
    )
    post_run_budget = report.get("post_run_budget", {})
    require(
        isinstance(post_run_budget, dict),
        "G19 report missing post_run_budget dictionary",
    )
    max_file_bytes = int(post_run_budget.get("max_file_bytes", -1))
    total_bytes = int(post_run_budget.get("total_bytes", -1))
    require(
        0 <= max_file_bytes <= MAX_GENERATED_FILE_BYTES,
        f"G19 max file budget exceeded: {max_file_bytes}",
    )
    require(
        0 <= total_bytes <= MAX_GENERATED_TOTAL_BYTES,
        f"G19 total generated budget exceeded: {total_bytes}",
    )
    engines = report.get("engines", [])
    require(isinstance(engines, list) and len(engines) >= 2, "G19 must have two engine runs")
    max_engine_seconds = 0.0
    for engine in engines:
        require(isinstance(engine, dict), f"invalid engine result: {engine}")
        duration_seconds = float(engine.get("duration_seconds", -1.0))
        require(
            0.0 <= duration_seconds <= MAX_LOAD_TO_PLAY_SECONDS,
            f"G19 engine duration exceeded budget: {engine}",
        )
        max_engine_seconds = max(max_engine_seconds, duration_seconds)
        marker = str(engine.get("marker", ""))
        require(marker.startswith(G19_MARKER), f"G19 marker mismatch: {marker}")
        require(marker_value(marker, "profile") == "g19_compact_2k_on_demand", marker)
        require(marker_value(marker, "pages") == "16384", marker)
        require(int(marker_value(marker, "max_render_resources")) <= 25, marker)
        require(int(marker_value(marker, "max_collision_resources")) <= 25, marker)
        require(marker_value(marker, "dense_world_files") == "0", marker)
        require(int(marker_value(marker, "edit_replacements")) >= 1, marker)
    return {
        "max_file_bytes": max_file_bytes,
        "total_bytes": total_bytes,
        "engines": len(engines),
        "max_engine_milliseconds": int(round(max_engine_seconds * 1000.0)),
    }


def validate_g18_report(report: dict[str, object]) -> None:
    require(
        report.get("implementation") == "production_terrain_budget_pivot",
        f"G18 report implementation mismatch: {report.get('implementation')}",
    )
    stress_artifacts = report.get("stress_artifacts", {})
    require(
        isinstance(stress_artifacts, dict),
        f"G18 report missing stress artifact summary: {report}",
    )
    require(
        int(stress_artifacts.get("oversized_stress_artifacts", -1)) == 0,
        f"G18 still sees oversized stress artifacts: {report}",
    )


def main() -> None:
    g19_summary = validate_g19_report(load_json(G19_REPORT))
    validate_g18_report(load_json(G18_REPORT))
    print(
        f"{MARKER} compact_path_resolved=true map_blocks=2048 active_budget=25 "
        f"engines={g19_summary['engines']} "
        f"max_file_bytes={g19_summary['max_file_bytes']} "
        f"total_bytes={g19_summary['total_bytes']} "
        f"max_engine_ms={g19_summary['max_engine_milliseconds']} "
        f"report={G19_REPORT.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
