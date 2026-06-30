#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import time

from compose_validation_project import ROOT, compose
from g0_install_run_smoke import discover_engines, has_godot_error
from g8_runtime_active_window_smoke import build_world_transvoxel
from g19_compact_2k_on_demand_smoke import (
    G19_PROJECT,
    PROFILE_ID,
    assert_compact_project_budget,
)
from prepare_human_playtest import pin_scene_profile, run_project_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g27_full_terrain_handoff_preflight"
SCRIPT = "res://tests/g27_full_terrain_handoff_preflight.gd"
MARKER = "WT_VALIDATION_G27_FULL_TERRAIN_HANDOFF_PREFLIGHT_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G27_FULL_TERRAIN_HANDOFF_PREFLIGHT_SMOKE_PASS"
MAX_LOAD_TO_PLAY_SECONDS = 30.0
MAX_RUNTIME_SECONDS = 120.0


def prepare_project(project: Path) -> tuple[dict[str, object], Path]:
    lock = compose(project)
    scene = pin_scene_profile(project, PROFILE_ID)
    assert_compact_project_budget(project)
    return lock, scene


def run_runtime(project: Path, version: str, engine: Path) -> dict[str, object]:
    command = [str(engine), "--path", str(project), "--script", SCRIPT]
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
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
    (ARTIFACT_ROOT / f"godot-{version}-g27.stdout.txt").write_text(
        result.stdout, encoding="utf-8"
    )
    (ARTIFACT_ROOT / f"godot-{version}-g27.stderr.txt").write_text(
        result.stderr, encoding="utf-8"
    )
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G27 full terrain handoff preflight failed on {version}")
    if duration_seconds > MAX_RUNTIME_SECONDS:
        raise RuntimeError(
            f"G27 exceeded runtime ceiling on {version}: "
            f"{duration_seconds:.3f}s > {MAX_RUNTIME_SECONDS:.3f}s"
        )
    return {
        "engine": version,
        "executable": str(engine),
        "duration_seconds": duration_seconds,
        "marker": next(line for line in combined.splitlines() if line.startswith(MARKER)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run full-terrain human handoff preflight validation."
    )
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=G19_PROJECT)
    parser.add_argument("--skip-build", action="store_true")
    arguments = parser.parse_args()

    build_world_transvoxel(arguments.skip_build)
    project = arguments.project.resolve()
    lock, scene = prepare_project(project)
    pre_run_budget = assert_compact_project_budget(project)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_project_import(project, version, engine, ARTIFACT_ROOT)
        results.append(run_runtime(project, version, engine))
    post_run_budget = assert_compact_project_budget(project)
    max_engine_seconds = max(float(result["duration_seconds"]) for result in results)
    if max_engine_seconds > MAX_LOAD_TO_PLAY_SECONDS:
        raise RuntimeError(
            "G27 max engine time exceeded load-to-play ceiling: "
            f"{max_engine_seconds:.3f}s > {MAX_LOAD_TO_PLAY_SECONDS:.3f}s"
        )
    report_path = ARTIFACT_ROOT / "g27_full_terrain_handoff_preflight_report.json"
    report_path.write_text(
        json.dumps(
            {
                "project": str(project),
                "scene": str(scene),
                "profile": PROFILE_ID,
                "lock": lock,
                "pre_run_budget": pre_run_budget,
                "post_run_budget": post_run_budget,
                "engines": results,
                "implementation": "full_terrain_handoff_preflight",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"{SUMMARY_MARKER} engines={len(results)} "
        f"max_engine_seconds={max_engine_seconds:.3f} "
        f"project={project.as_posix()} "
        f"scene=res://scenes/validation_playtest.tscn "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
