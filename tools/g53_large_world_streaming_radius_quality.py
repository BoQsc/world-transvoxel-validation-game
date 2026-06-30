#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time

from compose_validation_project import ROOT, WORLD_TRANSVOXEL_REPO, compose
from g0_install_run_smoke import discover_engines, has_godot_error
from g8_runtime_active_window_smoke import build_world_transvoxel
from g19_compact_2k_on_demand_smoke import PROFILE_ID, PROJECT_WORLD_ROOT, assert_compact_project_budget
from prepare_human_playtest import run_project_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g53_large_world_streaming_radius_quality"
PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g53_large_world_streaming_radius_quality.gd"
MARKER = "WT_VALIDATION_G53_LARGE_WORLD_STREAMING_RADIUS_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G53_LARGE_WORLD_STREAMING_RADIUS_SMOKE_PASS"
EXPECTED_RADII = "1,2,4,6"
EXPECTED_RESOURCES = "9,25,81,169"
ACTIVE_RESOURCE_CAPACITY = 256
MAX_RUNTIME_SECONDS = 150.0


def parse_marker(marker_line: str) -> dict[str, str]:
    return dict(token.split("=", 1) for token in marker_line.split()[1:] if "=" in token)


def reset_runtime_state(project: Path) -> None:
    path = project / PROJECT_WORLD_ROOT
    if path.exists():
        shutil.rmtree(path)


def static_audit() -> dict[str, object]:
    required = {
        ROOT / "tests/g53_large_world_streaming_radius_quality.gd": (
            MARKER,
            "RADIUS_STEPS",
            "ACTIVE_RESOURCE_CAPACITY",
            "_verify_radius_boundary",
            "_visible_mesh_spread",
            "outside_radius_absent",
        ),
        WORLD_TRANSVOXEL_REPO / "addons/world_transvoxel/src/api/world_transvoxel_terrain_streaming.cpp": (
            "radius_chunks",
            "update_viewer",
        ),
        WORLD_TRANSVOXEL_REPO / "addons/world_transvoxel/src/services/wt_read_only_world_runtime.cpp": (
            "valid_radius",
            "demand_capacity_per_viewer",
            "candidate_plan.demands",
        ),
    }
    errors: list[str] = []
    for path, phrases in required.items():
        if not path.is_file():
            errors.append(f"missing G53 input: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{path} missing phrase: {phrase}")
        if path.suffix in {".gd", ".py"} and len(text.splitlines()) > 300:
            errors.append(f"G53 source file exceeds line limit: {path}")
    if errors:
        raise RuntimeError("; ".join(errors))
    return {
        "implementation": "large_world_streaming_radius_quality",
        "profile": PROFILE_ID,
        "radii": EXPECTED_RADII,
        "active_capacity": ACTIVE_RESOURCE_CAPACITY,
    }


def run_runtime(project: Path, version: str, engine: Path) -> dict[str, object]:
    reset_runtime_state(project)
    started_at = time.perf_counter()
    result = subprocess.run(
        [str(engine), "--path", str(project), "--script", SCRIPT],
        cwd=project,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=240,
    )
    duration_seconds = time.perf_counter() - started_at
    (ARTIFACT_ROOT / f"godot-{version}-g53.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g53.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G53 large-world streaming radius failed on {version}")
    if duration_seconds > MAX_RUNTIME_SECONDS:
        raise RuntimeError(f"G53 runtime exceeded {MAX_RUNTIME_SECONDS:.0f}s on {version}: {duration_seconds:.3f}s")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    fields = parse_marker(marker_line)
    if fields.get("profile") != PROFILE_ID or fields.get("radii") != EXPECTED_RADII:
        raise RuntimeError(f"G53 marker identity/radius fields invalid: {marker_line}")
    if fields.get("expected_resources") != EXPECTED_RESOURCES:
        raise RuntimeError(f"G53 expected resource fields invalid: {marker_line}")
    if int(fields.get("max_active_resources", "999999")) > ACTIVE_RESOURCE_CAPACITY:
        raise RuntimeError(f"G53 exceeded active resource capacity: {marker_line}")
    if int(fields.get("inside_edge_ready", "0")) != 16 or int(fields.get("outside_radius_absent", "0")) != 16:
        raise RuntimeError(f"G53 radius boundary coverage invalid: {marker_line}")
    if float(fields.get("max_span_x", "0")) <= float(fields.get("min_span_x", "0")):
        raise RuntimeError(f"G53 visible span did not grow: {marker_line}")
    return {
        "engine": version,
        "duration_seconds": duration_seconds,
        "marker": marker_line,
        "fields": fields,
        "post_run_budget": assert_compact_project_budget(project),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run G53 large-world streaming radius quality validation.")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--skip-build", action="store_true")
    arguments = parser.parse_args()

    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    audit = static_audit()
    build_world_transvoxel(arguments.skip_build)
    project = arguments.project.resolve()
    lock = compose(project)
    reset_runtime_state(project)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_project_import(project, version, engine, ARTIFACT_ROOT)
        results.append(run_runtime(project, version, engine))
    report_path = ARTIFACT_ROOT / "g53_large_world_streaming_radius_quality_report.json"
    report_path.write_text(
        json.dumps({"project": str(project), "lock": lock, "audit": audit, "engines": results}, indent=2) + "\n",
        encoding="utf-8",
    )
    max_duration = max(float(result["duration_seconds"]) for result in results)
    print(
        f"{SUMMARY_MARKER} profile={PROFILE_ID} engines={len(results)} radii={EXPECTED_RADII} "
        f"expected_resources={EXPECTED_RESOURCES} active_capacity={ACTIVE_RESOURCE_CAPACITY} "
        f"max_engine_seconds={max_duration:.3f} dense_world_files=0 "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
