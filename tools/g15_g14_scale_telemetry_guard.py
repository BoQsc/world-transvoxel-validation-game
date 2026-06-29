#!/usr/bin/env python3

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from compose_validation_project import ROOT


G14_ARTIFACT_ROOT = ROOT / "artifacts" / "g14_generated_64x64_playable_streaming"
G14_REPORT = G14_ARTIFACT_ROOT / "g14_generated_64x64_playable_streaming_report.json"
G14_SOURCE_ROOT = G14_ARTIFACT_ROOT / "source"
G15_ARTIFACT_ROOT = ROOT / "artifacts" / "g15_g14_scale_telemetry"
G15_REPORT = G15_ARTIFACT_ROOT / "g15_g14_scale_telemetry_report.json"

G14_MARKER = "WT_VALIDATION_G14_GENERATED_64X64_PLAYABLE_STREAMING_PASS"
G15_MARKER = "WT_VALIDATION_G15_G14_SCALE_TELEMETRY_PASS"

EXPECTED_PROFILE = "g14_generated_64x64"
EXPECTED_IMPLEMENTATION = "generated_64x64_playable_streaming"
EXPECTED_SOURCE_WRITER = "streamed_height_source"
EXPECTED_DIMENSIONS = (1029, 65, 1029)
EXPECTED_SOURCE_REVISION = 146400
EXPECTED_PAGE_COUNT = 4096
EXPECTED_ENGINE_COUNT = 2
EXPECTED_MAX_ACTIVE_RESOURCES = 25
EXPECTED_DENSITY_BYTES = 275298660
EXPECTED_MATERIAL_BYTES = 137649330
EXPECTED_REQUIRED_LOWER_MARGIN = 1.0
EXPECTED_REQUIRED_UPPER_MARGIN = 0.75


def fail_missing_artifacts(path: Path) -> None:
    raise SystemExit(
        f"ERROR: missing {path.relative_to(ROOT).as_posix()}; "
        "run `python tools/g14_generated_64x64_playable_streaming_smoke.py` first"
    )


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def marker_fields(marker: str) -> dict[str, str]:
    return {match.group(1): match.group(2) for match in re.finditer(r"(\w+)=([^\s]+)", marker)}


def int_field(fields: dict[str, str], key: str, errors: list[str]) -> int | None:
    value = fields.get(key)
    if value is None:
        errors.append(f"marker missing {key}")
        return None
    try:
        return int(value)
    except ValueError:
        errors.append(f"marker has non-integer {key}: {value}")
        return None


def parse_keys(path: Path, errors: list[str]) -> set[tuple[int, int, int, int]]:
    keys: set[tuple[int, int, int, int]] = set()
    lines = path.read_text(encoding="utf-8").splitlines()
    require(len(lines) == EXPECTED_PAGE_COUNT, f"keys.txt row count {len(lines)} != {EXPECTED_PAGE_COUNT}", errors)
    for index, line in enumerate(lines, start=1):
        parts = line.split()
        if len(parts) != 4:
            errors.append(f"keys.txt line {index} does not have four integers: {line!r}")
            continue
        try:
            keys.add(tuple(int(part) for part in parts))  # type: ignore[arg-type]
        except ValueError:
            errors.append(f"keys.txt line {index} has non-integer values: {line!r}")
    return keys


def expected_chunk_keys() -> set[tuple[int, int, int, int]]:
    return {(x, 0, z, 0) for z in range(64) for x in range(64)}


def check_source_files(errors: list[str]) -> dict[str, Any]:
    density = G14_SOURCE_ROOT / "density.f32"
    materials = G14_SOURCE_ROOT / "materials.u16"
    keys = G14_SOURCE_ROOT / "keys.txt"
    for path in (density, materials, keys):
        if not path.is_file():
            fail_missing_artifacts(path)

    density_size = density.stat().st_size
    material_size = materials.stat().st_size
    require(
        density_size == EXPECTED_DENSITY_BYTES,
        f"density.f32 size {density_size} != {EXPECTED_DENSITY_BYTES}",
        errors,
    )
    require(
        material_size == EXPECTED_MATERIAL_BYTES,
        f"materials.u16 size {material_size} != {EXPECTED_MATERIAL_BYTES}",
        errors,
    )

    actual_keys = parse_keys(keys, errors)
    expected_keys = expected_chunk_keys()
    missing = expected_keys - actual_keys
    extra = actual_keys - expected_keys
    require(not missing, f"keys.txt missing {len(missing)} expected chunk keys", errors)
    require(not extra, f"keys.txt has {len(extra)} unexpected chunk keys", errors)
    require(len(actual_keys) == EXPECTED_PAGE_COUNT, f"keys.txt unique key count {len(actual_keys)} != {EXPECTED_PAGE_COUNT}", errors)

    return {
        "density_bytes": density_size,
        "materials_bytes": material_size,
        "keys_bytes": keys.stat().st_size,
        "keys": len(actual_keys),
    }


