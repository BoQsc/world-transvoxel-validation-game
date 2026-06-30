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


ARTIFACT_ROOT = ROOT / "artifacts" / "g51_material_texture_pipeline_quality"
PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g51_material_texture_pipeline_quality.gd"
MARKER = "WT_VALIDATION_G51_MATERIAL_TEXTURE_PIPELINE_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G51_MATERIAL_TEXTURE_PIPELINE_SMOKE_PASS"
TERRAIN_REPO = ROOT.parent / "world-transvoxel-terrain"
MAX_RUNTIME_SECONDS = 120.0
MAX_TEXTURE_RESOLUTION = 16
MAX_TEXTURE_BYTES = 4 * 1024
MIN_COLORED_SAMPLES = 1000


def parse_marker(marker_line: str) -> dict[str, str]:
    return dict(token.split("=", 1) for token in marker_line.split()[1:] if "=" in token)


def reset_runtime_state(project: Path) -> None:
    path = project / PROJECT_WORLD_ROOT
    if path.exists():
        shutil.rmtree(path)


def static_audit() -> dict[str, object]:
    required = {
        TERRAIN_REPO / "addons/world_transvoxel_terrain/material/wt_terrain_material_profile.gd": (
            "terrain_material_profile_contract_v1",
            "texture_bytes",
            "material_ids_csv",
            "deterministic_palette",
        ),
        TERRAIN_REPO / "addons/world_transvoxel_terrain/material/wt_terrain_material_applicator.gd": (
            "terrain_material_texture_pipeline_v1",
            "get_material_quality_summary",
            "texture_checksum",
            "MAX_STANDARD_TEXTURE_BYTES",
        ),
        TERRAIN_REPO / "addons/world_transvoxel_terrain/material/wt_terrain_palette.gdshader": (
            "UV2.x",
            "checker_texture",
            "material_4_color",
        ),
        ROOT / "tests/g51_material_texture_pipeline_quality.gd": (
            MARKER,
            "material_instance_stable=1",
            "MAX_TEXTURE_BYTES",
            "STREAM_SAMPLES",
        ),
    }
    errors: list[str] = []
    for path, phrases in required.items():
        if not path.is_file():
            errors.append(f"missing G51 input: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{path} missing phrase: {phrase}")
        if path.suffix in {".gd", ".py", ".gdshader"} and len(text.splitlines()) > 300:
            errors.append(f"G51 source file exceeds line limit: {path}")
    if errors:
        raise RuntimeError("; ".join(errors))
    return {"implementation": "material_texture_pipeline_quality", "profile": PROFILE_ID}


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
    (ARTIFACT_ROOT / f"godot-{version}-g51.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g51.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G51 material texture pipeline failed on {version}")
    if duration_seconds > MAX_RUNTIME_SECONDS:
        raise RuntimeError(f"G51 runtime exceeded {MAX_RUNTIME_SECONDS:.0f}s on {version}: {duration_seconds:.3f}s")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    fields = parse_marker(marker_line)
    if fields.get("profile") != PROFILE_ID or fields.get("material_instance_stable") != "1":
        raise RuntimeError(f"G51 marker identity fields invalid: {marker_line}")
    if int(fields.get("texture_resolution", "999")) > MAX_TEXTURE_RESOLUTION:
        raise RuntimeError(f"G51 texture resolution exceeds standard: {marker_line}")
    if int(fields.get("texture_bytes", "999999")) > MAX_TEXTURE_BYTES:
        raise RuntimeError(f"G51 texture bytes exceed standard: {marker_line}")
    if int(fields.get("capture_colored_samples", "0")) < MIN_COLORED_SAMPLES:
        raise RuntimeError(f"G51 material capture coverage too small: {marker_line}")
    if int(fields.get("materialized_after_stream", "0")) < 25 or int(fields.get("stream_windows", "0")) != 2:
        raise RuntimeError(f"G51 streaming material coverage invalid: {marker_line}")
    return {
        "engine": version,
        "duration_seconds": duration_seconds,
        "marker": marker_line,
        "fields": fields,
        "post_run_budget": assert_compact_project_budget(project),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run G51 material texture pipeline quality validation.")
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
    report_path = ARTIFACT_ROOT / "g51_material_texture_pipeline_quality_report.json"
    report_path.write_text(
        json.dumps({"project": str(project), "lock": lock, "audit": audit, "engines": results}, indent=2) + "\n",
        encoding="utf-8",
    )
    max_duration = max(float(result["duration_seconds"]) for result in results)
    print(
        f"{SUMMARY_MARKER} profile={PROFILE_ID} engines={len(results)} "
        f"texture_resolution={MAX_TEXTURE_RESOLUTION} texture_bytes_max={MAX_TEXTURE_BYTES} "
        f"material_instance_stable=1 max_engine_seconds={max_duration:.3f} "
        f"quality_track=runtime_terrain dense_world_files=0 report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
