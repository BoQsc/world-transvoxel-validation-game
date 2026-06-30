#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import queue
import shutil
import subprocess
import threading
import time

from g0_install_run_smoke import discover_engines, has_godot_error
from g19_compact_2k_on_demand_smoke import PROFILE_ID, assert_compact_project_budget
from g28_normal_project_launch_preflight import MAIN_SCENE, READY_MARKER, pin_scene_property
from prepare_human_playtest import run_project_import
from compose_validation_project import ROOT


ARTIFACT_ROOT = ROOT / "artifacts" / "g31_review_bundle_launch_preflight"
SOURCE_BUNDLE = ROOT / "artifacts" / "g30_compact_2k_review_bundle"
LAUNCH_BUNDLE = ARTIFACT_ROOT / "bundle_launch_copy"
SOURCE_MANIFEST = SOURCE_BUNDLE / "HANDOFF_MANIFEST.json"
MARKER = "WT_VALIDATION_G31_REVIEW_BUNDLE_LAUNCH_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G31_REVIEW_BUNDLE_LAUNCH_SMOKE_PASS"
MAX_READY_SECONDS = 30.0
MAX_RUNTIME_SECONDS = 45.0


def reset_directory(path: Path) -> None:
    if path.exists():
        path.relative_to(ROOT)
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_bundle(source: Path, target: Path) -> None:
    if not source.is_dir():
        raise RuntimeError(f"G31 source bundle missing: {source}")
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.tmp"))


def load_manifest(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise RuntimeError(f"G31 source manifest missing: {path}")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("implementation") != "compact_2k_review_bundle":
        raise RuntimeError(f"G31 wrong manifest implementation: {path}")
    if manifest.get("profile") != PROFILE_ID:
        raise RuntimeError(f"G31 wrong manifest profile: {path}")
    return manifest


def scene_path(bundle: Path) -> Path:
    return bundle / "project" / "scenes" / "validation_playtest.tscn"


def project_path(bundle: Path) -> Path:
    return bundle / "project"


def assert_original_bundle_human_ready(bundle: Path) -> None:
    project_text = (bundle / "project" / "project.godot").read_text(encoding="utf-8")
    scene_text = scene_path(bundle).read_text(encoding="utf-8")
    if f'run/main_scene="{MAIN_SCENE}"' not in project_text:
        raise RuntimeError("G31 original bundle main scene is wrong")
    if f'playtest_profile_id = &"{PROFILE_ID}"' not in scene_text:
        raise RuntimeError("G31 original bundle profile pin is wrong")
    if "human_input_enabled = true" not in scene_text:
        raise RuntimeError("G31 original bundle is not human-input ready")


def prepare_launch_copy(source: Path, target: Path) -> Path:
    copy_bundle(source, target)
    cache = target / "project" / ".godot"
    if cache.exists():
        shutil.rmtree(cache)
    scene = scene_path(target)
    pin_scene_property(scene, "human_input_enabled", "false")
    scene_text = scene.read_text(encoding="utf-8")
    if "human_input_enabled = false" not in scene_text:
        raise RuntimeError("G31 launch copy did not disable human input")
    return project_path(target)


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


def write_logs(version: str, lines: list[tuple[str, str]]) -> None:
    stdout = "".join(line for name, line in lines if name == "stdout")
    stderr = "".join(line for name, line in lines if name == "stderr")
    (ARTIFACT_ROOT / f"godot-{version}-bundle-launch.stdout.txt").write_text(
        stdout, encoding="utf-8"
    )
    (ARTIFACT_ROOT / f"godot-{version}-bundle-launch.stderr.txt").write_text(
        stderr, encoding="utf-8"
    )


def run_launch(project: Path, version: str, engine: Path) -> dict[str, object]:
    command = [str(engine), "--path", str(project), "--quit-after", "3600"]
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
    write_logs(version, lines)
    print(combined, end="" if combined.endswith("\n") else "\n")
    if ready_seconds is None:
        raise RuntimeError(f"G31 bundle launch did not reach ready on {version}")
    if ready_seconds > MAX_READY_SECONDS:
        raise RuntimeError(f"G31 ready time exceeded ceiling on {version}: {ready_seconds:.3f}s")
    if has_godot_error(combined):
        raise RuntimeError(f"G31 bundle launch logged Godot errors on {version}")
    return {
        "engine": version,
        "executable": str(engine),
        "ready_seconds": ready_seconds,
        "returncode_after_terminate": returncode,
        "marker": next(line for line in combined.splitlines() if line.startswith(READY_MARKER)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch-test copied G30 review bundle.")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--source-bundle", type=Path, default=SOURCE_BUNDLE)
    parser.add_argument("--output", type=Path, default=ARTIFACT_ROOT)
    arguments = parser.parse_args()

    source_bundle = arguments.source_bundle.resolve()
    output_root = arguments.output.resolve()
    reset_directory(output_root)
    manifest = load_manifest(source_bundle / "HANDOFF_MANIFEST.json")
    assert_original_bundle_human_ready(source_bundle)
    launch_project = prepare_launch_copy(source_bundle, output_root / "bundle_launch_copy")
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_project_import(launch_project, version, engine, ARTIFACT_ROOT)
        results.append(run_launch(launch_project, version, engine))
    assert_original_bundle_human_ready(source_bundle)
    assert_compact_project_budget(launch_project)
    max_ready_seconds = max(float(result["ready_seconds"]) for result in results)
    report_path = output_root / "g31_review_bundle_launch_preflight_report.json"
    report_path.write_text(
        json.dumps(
            {
                "source_bundle": str(source_bundle),
                "launch_project": str(launch_project),
                "profile": PROFILE_ID,
                "source_manifest": str(source_bundle / "HANDOFF_MANIFEST.json"),
                "manifest_implementation": manifest.get("implementation"),
                "automation_human_input_enabled": False,
                "source_bundle_human_input_enabled": True,
                "engines": results,
                "implementation": "review_bundle_launch_preflight",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"{MARKER} profile={PROFILE_ID} engines={len(results)} "
        f"max_ready_seconds={max_ready_seconds:.3f} "
        "launch_copy_human_input=false source_bundle_human_input=true "
        "dense_world_files=0"
    )
    print(
        f"{SUMMARY_MARKER} engines={len(results)} "
        f"max_ready_seconds={max_ready_seconds:.3f} "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
