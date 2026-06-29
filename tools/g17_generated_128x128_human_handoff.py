#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from compose_validation_project import ROOT, compose
from g16_generated_128x128_playable_streaming_smoke import (
    G16_PROJECT,
    MARKER as G16_RUNTIME_MARKER,
    PROFILE_ID,
    PROJECT_WORLD_ROOT,
    WORLD_MANIFEST,
    copy_fixture_into_project,
)
from prepare_human_playtest import launch_project, pin_scene_profile, run_project_import, select_engine


ARTIFACT_ROOT = ROOT / "artifacts" / "g17_generated_128x128_human_handoff"
G16_REPORT = (
    ROOT
    / "artifacts"
    / "g16_generated_128x128_playable_streaming"
    / "g16_generated_128x128_playable_streaming_report.json"
)
SCENE = "scenes/validation_playtest.tscn"
MARKER = "WT_VALIDATION_G17_GENERATED_128X128_HUMAN_HANDOFF_READY"


def validate_g16_runtime_report() -> dict[str, object]:
    if not G16_REPORT.is_file():
        raise RuntimeError(
            "G16 runtime report is missing; run "
            "`python tools/g16_generated_128x128_playable_streaming_smoke.py --skip-build --reuse-fixture` first"
        )
    report = json.loads(G16_REPORT.read_text(encoding="utf-8"))
    fixture = report.get("fixture", {})
    metadata = fixture.get("metadata", {}) if isinstance(fixture, dict) else {}
    engines = report.get("engines", [])
    if report.get("implementation") != "generated_128x128_playable_streaming":
        raise RuntimeError("G16 runtime report implementation mismatch")
    if metadata.get("pages") != 16384:
        raise RuntimeError(f"G16 runtime report page count mismatch: {metadata}")
    if metadata.get("source_revision") != 1612800:
        raise RuntimeError(f"G16 runtime report source revision mismatch: {metadata}")
    if not isinstance(engines, list) or len(engines) != 2:
        raise RuntimeError("G16 runtime report must contain two engine results")
    for engine in engines:
        marker = engine.get("marker") if isinstance(engine, dict) else None
        if not isinstance(marker, str) or not marker.startswith(G16_RUNTIME_MARKER):
            raise RuntimeError(f"G16 runtime marker mismatch: {marker}")
    return {
        "report": str(G16_REPORT),
        "pages": metadata.get("pages"),
        "source_revision": metadata.get("source_revision"),
        "engines": len(engines),
    }


def scene_is_pinned(project: Path, profile: str) -> bool:
    scene = project / SCENE
    text = scene.read_text(encoding="utf-8")
    return f'playtest_profile_id = &"{profile}"' in text


def project_world_manifest(project: Path) -> Path:
    return project / PROJECT_WORLD_ROOT / "world.wtworld"


def prepare_project(project: Path) -> tuple[dict[str, object], Path]:
    if not WORLD_MANIFEST.is_file():
        raise RuntimeError(
            "G16 baked world is missing; run "
            "`python tools/g16_generated_128x128_playable_streaming_smoke.py` first"
        )
    lock = compose(project)
    copy_fixture_into_project(project)
    scene = pin_scene_profile(project, PROFILE_ID)
    if not project_world_manifest(project).is_file():
        raise RuntimeError(f"G16 world manifest was not copied into {project}")
    if not scene_is_pinned(project, PROFILE_ID):
        raise RuntimeError(f"{SCENE} is not pinned to {PROFILE_ID}")
    return lock, scene


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare the G16 128x128 generated terrain project for human visual playtesting."
    )
    parser.add_argument("--project", type=Path, default=G16_PROJECT)
    parser.add_argument("--import-project", action="store_true")
    parser.add_argument("--launch", action="store_true")
    parser.add_argument("--fullscreen", action="store_true")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    arguments = parser.parse_args()

    runtime = validate_g16_runtime_report()
    project = arguments.project.resolve()
    lock, scene = prepare_project(project)

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
        "project": str(project),
        "scene": str(scene),
        "profile": PROFILE_ID,
        "world_manifest": str(project_world_manifest(project)),
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
    report_path = ARTIFACT_ROOT / "g17_generated_128x128_human_handoff_report.json"
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
