#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from compose_validation_project import ROOT, compose
from g0_install_run_smoke import discover_engines
from g8_runtime_active_window_smoke import build_world_transvoxel
from g19_compact_2k_on_demand_smoke import (
    PROFILE_ID,
    assert_compact_project_budget,
)
from g28_normal_project_launch_preflight import MAIN_SCENE, pin_scene_property
from prepare_human_playtest import SCENE, pin_scene_profile, run_project_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g29_compact_2k_human_ready_handoff"
PROJECT = ARTIFACT_ROOT / "project"
G27_REPORT = (
    ROOT
    / "artifacts"
    / "g27_full_terrain_handoff_preflight"
    / "g27_full_terrain_handoff_preflight_report.json"
)
G28_REPORT = (
    ROOT
    / "artifacts"
    / "g28_normal_project_launch_preflight"
    / "g28_normal_project_launch_preflight_report.json"
)
MARKER = "WT_VALIDATION_G29_COMPACT_2K_HUMAN_READY_HANDOFF_PASS"


def load_report(path: Path, implementation: str) -> dict[str, object]:
    if not path.is_file():
        raise RuntimeError(f"G29 requires current prerequisite report: {path}")
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("implementation") != implementation:
        raise RuntimeError(f"G29 prerequisite report has wrong implementation: {path}")
    if report.get("profile") != PROFILE_ID:
        raise RuntimeError(f"G29 prerequisite report has wrong profile: {path}")
    return report


def assert_report_lock_matches(lock: dict[str, object], report: dict[str, object]) -> None:
    lock_sources = dict(lock.get("sources", {}))
    report_sources = dict(dict(report.get("lock", {})).get("sources", {}))
    for name in ("world-transvoxel", "world-transvoxel-terrain"):
        expected = dict(lock_sources.get(name, {})).get("commit")
        actual = dict(report_sources.get(name, {})).get("commit")
        if expected != actual:
            raise RuntimeError(
                f"G29 prerequisite report is stale for {name}: {actual} != {expected}"
            )


def assert_handoff_shape(project: Path, scene: Path) -> None:
    project_text = (project / "project.godot").read_text(encoding="utf-8")
    scene_text = scene.read_text(encoding="utf-8")
    if f'run/main_scene="{MAIN_SCENE}"' not in project_text:
        raise RuntimeError("G29 handoff project does not launch validation_playtest")
    if f'playtest_profile_id = &"{PROFILE_ID}"' not in scene_text:
        raise RuntimeError("G29 handoff scene is not pinned to compact profile")
    if "human_input_enabled = true" not in scene_text:
        raise RuntimeError("G29 handoff scene does not have human input enabled")
    if "human_input_enabled = false" in scene_text:
        raise RuntimeError("G29 handoff scene still contains automation input disable")


def write_human_review(project: Path, lock: dict[str, object]) -> Path:
    review_path = project / "HUMAN_REVIEW.md"
    world_commit = dict(dict(lock["sources"])["world-transvoxel"])["commit"]
    terrain_commit = dict(dict(lock["sources"])["world-transvoxel-terrain"])["commit"]
    review_path.write_text(
        "\n".join(
            [
                "# G29 compact 2K human-ready handoff",
                "",
                "Open `project.godot` and run the main scene.",
                "",
                "Controls:",
                "",
                "- WASD: move",
                "- Mouse: look",
                "- Space: jump",
                "- Left mouse: carve terrain",
                "- Right mouse: place/construct terrain",
                "- Esc/click: release or recapture mouse depending on Godot state",
                "",
                "Expected baseline:",
                "",
                "- profile: g19_compact_2k_on_demand",
                "- map: 2048 by 2048 blocks",
                "- human input: enabled",
                "- native editable/collision detail: local active Transvoxel window",
                "- far terrain: full-map deterministic visual layer",
                "",
                "Prerequisite automated proofs:",
                "",
                "- G27 full-terrain scene-level handoff preflight",
                "- G28 normal project launch preflight",
                "",
                "Known boundaries:",
                "",
                "- placeholder terrain art/materials",
                "- not seamless dynamic LOD approval",
                "- no water, biomes, vegetation, buildings, GPU compute, or multiplayer",
                "",
                "Source commits:",
                "",
                f"- world-transvoxel: {world_commit}",
                f"- world-transvoxel-terrain: {terrain_commit}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return review_path


def prepare_project(project: Path) -> tuple[dict[str, object], Path, Path]:
    lock = compose(project)
    scene = pin_scene_profile(project, PROFILE_ID)
    pin_scene_property(scene, "human_input_enabled", "true")
    assert_handoff_shape(project, scene)
    review_path = write_human_review(project, lock)
    return lock, scene, review_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare compact 2K human-ready handoff project."
    )
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--skip-build", action="store_true")
    arguments = parser.parse_args()

    build_world_transvoxel(arguments.skip_build)
    project = arguments.project.resolve()
    lock, scene, review_path = prepare_project(project)
    g27 = load_report(G27_REPORT, "full_terrain_handoff_preflight")
    g28 = load_report(G28_REPORT, "normal_project_launch_preflight")
    assert_report_lock_matches(lock, g27)
    assert_report_lock_matches(lock, g28)
    pre_import_budget = assert_compact_project_budget(project)
    engines = discover_engines(arguments.godot)
    imported: list[dict[str, str]] = []
    for version, engine in engines:
        run_project_import(project, version, engine, ARTIFACT_ROOT)
        imported.append({"engine": version, "executable": str(engine)})
    post_import_budget = assert_compact_project_budget(project)
    report_path = ARTIFACT_ROOT / "g29_compact_2k_human_ready_handoff_report.json"
    report_path.write_text(
        json.dumps(
            {
                "project": str(project),
                "scene": str(scene),
                "scene_res": MAIN_SCENE,
                "profile": PROFILE_ID,
                "human_input_enabled": True,
                "review": str(review_path),
                "lock": lock,
                "g27_report": str(G27_REPORT),
                "g28_report": str(G28_REPORT),
                "pre_import_budget": pre_import_budget,
                "post_import_budget": post_import_budget,
                "engines": imported,
                "implementation": "compact_2k_human_ready_handoff",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"{MARKER} profile={PROFILE_ID} project={project.as_posix()} "
        f"scene={MAIN_SCENE} human_input=true imported_engines={len(imported)} "
        f"review={review_path.relative_to(project).as_posix()} dense_world_files=0 "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
