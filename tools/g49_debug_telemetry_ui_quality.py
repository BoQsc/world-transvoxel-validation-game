#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time

from compose_validation_project import ROOT, compose
from g0_install_run_smoke import discover_engines, has_godot_error
from g8_runtime_active_window_smoke import build_world_transvoxel
from g19_compact_2k_on_demand_smoke import (
    PROFILE_ID,
    PROJECT_WORLD_ROOT,
    assert_compact_project_budget,
)
from prepare_human_playtest import pin_scene_profile, run_project_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g49_debug_telemetry_ui_quality"
PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g49_debug_telemetry_ui_quality.gd"
MARKER = "WT_VALIDATION_G49_DEBUG_TELEMETRY_UI_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G49_DEBUG_TELEMETRY_UI_SMOKE_PASS"
TELEMETRY_RELATIVE = Path("artifacts/g49_debug_telemetry_ui_quality/debug_telemetry.json")
MAX_RUNTIME_SECONDS = 90.0
REQUIRED_CATEGORIES = {
    "active_chunks",
    "queues",
    "frame_update",
    "edit_state",
    "material_state",
    "storage_state",
}


def parse_marker(marker: str) -> dict[str, str]:
    return dict(token.split("=", 1) for token in marker.split()[1:] if "=" in token)


def reset_runtime_state(project: Path) -> None:
    path = project / PROJECT_WORLD_ROOT
    if path.exists():
        shutil.rmtree(path)


def static_audit() -> dict[str, object]:
    required = {
        "scripts/validation_debug_telemetry_overlay.gd": [
            "validation_debug_telemetry_overlay_v1",
            "active_chunks",
            "frame_update",
            "export_debug_telemetry",
        ],
        "scenes/validation_playtest.tscn": [
            "ValidationDebugTelemetryOverlay",
            "validation_debug_telemetry_overlay.gd",
        ],
    }
    errors: list[str] = []
    for relative, phrases in required.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing G49 telemetry file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{relative} missing phrase: {phrase}")
    overlay = (ROOT / "scripts/validation_debug_telemetry_overlay.gd").read_text(encoding="utf-8")
    if "get_backend_terrain" in overlay or "get_backend_world_state_name" in overlay:
        errors.append("G49 overlay uses backend internals instead of public telemetry")
    if errors:
        raise RuntimeError("; ".join(errors))
    return {"overlay": "validation_debug_telemetry_overlay_v1", "categories": len(REQUIRED_CATEGORIES)}


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
        timeout=180,
    )
    duration_seconds = time.perf_counter() - started_at
    (ARTIFACT_ROOT / f"godot-{version}-g49.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g49.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G49 debug telemetry UI failed on {version}")
    if duration_seconds > MAX_RUNTIME_SECONDS:
        raise RuntimeError(f"G49 runtime exceeded {MAX_RUNTIME_SECONDS:.0f}s on {version}: {duration_seconds:.3f}s")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    fields = parse_marker(marker_line)
    if fields.get("profile") != PROFILE_ID or fields.get("overlay") != "1" or fields.get("exported") != "1":
        raise RuntimeError(f"G49 marker fields invalid: {marker_line}")
    if int(fields.get("categories", "0")) < len(REQUIRED_CATEGORIES):
        raise RuntimeError(f"G49 category coverage too small: {marker_line}")
    if int(fields.get("active_chunks", "0")) != 25 or int(fields.get("frame_samples", "0")) < 10:
        raise RuntimeError(f"G49 active/frame telemetry invalid: {marker_line}")
    telemetry_path = project / TELEMETRY_RELATIVE
    if not telemetry_path.is_file():
        raise RuntimeError(f"G49 telemetry export missing: {telemetry_path}")
    telemetry = json.loads(telemetry_path.read_text(encoding="utf-8"))
    if not REQUIRED_CATEGORIES.issubset(set(telemetry.get("categories", []))):
        raise RuntimeError(f"G49 telemetry JSON categories incomplete: {telemetry}")
    return {
        "engine": version,
        "duration_seconds": duration_seconds,
        "marker": marker_line,
        "fields": fields,
        "telemetry": telemetry,
        "post_run_budget": assert_compact_project_budget(project),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run debug telemetry UI quality validation.")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--skip-build", action="store_true")
    arguments = parser.parse_args()

    audit = static_audit()
    build_world_transvoxel(arguments.skip_build)
    project = arguments.project.resolve()
    lock = compose(project)
    pin_scene_profile(project, PROFILE_ID)
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_project_import(project, version, engine, ARTIFACT_ROOT)
        results.append(run_runtime(project, version, engine))
    report_path = ARTIFACT_ROOT / "g49_debug_telemetry_ui_quality_report.json"
    report_path.write_text(
        json.dumps({"project": str(project), "lock": lock, "audit": audit, "engines": results}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"{SUMMARY_MARKER} profile={PROFILE_ID} engines={len(results)} categories={len(REQUIRED_CATEGORIES)} "
        f"overlay=1 exported=1 quality_track=runtime_terrain dense_world_files=0 "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
