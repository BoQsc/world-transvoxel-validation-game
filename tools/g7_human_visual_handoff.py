#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from compose_validation_project import ROOT, compose
from g3_generation_modes_smoke import copy_worlds_into_project, generate_worlds
from prepare_human_playtest import PROFILES, pin_scene_profile
from prepare_human_playtest import profile_worlds_exist, run_project_import
from prepare_human_playtest import select_engine


ARTIFACT_ROOT = ROOT / "artifacts" / "g7_human_visual_handoff"
MARKER = "WT_VALIDATION_G7_HANDOFF_READY"


def ensure_worlds(reuse_bake: bool) -> list[dict[str, object]]:
    if reuse_bake and profile_worlds_exist():
        return [{"mode": profile, "reused": True} for profile in PROFILES]
    return generate_worlds()


def prepare_profile_project(profile: str) -> dict[str, object]:
    project = (ARTIFACT_ROOT / profile / "project").resolve()
    lock = compose(project)
    copy_worlds_into_project(project)
    scene = pin_scene_profile(project, profile)
    return {
        "profile": profile,
        "project": str(project),
        "scene": str(scene),
        "lock": lock,
    }


def scene_is_pinned(project: Path, profile: str) -> bool:
    scene = project / "scenes" / "validation_playtest.tscn"
    text = scene.read_text(encoding="utf-8")
    return f'playtest_profile_id = &"{profile}"' in text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare reproducible G7 projects for final human visual review."
    )
    parser.add_argument("--reuse-bake", action="store_true")
    parser.add_argument("--import-projects", action="store_true")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    arguments = parser.parse_args()

    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    bake = ensure_worlds(arguments.reuse_bake)
    engine_info: dict[str, str] | None = None
    if arguments.import_projects:
        version, engine = select_engine(arguments.godot)
        engine_info = {"version": version, "executable": str(engine)}
    projects: list[dict[str, object]] = []
    for profile in PROFILES:
        prepared = prepare_profile_project(profile)
        project_path = Path(str(prepared["project"]))
        if not scene_is_pinned(project_path, profile):
            raise RuntimeError(f"{profile} generated scene is not pinned to its profile.")
        if arguments.import_projects:
            assert engine_info is not None
            run_project_import(
                project_path,
                engine_info["version"],
                Path(engine_info["executable"]),
                ARTIFACT_ROOT / profile,
            )
            prepared["imported"] = True
        else:
            prepared["imported"] = False
        projects.append(prepared)
    report = {
        "profiles": list(PROFILES),
        "projects": projects,
        "bake": bake,
        "engine": engine_info,
        "human_confirmation": "pending",
    }
    report_path = ARTIFACT_ROOT / "g7_human_visual_handoff_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"{MARKER} profiles={len(PROFILES)} "
        f"imported={str(arguments.import_projects).lower()} "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
