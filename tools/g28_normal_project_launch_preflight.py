#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import queue
import subprocess
import threading
import time

from g0_install_run_smoke import discover_engines, has_godot_error
from g8_runtime_active_window_smoke import build_world_transvoxel
from g19_compact_2k_on_demand_smoke import (
    G19_PROJECT,
    PROFILE_ID,
    assert_compact_project_budget,
)
from prepare_human_playtest import SCENE, pin_scene_profile, run_project_import
from compose_validation_project import ROOT, compose


ARTIFACT_ROOT = ROOT / "artifacts" / "g28_normal_project_launch_preflight"
MAIN_SCENE = "res://scenes/validation_playtest.tscn"
READY_MARKER = "WT_VALIDATION_PLAYTEST_READY"
MARKER = "WT_VALIDATION_G28_NORMAL_PROJECT_LAUNCH_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G28_NORMAL_PROJECT_LAUNCH_SMOKE_PASS"
MAX_READY_SECONDS = 30.0
MAX_RUNTIME_SECONDS = 45.0


def prepare_project(project: Path) -> tuple[dict[str, object], Path]:
    lock = compose(project)
    scene = pin_scene_profile(project, PROFILE_ID)
    pin_scene_property(scene, "human_input_enabled", "false")
    assert_project_launch_shape(project, scene)
    assert_compact_project_budget(project)
    return lock, scene


def restore_human_handoff_scene(scene: Path) -> None:
    pin_scene_property(scene, "human_input_enabled", "true")
    if "human_input_enabled = true" not in scene.read_text(encoding="utf-8"):
        raise RuntimeError("G28 failed to restore human input in handoff scene")


def pin_scene_property(scene: Path, property_name: str, value: str) -> None:
    text = scene.read_text(encoding="utf-8")
    target_line = f"{property_name} = {value}"
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
        if in_root and line.startswith(f"{property_name} ="):
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
        raise RuntimeError(f"Could not pin {scene.name} property {property_name}.")
    scene.write_text("\n".join(output) + "\n", encoding="utf-8")


def assert_project_launch_shape(project: Path, scene: Path) -> None:
    project_text = (project / "project.godot").read_text(encoding="utf-8")
    scene_text = scene.read_text(encoding="utf-8")
    if f'run/main_scene="{MAIN_SCENE}"' not in project_text:
        raise RuntimeError("generated project does not launch validation_playtest")
    if f'playtest_profile_id = &"{PROFILE_ID}"' not in scene_text:
        raise RuntimeError("normal launch scene is not pinned to compact profile")
    if "human_input_enabled = false" not in scene_text:
        raise RuntimeError("normal launch automation did not disable human input")


def read_pipe(pipe, name: str, output: queue.Queue[tuple[str, str]]) -> None:
    try:
        for line in iter(pipe.readline, ""):
            output.put((name, line))
    finally:
        pipe.close()


def drain(output: queue.Queue[tuple[str, str]], lines: list[tuple[str, str]]) -> None:
    while True:
        try:
            lines.append(output.get_nowait())
        except queue.Empty:
            return


def stop_process(process: subprocess.Popen[str]) -> int:
    if process.poll() is None:
        process.terminate()
        try:
            return process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            return process.wait(timeout=10)
    return int(process.returncode)


def run_normal_launch(project: Path, version: str, engine: Path) -> dict[str, object]:
    command = [str(engine), "--path", str(project), "--quit-after", "3600"]
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    started_at = time.perf_counter()
    process = subprocess.Popen(
        command,
        cwd=project,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        errors="replace",
    )
    assert process.stdout is not None and process.stderr is not None
    output: queue.Queue[tuple[str, str]] = queue.Queue()
    threads = [
        threading.Thread(target=read_pipe, args=(process.stdout, "stdout", output)),
        threading.Thread(target=read_pipe, args=(process.stderr, "stderr", output)),
    ]
    for thread in threads:
        thread.daemon = True
        thread.start()
    lines: list[tuple[str, str]] = []
    ready_seconds: float | None = None
    deadline = started_at + MAX_RUNTIME_SECONDS
    while time.perf_counter() < deadline:
        drain(output, lines)
        combined = "".join(line for _name, line in lines)
        if READY_MARKER in combined:
            ready_seconds = time.perf_counter() - started_at
            break
        if process.poll() is not None:
            break
        time.sleep(0.05)
    returncode = stop_process(process)
    for thread in threads:
        thread.join(timeout=2)
    drain(output, lines)
    combined = "".join(line for _name, line in lines)
    write_launch_logs(version, lines)
    print(combined, end="" if combined.endswith("\n") else "\n")
    if ready_seconds is None:
        raise RuntimeError(f"G28 normal launch did not reach ready on {version}")
    if ready_seconds > MAX_READY_SECONDS:
        raise RuntimeError(
            f"G28 ready time exceeded ceiling on {version}: "
            f"{ready_seconds:.3f}s > {MAX_READY_SECONDS:.3f}s"
        )
    if has_godot_error(combined):
        raise RuntimeError(f"G28 normal launch logged Godot errors on {version}")
    return {
        "engine": version,
        "executable": str(engine),
        "ready_seconds": ready_seconds,
        "returncode_after_terminate": returncode,
        "marker": next(line for line in combined.splitlines() if line.startswith(READY_MARKER)),
    }


def write_launch_logs(version: str, lines: list[tuple[str, str]]) -> None:
    stdout = "".join(line for name, line in lines if name == "stdout")
    stderr = "".join(line for name, line in lines if name == "stderr")
    (ARTIFACT_ROOT / f"godot-{version}-normal-launch.stdout.txt").write_text(
        stdout, encoding="utf-8"
    )
    (ARTIFACT_ROOT / f"godot-{version}-normal-launch.stderr.txt").write_text(
        stderr, encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run normal generated-project launch preflight."
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
    try:
        for version, engine in engines:
            run_project_import(project, version, engine, ARTIFACT_ROOT)
            results.append(run_normal_launch(project, version, engine))
    finally:
        restore_human_handoff_scene(scene)
    post_run_budget = assert_compact_project_budget(project)
    max_ready_seconds = max(float(result["ready_seconds"]) for result in results)
    report_path = ARTIFACT_ROOT / "g28_normal_project_launch_preflight_report.json"
    report_path.write_text(
        json.dumps(
            {
                "project": str(project),
                "scene": str(scene),
                "scene_res": MAIN_SCENE,
                "profile": PROFILE_ID,
                "automation_human_input_enabled": False,
                "post_preflight_human_input_enabled": True,
                "lock": lock,
                "pre_run_budget": pre_run_budget,
                "post_run_budget": post_run_budget,
                "engines": results,
                "implementation": "normal_project_launch_preflight",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"{MARKER} profile={PROFILE_ID} main_scene={MAIN_SCENE} "
        f"human_input=false engines={len(results)} "
        f"max_ready_seconds={max_ready_seconds:.3f} "
        "handoff_human_input_restored=true dense_world_files=0"
    )
    print(
        f"{SUMMARY_MARKER} engines={len(results)} "
        f"max_ready_seconds={max_ready_seconds:.3f} "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