def check_fixture(report: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    fixture = report.get("fixture")
    if not isinstance(fixture, dict):
        errors.append("report fixture is missing or not an object")
        return {}

    metadata = fixture.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("fixture metadata is missing or not an object")
        metadata = {}
    coverage = fixture.get("vertical_coverage")
    if not isinstance(coverage, dict):
        errors.append("fixture vertical_coverage is missing or not an object")
        coverage = {}

    require(report.get("implementation") == EXPECTED_IMPLEMENTATION, "report implementation mismatch", errors)
    require(fixture.get("profile") == EXPECTED_PROFILE, "fixture profile mismatch", errors)
    require(fixture.get("chunk_pages") == EXPECTED_PAGE_COUNT, "fixture chunk_pages mismatch", errors)
    require(fixture.get("source_writer") == EXPECTED_SOURCE_WRITER, "fixture source_writer mismatch", errors)
    require(metadata.get("pages") == EXPECTED_PAGE_COUNT, "metadata pages mismatch", errors)
    require(metadata.get("source_revision") == EXPECTED_SOURCE_REVISION, "metadata source_revision mismatch", errors)
    require(isinstance(metadata.get("sha256"), str) and bool(metadata.get("sha256")), "metadata sha256 missing", errors)

    lower_margin = float(coverage.get("lower_margin", -1.0))
    upper_margin = float(coverage.get("upper_margin", -1.0))
    required_lower = float(coverage.get("required_lower_margin", -1.0))
    required_upper = float(coverage.get("required_upper_margin", -1.0))
    require(required_lower == EXPECTED_REQUIRED_LOWER_MARGIN, "required lower margin mismatch", errors)
    require(required_upper == EXPECTED_REQUIRED_UPPER_MARGIN, "required upper margin mismatch", errors)
    require(lower_margin >= required_lower, "vertical lower margin is unsafe", errors)
    require(upper_margin >= required_upper, "vertical upper margin is unsafe", errors)
    require(
        float(coverage.get("active_vertical_min_y", 0.0)) <= float(coverage.get("surface_min_y", -1.0)),
        "surface_min_y is below active vertical range",
        errors,
    )
    require(
        float(coverage.get("surface_max_y", 0.0)) <= float(coverage.get("active_vertical_max_y", -1.0)),
        "surface_max_y is above active vertical range",
        errors,
    )

    return {
        "profile": fixture.get("profile"),
        "pages": metadata.get("pages"),
        "source_revision": metadata.get("source_revision"),
        "source_writer": fixture.get("source_writer"),
        "vertical_coverage": coverage,
    }


def check_engine_markers(report: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    engines = report.get("engines")
    if not isinstance(engines, list):
        errors.append("report engines is missing or not a list")
        return {"engines": 0}
    require(len(engines) == EXPECTED_ENGINE_COUNT, f"engine count {len(engines)} != {EXPECTED_ENGINE_COUNT}", errors)

    max_render = 0
    max_collision = 0
    edit_replacements = 0
    markers: list[str] = []
    engine_names: list[str] = []
    for index, engine in enumerate(engines, start=1):
        if not isinstance(engine, dict):
            errors.append(f"engine entry {index} is not an object")
            continue
        marker = engine.get("marker")
        if not isinstance(marker, str):
            errors.append(f"engine entry {index} missing marker")
            continue
        markers.append(marker)
        engine_name = engine.get("engine")
        if isinstance(engine_name, str):
            engine_names.append(engine_name)
        require(marker.startswith(G14_MARKER), f"engine entry {index} has wrong marker", errors)
        fields = marker_fields(marker)
        require(fields.get("profile") == EXPECTED_PROFILE, f"engine entry {index} profile mismatch", errors)
        pages = int_field(fields, "pages", errors)
        render_resources = int_field(fields, "max_render_resources", errors)
        collision_resources = int_field(fields, "max_collision_resources", errors)
        replacements = int_field(fields, "edit_replacements", errors)
        if pages is not None:
            require(pages == EXPECTED_PAGE_COUNT, f"engine entry {index} pages mismatch", errors)
        if render_resources is not None:
            max_render = max(max_render, render_resources)
            require(
                render_resources <= EXPECTED_MAX_ACTIVE_RESOURCES,
                f"engine entry {index} render resources exceed budget",
                errors,
            )
        if collision_resources is not None:
            max_collision = max(max_collision, collision_resources)
            require(
                collision_resources <= EXPECTED_MAX_ACTIVE_RESOURCES,
                f"engine entry {index} collision resources exceed budget",
                errors,
            )
        if replacements is not None:
            edit_replacements += replacements
            require(replacements > 0, f"engine entry {index} did not replace edited terrain", errors)

    return {
        "engines": len(engines),
        "engine_names": engine_names,
        "markers": markers,
        "max_render_resources": max_render,
        "max_collision_resources": max_collision,
        "edit_replacements": edit_replacements,
    }


def main() -> None:
    if not G14_REPORT.is_file():
        fail_missing_artifacts(G14_REPORT)
    report = json.loads(G14_REPORT.read_text(encoding="utf-8"))
    errors: list[str] = []

    source_summary = check_source_files(errors)
    fixture_summary = check_fixture(report, errors)
    engine_summary = check_engine_markers(report, errors)

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)

    G15_ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    G15_REPORT.write_text(
        json.dumps(
            {
                "implementation": "g14_scale_telemetry_guard",
                "source": source_summary,
                "fixture": fixture_summary,
                "runtime": engine_summary,
                "g14_report": str(G14_REPORT.relative_to(ROOT).as_posix()),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"{G15_MARKER} "
        f"pages={EXPECTED_PAGE_COUNT} engines={engine_summary['engines']} "
        f"density_bytes={source_summary['density_bytes']} materials_bytes={source_summary['materials_bytes']} "
        f"max_render_resources={engine_summary['max_render_resources']} "
        f"max_collision_resources={engine_summary['max_collision_resources']} "
        f"report={G15_REPORT.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
