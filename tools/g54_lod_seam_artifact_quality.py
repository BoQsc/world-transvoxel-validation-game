#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

from compose_validation_project import ROOT, WORLD_TRANSVOXEL_REPO, compose
from g0_install_run_smoke import discover_engines, has_godot_error, run_import
from g8_runtime_active_window_smoke import build_world_transvoxel


ARTIFACT_ROOT = ROOT / "artifacts" / "g54_lod_seam_artifact_quality"
PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g54_lod_seam_artifact_quality.gd"
MARKER = "WT_VALIDATION_G54_LOD_SEAM_ARTIFACT_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G54_LOD_SEAM_ARTIFACT_SMOKE_PASS"
FIXTURE_ROOT = WORLD_TRANSVOXEL_REPO / "build" / "production-lifecycle-fixture"
TRANSITION_MANIFEST = FIXTURE_ROOT / "transition.wtworld"
MAX_RUNTIME_SECONDS = 150.0


def parse_marker(marker_line: str) -> dict[str, str]:
    return dict(token.split("=", 1) for token in marker_line.split()[1:] if "=" in token)


def native_test_path(configuration: str, name: str) -> Path:
    scripts_path = str(WORLD_TRANSVOXEL_REPO / "scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    from wt_script_common import native_test_path as resolve_native_test_path

    return resolve_native_test_path(configuration, name)


def prepare_transition_fixture(reuse_fixture: bool) -> dict[str, object]:
    if reuse_fixture and TRANSITION_MANIFEST.is_file():
        return {"reused": True, "fixture_manifest": str(TRANSITION_MANIFEST)}
    executable = native_test_path("template_release", "test_wt_production_lifecycle")
    if not executable.is_file():
        raise RuntimeError(f"missing production lifecycle fixture generator: {executable}")
    if FIXTURE_ROOT.exists():
        shutil.rmtree(FIXTURE_ROOT)
    result = subprocess.run(
        [str(executable), "--write-godot-fixture", str(FIXTURE_ROOT)],
        cwd=WORLD_TRANSVOXEL_REPO,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=180,
    )
    (ARTIFACT_ROOT / "fixture-generation.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / "fixture-generation.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or "PRODUCTION_TRANSITION_FIXTURE_PASS" not in combined:
        raise RuntimeError("G54 transition fixture generation failed")
    if not TRANSITION_MANIFEST.is_file():
        raise RuntimeError(f"G54 transition manifest was not written: {TRANSITION_MANIFEST}")
    return {"reused": False, "generator": str(executable), "fixture_manifest": str(TRANSITION_MANIFEST)}


def run_native_lod_streaming() -> dict[str, object]:
    executable = native_test_path("template_release", "test_wt_production_lod_streaming")
    if not executable.is_file():
        raise RuntimeError(f"missing native LOD streaming test: {executable}")
    result = subprocess.run(
        [str(executable)],
        cwd=WORLD_TRANSVOXEL_REPO,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=180,
    )
    (ARTIFACT_ROOT / "native-lod-streaming.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / "native-lod-streaming.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or "PRODUCTION_LOD_STREAMING_PASS" not in combined:
        raise RuntimeError("G54 native production LOD streaming proof failed")
    marker = next(line for line in combined.splitlines() if line.startswith("PRODUCTION_LOD_STREAMING_PASS"))
    return {"executable": str(executable), "marker": marker}


def static_audit() -> dict[str, object]:
    required = {
        ROOT / "tests/g54_lod_seam_artifact_quality.gd": (
            MARKER,
            "transition.wtworld",
            "maximum_lod",
            "_submit_seam_edit",
            "MAX_BOUNDARY_Y_GAP",
        ),
        ROOT / "tests/g54_lod_seam_artifact_audit.gd": (
            "_audit_lod_seams",
            "boundary_epsilon",
            "max_boundary_y_gap",
            "diagonal_edges",
        ),
        WORLD_TRANSVOXEL_REPO / "tests/native/test_wt_production_lod_streaming.cpp": (
            "PRODUCTION_LOD_STREAMING_PASS",
            "transition_mesh_completions",
            "transition-mask change",
        ),
        WORLD_TRANSVOXEL_REPO / "tests/native/wt_production_world_fixture.cpp": (
            "wt_write_production_transition_fixture",
            "transition.wtworld",
            "keys.reserve(28)",
        ),
        WORLD_TRANSVOXEL_REPO / "addons/world_transvoxel/src/streaming/wt_lod_map.cpp": (
            "transition_mask",
            "lod_difference",
        ),
    }
    errors: list[str] = []
    for path, phrases in required.items():
        if not path.is_file():
            errors.append(f"missing G54 audit input: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{path} missing phrase: {phrase}")
    if errors:
        raise RuntimeError("; ".join(errors))
    return {"implementation": "lod_seam_artifact_quality", "pages": 28, "active_capacity": 40}


def run_runtime(project: Path, version: str, engine: Path, headless: bool) -> dict[str, object]:
    command = [str(engine)]
    if headless:
        command.append("--headless")
    command.extend(["--path", str(project), "--script", SCRIPT])
    started_at = time.perf_counter()
    result = subprocess.run(
        command,
        cwd=project,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=240,
    )
    duration = time.perf_counter() - started_at
    (ARTIFACT_ROOT / f"godot-{version}-g54.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g54.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G54 LOD seam/artifact runtime failed on {version}")
    if duration > MAX_RUNTIME_SECONDS:
        raise RuntimeError(f"G54 runtime exceeded {MAX_RUNTIME_SECONDS:.0f}s on {version}: {duration:.3f}s")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    fields = parse_marker(marker_line)
    for key in ("lod0", "lod1", "seam_pairs", "edited_seam_pairs", "diagonal_edges", "edited_diagonal_edges"):
        if int(fields.get(key, "0")) <= 0:
            raise RuntimeError(f"G54 marker field {key} did not prove coverage: {marker_line}")
    if int(fields.get("transition_completions", "0")) < 2 or int(fields.get("edit_replacements", "0")) <= 0:
        raise RuntimeError(f"G54 transition/edit evidence invalid: {marker_line}")
    if float(fields.get("max_boundary_gap", "999")) > 0.75 or float(fields.get("edited_boundary_gap", "999")) > 0.75:
        raise RuntimeError(f"G54 seam boundary gap exceeded budget: {marker_line}")
    return {"engine": version, "duration_seconds": duration, "marker": marker_line, "fields": fields}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run G54 LOD seam/artifact quality validation.")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--reuse-fixture", action="store_true")
    parser.add_argument("--windowed", action="store_true")
    arguments = parser.parse_args()

    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    audit = static_audit()
    build_world_transvoxel(arguments.skip_build)
    fixture = prepare_transition_fixture(arguments.reuse_fixture)
    native = run_native_lod_streaming()
    project = arguments.project.resolve()
    lock = compose(project)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_import(project, version, engine)
        results.append(run_runtime(project, version, engine, not arguments.windowed))
    report_path = ARTIFACT_ROOT / "g54_lod_seam_artifact_quality_report.json"
    report_path.write_text(
        json.dumps({"project": str(project), "lock": lock, "audit": audit, "fixture": fixture, "native": native, "engines": results}, indent=2) + "\n",
        encoding="utf-8",
    )
    max_duration = max(float(result["duration_seconds"]) for result in results)
    print(
        f"{SUMMARY_MARKER} engines={len(results)} pages=28 active_capacity=40 "
        f"max_engine_seconds={max_duration:.3f} dense_world_files=0 "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
