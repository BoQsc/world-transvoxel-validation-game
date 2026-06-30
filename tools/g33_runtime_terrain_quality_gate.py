#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from compose_validation_project import ROOT
from g19_compact_2k_on_demand_smoke import (
    MAX_GENERATED_FILE_BYTES,
    MAX_GENERATED_TOTAL_BYTES,
    PROFILE_ID,
)


ARTIFACT_ROOT = ROOT / "artifacts" / "g33_runtime_terrain_quality_gate"
G32_REPORT = (
    ROOT
    / "artifacts"
    / "g32_review_bundle_runtime_proof"
    / "g32_review_bundle_runtime_proof_report.json"
)
MARKER = "WT_VALIDATION_G33_RUNTIME_TERRAIN_QUALITY_PASS"
MAX_ACTIVE_RESOURCES = 25
MAX_SCRIPT_SECONDS = 30.0
MIN_FULL_MAP_COLORED_SAMPLES = 50_000


def parse_marker(marker: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for token in marker.split()[1:]:
        if "=" in token:
            key, value = token.split("=", 1)
            fields[key] = value
    return fields


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def int_field(fields: dict[str, str], key: str) -> int:
    return int(fields.get(key, "-1"))


def bool_field(fields: dict[str, str], key: str) -> bool:
    return fields.get(key, "false").lower() == "true"


def assert_common(result: dict[str, object], fields: dict[str, str], errors: list[str]) -> None:
    evidence = dict(result.get("evidence", {}))
    duration = float(result.get("duration_seconds", 9999.0))
    require(duration <= MAX_SCRIPT_SECONDS, f"script exceeded {MAX_SCRIPT_SECONDS:.0f}s: {result}", errors)
    require(fields.get("profile") == PROFILE_ID, f"wrong profile in marker: {result}", errors)
    require(int_field(fields, "pages") == 16_384, f"page count mismatch: {result}", errors)
    require(int_field(fields, "map_blocks") == 2_048, f"map size mismatch: {result}", errors)
    require(fields.get("dense_world_files") == "0", f"dense files reported: {result}", errors)
    require(int(evidence.get("png_count", 0)) > 0, f"missing PNG evidence: {result}", errors)
    for file_record in evidence.get("files", []):
        path = ROOT / "artifacts" / "g32_review_bundle_runtime_proof" / str(file_record["path"])
        require(path.is_file(), f"evidence file missing on disk: {path}", errors)
        require(int(file_record.get("bytes", 0)) > 1024, f"evidence file too small: {file_record}", errors)


def assert_g25(result: dict[str, object], fields: dict[str, str], errors: list[str]) -> None:
    assert_common(result, fields, errors)
    require(fields.get("full_visual_blocks") == "2048x2048", f"full visual coverage mismatch: {result}", errors)
    require(int_field(fields, "full_visual_vertices") > 0, f"full visual has no vertices: {result}", errors)
    require(int_field(fields, "full_visual_triangles") > 0, f"full visual has no triangles: {result}", errors)
    require(int_field(fields, "native_render_resources") <= MAX_ACTIVE_RESOURCES, f"render budget exceeded: {result}", errors)
    require(int_field(fields, "native_collision_resources") <= MAX_ACTIVE_RESOURCES, f"collision budget exceeded: {result}", errors)
    require(
        int_field(fields, "capture_colored_samples") >= MIN_FULL_MAP_COLORED_SAMPLES,
        f"full-map capture lacks colored terrain samples: {result}",
        errors,
    )


def assert_g26(result: dict[str, object], fields: dict[str, str], errors: list[str]) -> None:
    assert_common(result, fields, errors)
    evidence = dict(result.get("evidence", {}))
    require(int_field(fields, "captures") >= 3, f"not enough first-person captures: {result}", errors)
    require(int(evidence.get("png_count", 0)) >= 3, f"G26 copied evidence incomplete: {result}", errors)
    require(int_field(fields, "player_stream_updates") >= 3, f"player streaming did not update enough: {result}", errors)
    require(int_field(fields, "max_render_resources") <= MAX_ACTIVE_RESOURCES, f"render budget exceeded: {result}", errors)
    require(int_field(fields, "max_collision_resources") <= MAX_ACTIVE_RESOURCES, f"collision budget exceeded: {result}", errors)
    require(bool_field(fields, "full_visual_visible"), f"full visual was not visible: {result}", errors)


def assert_g27(result: dict[str, object], fields: dict[str, str], errors: list[str]) -> None:
    assert_common(result, fields, errors)
    evidence = dict(result.get("evidence", {}))
    require(int_field(fields, "captures") >= 2, f"not enough handoff captures: {result}", errors)
    require(int(evidence.get("png_count", 0)) >= 2, f"G27 copied evidence incomplete: {result}", errors)
    require(1 <= int_field(fields, "material_auto_applies") <= 12, f"material auto-apply count unstable: {result}", errors)
    require(int_field(fields, "player_stream_updates") >= 1, f"player streaming did not update: {result}", errors)
    require(int_field(fields, "max_render_resources") <= MAX_ACTIVE_RESOURCES, f"render budget exceeded: {result}", errors)
    require(int_field(fields, "max_collision_resources") <= MAX_ACTIVE_RESOURCES, f"collision budget exceeded: {result}", errors)
    require(fields.get("human_input") == "false", f"automation did not disable human input: {result}", errors)
    require(bool_field(fields, "full_visual_visible"), f"full visual was not visible: {result}", errors)


def assert_result_coverage(results: list[dict[str, object]], errors: list[str]) -> dict[str, int]:
    coverage: dict[str, int] = {}
    expected = {
        "g25_full_terrain_visual_baseline": assert_g25,
        "g26_full_terrain_playable_experience": assert_g26,
        "g27_full_terrain_handoff_preflight": assert_g27,
    }
    engines = {str(result.get("engine", "")) for result in results}
    require(len(engines) >= 2, f"expected at least two engines, got {engines}", errors)
    for result in results:
        test_id = str(result.get("test_id", ""))
        fields = parse_marker(str(result.get("marker", "")))
        require(test_id in expected, f"unexpected G32 result test_id: {test_id}", errors)
        if test_id in expected:
            expected[test_id](result, fields, errors)
            coverage[test_id] = coverage.get(test_id, 0) + 1
    for test_id in expected:
        require(coverage.get(test_id, 0) == len(engines), f"missing engine coverage for {test_id}", errors)
    return coverage


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit runtime terrain quality evidence.")
    parser.add_argument("--report", type=Path, default=G32_REPORT)
    arguments = parser.parse_args()

    report_path = arguments.report.resolve()
    if not report_path.is_file():
        raise SystemExit(f"G33 requires G32 runtime proof report: {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    require(report.get("implementation") == "review_bundle_runtime_proof", "wrong prerequisite implementation", errors)
    require(report.get("profile") == PROFILE_ID, "wrong prerequisite profile", errors)
    require(report.get("automation_human_input_enabled") is False, "automation input should be disabled", errors)
    require(report.get("source_bundle_human_input_enabled") is True, "source bundle should stay human-input ready", errors)
    budget = dict(report.get("post_run_budget", {}))
    require(int(budget.get("max_file_bytes", 0)) <= MAX_GENERATED_FILE_BYTES, f"max file budget exceeded: {budget}", errors)
    require(int(budget.get("total_bytes", 0)) <= MAX_GENERATED_TOTAL_BYTES, f"total file budget exceeded: {budget}", errors)
    results = list(report.get("results", []))
    coverage = assert_result_coverage(results, errors)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    summary = {
        "source_report": str(report_path),
        "profile": PROFILE_ID,
        "engines": sorted({str(result.get("engine", "")) for result in results}),
        "coverage": coverage,
        "max_script_seconds": max(float(result["duration_seconds"]) for result in results),
        "max_active_resources": MAX_ACTIVE_RESOURCES,
        "implementation": "runtime_terrain_quality_gate",
    }
    summary_path = ARTIFACT_ROOT / "g33_runtime_terrain_quality_gate_report.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(
        f"{MARKER} profile={PROFILE_ID} engines={len(summary['engines'])} "
        f"g25={coverage.get('g25_full_terrain_visual_baseline', 0)} "
        f"g26={coverage.get('g26_full_terrain_playable_experience', 0)} "
        f"g27={coverage.get('g27_full_terrain_handoff_preflight', 0)} "
        "map_blocks=2048 max_active_resources=25 "
        f"max_script_seconds={float(summary['max_script_seconds']):.3f} "
        "quality_track=runtime_terrain dense_world_files=0 "
        f"report={summary_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
