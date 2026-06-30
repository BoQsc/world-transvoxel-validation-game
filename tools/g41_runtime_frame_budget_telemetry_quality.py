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
from g19_compact_2k_on_demand_smoke import PROFILE_ID, PROJECT_WORLD_ROOT, assert_compact_project_budget
from prepare_human_playtest import pin_scene_profile, run_project_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g41_runtime_frame_budget_telemetry_quality"
PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g41_runtime_frame_budget_telemetry_quality.gd"
MARKER = "WT_VALIDATION_G41_RUNTIME_FRAME_BUDGET_TELEMETRY_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G41_RUNTIME_FRAME_BUDGET_TELEMETRY_SMOKE_PASS"
MAX_RUNTIME_SECONDS = 90.0
MAX_AVG_FRAME_MS = 80.0
MAX_FRAME_SPIKE_MS = 1000.0


def parse_marker(marker: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for token in marker.split()[1:]:
        if "=" in token:
            key, value = token.split("=", 1)
            fields[key] = value
    return fields


def reset_compact_runtime_state(project: Path) -> None:
    path = project / PROJECT_WORLD_ROOT
    if path.exists():
        shutil.rmtree(path)


def run_runtime(project: Path, version: str, engine: Path) -> dict[str, object]:
    reset_compact_runtime_state(project)
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
    (ARTIFACT_ROOT / f"godot-{version}-g41.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g41.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G41 runtime frame budget telemetry quality failed on {version}")
    if duration_seconds > MAX_RUNTIME_SECONDS:
        raise RuntimeError(f"G41 runtime exceeded {MAX_RUNTIME_SECONDS:.0f}s on {version}: {duration_seconds:.3f}s")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    fields = parse_marker(marker_line)
    if fields.get("profile") != PROFILE_ID or fields.get("dense_world_files") != "0":
        raise RuntimeError(f"G41 marker fields invalid: {marker_line}")
    if int(fields.get("phases", "0")) < 5 or int(fields.get("total_frames", "0")) < 240:
        raise RuntimeError(f"G41 telemetry coverage too small: {marker_line}")
    if float(fields.get("max_avg_frame_ms", "9999")) > MAX_AVG_FRAME_MS:
        raise RuntimeError(f"G41 average frame budget exceeded: {marker_line}")
    if float(fields.get("max_frame_ms", "9999")) > MAX_FRAME_SPIKE_MS:
        raise RuntimeError(f"G41 frame spike budget exceeded: {marker_line}")
    if int(fields.get("movement_samples", "0")) < 2 or int(fields.get("edits", "0")) != 2:
        raise RuntimeError(f"G41 movement/edit coverage invalid: {marker_line}")
    if int(fields.get("reload_ready_frames", "9999")) > 1800:
        raise RuntimeError(f"G41 reload did not reach ready within budget: {marker_line}")
    for field in ("max_render_resources", "max_collision_resources", "max_active_records"):
        if int(fields.get(field, "999")) > 50:
            raise RuntimeError(f"G41 active resource field exceeded transient budget: {field} in {marker_line}")
    if int(fields.get("max_render_fading_resources", "1")) != 0:
        raise RuntimeError(f"G41 render fade/blink resources observed: {marker_line}")
    telemetry = project / "artifacts" / "g41_runtime_frame_budget_telemetry_quality" / "frame_telemetry.json"
    if not telemetry.is_file():
        raise RuntimeError(f"G41 telemetry JSON missing: {telemetry}")
    return {
        "engine": version,
        "executable": str(engine),
        "duration_seconds": duration_seconds,
        "marker": marker_line,
        "fields": fields,
        "telemetry": json.loads(telemetry.read_text(encoding="utf-8")),
        "post_run_budget": assert_compact_project_budget(project),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run runtime frame budget telemetry quality validation.")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--skip-build", action="store_true")
    arguments = parser.parse_args()

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
    max_frame = max(float(result["fields"]["max_frame_ms"]) for result in results)
    max_avg = max(float(result["fields"]["max_avg_frame_ms"]) for result in results)
    min_frames = min(int(result["fields"]["total_frames"]) for result in results)
    min_phases = min(int(result["fields"]["phases"]) for result in results)
    report_path = ARTIFACT_ROOT / "g41_runtime_frame_budget_telemetry_quality_report.json"
    report_path.write_text(json.dumps({
        "project": str(project),
        "lock": lock,
        "profile": PROFILE_ID,
        "engines": results,
        "max_frame_ms": max_frame,
        "max_avg_frame_ms": max_avg,
        "min_total_frames": min_frames,
        "min_phases": min_phases,
        "implementation": "runtime_frame_budget_telemetry_quality",
    }, indent=2) + "\n", encoding="utf-8")
    print(
        f"{SUMMARY_MARKER} profile={PROFILE_ID} engines={len(results)} phases={min_phases} "
        f"total_frames={min_frames} max_frame_ms={max_frame:.3f} max_avg_frame_ms={max_avg:.3f} "
        "quality_track=runtime_terrain dense_world_files=0 "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
