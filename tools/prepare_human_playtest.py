#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from compose_validation_project import ROOT, compose
from g0_install_run_smoke import discover_engines, has_godot_error
from g3_generation_modes_smoke import copy_worlds_into_project, generate_worlds
from g3_generation_modes_smoke import WORLDS_ROOT


ARTIFACT_ROOT = ROOT / "artifacts" / "human_playtest"
PROJECT = ARTIFACT_ROOT / "project"
SCENE = "scenes/validation_playtest.tscn"
MARKER = "WT_VALIDATION_HUMAN_PLAYTEST_READY"
PROFILES = ("flat_large", "mountain_large")


def profile_worlds_exist() -> bool:
    return all((WORLDS_ROOT / profile / "world.wtworld").is_file() for profile in PROFILES)


def ensure_worlds(reuse_bake: bool) -> list[dict[str, object]]:
    if reuse_bake and profile_worlds_exist():
        return [
            {
                "mode": profile,
                "world": str(WORLDS_ROOT / profile / "world.wtworld"),
                "reused": True,
            }
            for profile in PROFILES
        ]
    return generate_worlds()


def pin_scene_profile(project: Path, profile: str) -> Path:
    scene = project / SCENE
    text = scene.read_text(encoding="utf-8")
    target_line = f'playtest_profile_id = &"{profile}"'
    output: list[str] = []
    in_root = False
    root_seen = False
    inserted = False
    for line in text.splitlines():
        if line.startswith('[node name="ValidationPlaytest"'):
            in_root = True
            root_seen = True
        elif in_root and line.startswith("[node "):
            if not inserted:
                output.append(target_line)
                inserted = True
            in_root = False
        if in_root and line.startswith("playtest_profile_id ="):
            if not inserted:
                output.append(target_line)
                inserted = True
            continue
        output.append(line)
        if in_root and line == 'script = ExtResource("1_playtest")' and not inserted:
            output.append(target_line)
            inserted = True
    if in_root and not inserted:
        output.append(target_line)
        inserted = True
    if not root_seen or not inserted:
        raise RuntimeError(f"Could not pin {SCENE} to {profile}.")
    scene.write_text("\n".join(output) + "\n", encoding="utf-8")
    return scene


def select_engine(explicit: list[Path]) -> tuple[str, Path]:
    engines = discover_engines(explicit)
    return engines[-1]


def run_project_import(project: Path, version: str, engine: Path) -> None:
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [str(engine), "--headless", "--path", str(project), "--import"],
        cwd=project,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=180,
    )
    (ARTIFACT_ROOT / f"godot-{version}-import.stdout.txt").write_text(
        result.stdout, encoding="utf-8"
    )
    (ARTIFACT_ROOT / f"godot-{version}-import.stderr.txt").write_text(
        result.stderr, encoding="utf-8"
    )
    combined = result.stdout + result.stderr
    extension_cache = project / ".godot" / "extension_list.cfg"
    cache_valid = (
        extension_cache.is_file()
        and "res://addons/world_transvoxel/world_transvoxel.gdextension"
        in extension_cache.read_text(encoding="utf-8", errors="replace")
    )
    if result.returncode != 0 or has_godot_error(combined) or not cache_valid:
        raise RuntimeError(f"Human playtest import failed on {version}")


def launch_project(project: Path, engine: Path, fullscreen: bool) -> int:
    command = [str(engine), "--path", str(project)]
    if fullscreen:
        command.append("--fullscreen")
    process = subprocess.Popen(command, cwd=project)
    return int(process.pid)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare the generated project used for final human visual playtesting."
    )
    parser.add_argument("--profile", choices=PROFILES, default="flat_large")
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--reuse-bake", action="store_true")
    parser.add_argument("--import-project", action="store_true")
    parser.add_argument("--launch", action="store_true")
    parser.add_argument("--fullscreen", action="store_true")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    arguments = parser.parse_args()

    bake = ensure_worlds(arguments.reuse_bake)
    project = arguments.project.resolve()
    lock = compose(project)
    copy_worlds_into_project(project)
    scene = pin_scene_profile(project, arguments.profile)
    engine_info: dict[str, str] | None = None
    if arguments.import_project or arguments.launch:
        version, engine = select_engine(arguments.godot)
        run_project_import(project, version, engine)
        engine_info = {"version": version, "executable": str(engine)}
    pid: int | None = None
    if arguments.launch:
        assert engine_info is not None
        pid = launch_project(project, Path(engine_info["executable"]), arguments.fullscreen)
    report = {
        "project": str(project),
        "scene": str(scene),
        "profile": arguments.profile,
        "lock": lock,
        "bake": bake,
        "engine": engine_info,
        "pid": pid,
    }
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    report_path = ARTIFACT_ROOT / "human_playtest_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"{MARKER} profile={arguments.profile} "
        f"project={project.as_posix()} "
        f"scene=res://{SCENE} "
        f"launch={str(arguments.launch).lower()} "
        f"fullscreen={str(arguments.fullscreen).lower()} "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
