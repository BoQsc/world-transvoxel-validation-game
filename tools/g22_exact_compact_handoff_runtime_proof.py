#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time

from g0_install_run_smoke import discover_engines, has_godot_error
from g8_runtime_active_window_smoke import build_world_transvoxel
from g19_compact_2k_on_demand_smoke import (
    G19_PROJECT,
    PROJECT_WORLD_ROOT,
    assert_compact_project_budget,
)
from g21_compact_2k_human_handoff import MARKER as G21_MARKER
from g21_compact_2k_human_handoff import PROFILE_ID, prepare_project
from prepare_human_playtest import run_project_import


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "artifacts" / "g22_exact_compact_handoff_runtime_proof"
SCRIPT = "res://tests/g22_exact_compact_handoff_runtime_proof.gd"
PROJECT_CAPTURE_ROOT = Path("artifacts") / "g22_exact_compact_handoff_runtime_proof"
MARKER = "WT_VALIDATION_G22_EXACT_COMPACT_HANDOFF_RUNTIME_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G22_EXACT_COMPACT_HANDOFF_RUNTIME_SMOKE_PASS"
MAX_LOAD_TO_PLAY_SECONDS = 30.0


def marker_value(marker: str, key: str) -> str:
    prefix = f"{key}="
    for token in marker.split():
        if token.startswith(prefix):
            return token[len(prefix):]
    return ""


def remove_project_runtime_artifacts(project: Path) -> None:
    path = project / PROJECT_CAPTURE_ROOT
    if path.exists():
        path.relative_to(project)
        shutil.rmtree(path)


def copy_runtime_artifacts(project: Path, version: str) -> dict[str, object]:
    source = project / PROJECT_CAPTURE_ROOT
    if not source.is_dir():
        raise RuntimeError(f"G22 runtime artifact directory missing: {source}")
    target = ARTIFACT_ROOT / f"godot-{version}"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    captures: list[str] = []
    for capture in sorted(source.glob("*.png")):
        copied = target / capture.name
        copied.write_bytes(capture.read_bytes())
        captures.append(str(copied))
    metrics_source = source / "runtime_metrics.json"
    if not metrics_source.is_file():
        raise RuntimeError(f"G22 runtime metrics missing: {metrics_source}")
    metrics = json.loads(metrics_source.read_text(encoding="utf-8"))
    (target / "runtime_metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "capture_count": len(captures),
        "captures": captures,
        "metrics": metrics,
        "artifact_dir": str(target),
    }


def validate_marker(marker: str) -> None:
    if not marker.startswith(MARKER):
        raise RuntimeError(f"G22 marker mismatch: {marker}")
    if marker_value(marker, "profile") != PROFILE_ID:
        raise RuntimeError(f"G22 profile mismatch: {marker}")
    if marker_value(marker, "pages") != "16384":
        raise RuntimeError(f"G22 page count mismatch: {marker}")
    if int(marker_value(marker, "max_render_resources")) > 25:
        raise RuntimeError(f"G22 render budget exceeded: {marker}")
    if int(marker_value(marker, "max_collision_resources")) > 25:
        raise RuntimeError(f"G22 collision budget exceeded: {marker}")
    if int(marker_value(marker, "captures")) < 3:
        raise RuntimeError(f"G22 did not capture enough images: {marker}")
    if int(marker_value(marker, "construct_verified")) != 1:
        raise RuntimeError(f"G22 construct/place was not verified: {marker}")
    if int(marker_value(marker, "pending_retirements")) != 0:
        raise RuntimeError(f"G22 pending retirements not settled: {marker}")
    if int(marker_value(marker, "render_fading_resources")) != 0:
        raise RuntimeError(f"G22 render fading resources not settled: {marker}")
    if marker_value(marker, "dense_world_files") != "0":
        raise RuntimeError(f"G22 dense world files were detected: {marker}")


