#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from compose_validation_project import ROOT, compose
from g19_compact_2k_on_demand_smoke import (
    G19_PROJECT,
    PROFILE_ID,
    PROJECT_WORLD_ROOT,
    assert_compact_project_budget,
)
from g20_compact_terrain_resolution import G19_REPORT, load_json, validate_g19_report
from prepare_human_playtest import (
    launch_project,
    pin_scene_profile,
    run_project_import,
    select_engine,
)


ARTIFACT_ROOT = ROOT / "artifacts" / "g21_compact_2k_human_handoff"
SCENE = "scenes/validation_playtest.tscn"
MARKER = "WT_VALIDATION_G21_COMPACT_2K_HUMAN_HANDOFF_READY"


def scene_is_pinned(project: Path, profile: str) -> bool:
    scene = project / SCENE
    text = scene.read_text(encoding="utf-8")
    return f'playtest_profile_id = &"{profile}"' in text


def prepare_project(project: Path) -> tuple[dict[str, object], Path, dict[str, object]]:
    runtime = validate_g19_report(load_json(G19_REPORT))
    lock = compose(project)
    scene = pin_scene_profile(project, PROFILE_ID)
    if not scene_is_pinned(project, PROFILE_ID):
        raise RuntimeError(f"{SCENE} is not pinned to {PROFILE_ID}")
    budget = assert_compact_project_budget(project)
    return lock, scene, {
        "report": str(G19_REPORT),
        "pages": 16384,
        "engines": runtime["engines"],
        "max_file_bytes": runtime["max_file_bytes"],
        "total_bytes": runtime["total_bytes"],
        "max_engine_milliseconds": runtime["max_engine_milliseconds"],
        "project_budget": budget,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare the G19 compact near-2K project for human visual playtesting."
    )
    parser.add_argument("--project", type=Path, default=G19_PROJECT)
    parser.add_argument("--import-project", action="store_true")
    parser.add_argument("--launch", action="store_true")
    parser.add_argument("--fullscreen", action="store_true")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    arguments = parser.parse_args()

    project = arguments.project.resolve()
    lock, scene, runtime = prepare_project(project)

    engine_info: dict[str, str] | None = None
    if arguments.import_project or arguments.launch:
        version, engine = select_engine(arguments.godot)
        engine_info = {"version": version, "executable": str(engine)}
        run_project_import(project, version, engine, ARTIFACT_ROOT)

    pid: int | None = None
    if arguments.launch:
        assert engine_info is not None
        pid = launch_project(project, Path(engine_info["executable"]), arguments.fullscreen)

    report = {
        "marker": MARKER,
        "project": str(project),
        "scene": str(scene),
        "scene_res": f"res://{SCENE}",
        "profile": PROFILE_ID,
        "object_root": str(project / PROJECT_WORLD_ROOT),
        "runtime": runtime,
        "lock": lock,
        "engine": engine_info,
        "imported": bool(arguments.import_project or arguments.launch),
        "launched": bool(arguments.launch),
        "fullscreen": bool(arguments.fullscreen),
        "pid": pid,
        "human_confirmation": "pending",
    }
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    report_path = ARTIFACT_ROOT / "g21_compact_2k_human_handoff_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"{MARKER} profile={PROFILE_ID} "
        f"imported={str(report['imported']).lower()} "
        f"project={project.as_posix()} "
        f"scene=res://{SCENE} "
        f"fullscreen={str(report['fullscreen']).lower()} "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