def validate_runtime_artifacts(artifacts: dict[str, object]) -> None:
    if int(artifacts["capture_count"]) < 3:
        raise RuntimeError(f"G22 expected at least 3 captures: {artifacts}")
    metrics = artifacts.get("metrics", {})
    if not isinstance(metrics, dict):
        raise RuntimeError(f"G22 metrics are invalid: {artifacts}")
    if metrics.get("profile") != PROFILE_ID:
        raise RuntimeError(f"G22 metrics profile mismatch: {metrics}")
    if int(metrics.get("page_count", -1)) != 16384:
        raise RuntimeError(f"G22 metrics page count mismatch: {metrics}")
    if int(metrics.get("max_render_resources", 999)) > 25:
        raise RuntimeError(f"G22 metrics render budget exceeded: {metrics}")
    if int(metrics.get("max_collision_resources", 999)) > 25:
        raise RuntimeError(f"G22 metrics collision budget exceeded: {metrics}")
    if int(metrics.get("final_pending_chunk_retirements", 999)) != 0:
        raise RuntimeError(f"G22 metrics pending retirements not settled: {metrics}")
    if int(metrics.get("final_render_fading_resources", 999)) != 0:
        raise RuntimeError(f"G22 metrics render fading not settled: {metrics}")
    if not bool(metrics.get("construct_verified", False)):
        raise RuntimeError(f"G22 metrics construct/place missing: {metrics}")


def run_runtime(project: Path, version: str, engine: Path, headless: bool) -> dict[str, object]:
    command = [str(engine)]
    if headless:
        command.append("--headless")
    command.extend(["--path", str(project), "--script", SCRIPT])
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    remove_project_runtime_artifacts(project)
    started_at = time.perf_counter()
    result = subprocess.run(
        command,
        cwd=project,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=900,
    )
    duration_seconds = time.perf_counter() - started_at
    (ARTIFACT_ROOT / f"godot-{version}-g22.stdout.txt").write_text(
        result.stdout,
        encoding="utf-8",
    )
    (ARTIFACT_ROOT / f"godot-{version}-g22.stderr.txt").write_text(
        result.stderr,
        encoding="utf-8",
    )
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G22 exact compact handoff runtime proof failed on {version}")
    if duration_seconds > MAX_LOAD_TO_PLAY_SECONDS:
        raise RuntimeError(
            "G22 exact compact handoff runtime exceeded load-to-play ceiling "
            f"on {version}: {duration_seconds:.3f}s > {MAX_LOAD_TO_PLAY_SECONDS:.3f}s"
        )
    marker = next(line for line in combined.splitlines() if line.startswith(MARKER))
    validate_marker(marker)
    artifacts = copy_runtime_artifacts(project, version)
    validate_runtime_artifacts(artifacts)
    return {
        "engine": version,
        "executable": str(engine),
        "duration_seconds": duration_seconds,
        "marker": marker,
        **artifacts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run exact runtime proof on the compact G21 handoff project."
    )
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=G19_PROJECT)
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run Godot headless. Not recommended for G22 because PNG capture needs a render texture.",
    )
    parser.add_argument(
        "--windowed",
        action="store_true",
        help="Deprecated compatibility flag; G22 runs windowed by default for PNG capture.",
    )
    parser.add_argument("--skip-build", action="store_true")
    arguments = parser.parse_args()

    build_world_transvoxel(arguments.skip_build)
    project = arguments.project.resolve()
    lock, scene, handoff_runtime = prepare_project(project)
    pre_run_budget = assert_compact_project_budget(project)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_project_import(project, version, engine, ARTIFACT_ROOT)
        results.append(run_runtime(project, version, engine, arguments.headless))
    post_run_budget = assert_compact_project_budget(project)
    max_engine_seconds = max(float(result["duration_seconds"]) for result in results)
    capture_count = sum(int(result["capture_count"]) for result in results)
    report_path = ARTIFACT_ROOT / "g22_exact_compact_handoff_runtime_proof_report.json"
    report_path.write_text(
        json.dumps(
            {
                "project": str(project),
                "scene": str(scene),
                "scene_res": "res://scenes/validation_playtest.tscn",
                "profile": PROFILE_ID,
                "g21_marker": G21_MARKER,
                "lock": lock,
                "handoff_runtime": handoff_runtime,
                "pre_run_budget": pre_run_budget,
                "post_run_budget": post_run_budget,
                "engines": results,
                "implementation": "exact_compact_handoff_runtime_proof",
                "budget": {
                    "max_load_to_play_seconds": MAX_LOAD_TO_PLAY_SECONDS,
                    "active_resource_budget": 25,
                    "dense_source_artifacts": False,
                    "dense_world_artifacts": False,
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"{SUMMARY_MARKER} engines={len(results)} "
        f"captures={capture_count} "
        f"max_file_bytes={post_run_budget['max_file_bytes']} "
        f"total_bytes={post_run_budget['total_bytes']} "
        f"max_engine_seconds={max_engine_seconds:.3f} "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
