#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess

from compose_validation_project import ROOT, compose
from g0_install_run_smoke import discover_engines, has_godot_error, run_import
from g8_runtime_active_window_smoke import build_world_transvoxel


ARTIFACT_ROOT = ROOT / "artifacts" / "g19_compact_2k_on_demand"
G19_PROJECT = ARTIFACT_ROOT / "project"
PROFILE_ID = "g19_compact_2k_on_demand"
PROJECT_WORLD_ROOT = Path("build") / "g19-compact-on-demand" / PROFILE_ID
SCRIPT = "res://tests/g19_compact_2k_on_demand_smoke.gd"
MARKER = "WT_VALIDATION_G19_COMPACT_2K_ON_DEMAND_PASS"
MAX_GENERATED_FILE_BYTES = 50 * 1024 * 1024
MAX_GENERATED_TOTAL_BYTES = 100 * 1024 * 1024
FORBIDDEN_ARTIFACT_DIRS = (
    ARTIFACT_ROOT / "source",
    ARTIFACT_ROOT / "worlds",
)
FORBIDDEN_PROJECT_FILES = (
    PROJECT_WORLD_ROOT / "world.wtworld",
    PROJECT_WORLD_ROOT / "streaming.wtworld",
    PROJECT_WORLD_ROOT / "procedural.wtseed",
)


def remove_tree(path: Path) -> None:
    if path.exists():
        path.relative_to(ROOT)
        shutil.rmtree(path)


def collect_directory_budget(path: Path) -> dict[str, object]:
    total_bytes = 0
    max_file_bytes = 0
    max_file = ""
    file_count = 0
    if path.is_dir():
        for file_path in path.rglob("*"):
            if not file_path.is_file():
                continue
            file_count += 1
            size = file_path.stat().st_size
            total_bytes += size
            if size > max_file_bytes:
                max_file_bytes = size
                max_file = file_path.relative_to(path).as_posix()
    return {
        "path": str(path),
        "exists": path.exists(),
        "file_count": file_count,
        "total_bytes": total_bytes,
        "max_file_bytes": max_file_bytes,
        "max_file": max_file,
    }


def assert_compact_project_budget(project: Path) -> dict[str, object]:
    for forbidden in FORBIDDEN_ARTIFACT_DIRS:
        if forbidden.exists():
            raise RuntimeError(f"G19 must not create dense artifact directory: {forbidden}")
    for relative in FORBIDDEN_PROJECT_FILES:
        path = project / relative
        if path.exists():
            raise RuntimeError(f"G19 must not create dense project file: {path}")
    world_root = project / PROJECT_WORLD_ROOT
    budget = collect_directory_budget(world_root)
    if int(budget["max_file_bytes"]) > MAX_GENERATED_FILE_BYTES:
        raise RuntimeError(f"G19 generated file exceeds budget: {budget}")
    if int(budget["total_bytes"]) > MAX_GENERATED_TOTAL_BYTES:
        raise RuntimeError(f"G19 generated directory exceeds budget: {budget}")
    return budget


def run_smoke(project: Path, version: str, engine: Path, headless: bool) -> dict[str, object]:
    command = [str(engine)]
    if headless:
        command.append("--headless")
    command.extend(["--path", str(project), "--script", SCRIPT])
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        command,
        cwd=project,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=900,
    )
    (ARTIFACT_ROOT / f"godot-{version}-g19.stdout.txt").write_text(
        result.stdout,
        encoding="utf-8",
    )
    (ARTIFACT_ROOT / f"godot-{version}-g19.stderr.txt").write_text(
        result.stderr,
        encoding="utf-8",
    )
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G19 compact 2K on-demand smoke failed on {version}")
    return {
        "engine": version,
        "executable": str(engine),
        "marker": next(line for line in combined.splitlines() if line.startswith(MARKER)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the G19 compact 2K on-demand procedural streaming validation smoke."
    )
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=G19_PROJECT)
    parser.add_argument("--windowed", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    arguments = parser.parse_args()

    build_world_transvoxel(arguments.skip_build)
    project = arguments.project.resolve()
    remove_tree(ARTIFACT_ROOT / "source")
    remove_tree(ARTIFACT_ROOT / "worlds")
    lock = compose(project)
    remove_tree(project / PROJECT_WORLD_ROOT)
    pre_run_budget = assert_compact_project_budget(project)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_import(project, version, engine)
        results.append(run_smoke(project, version, engine, not arguments.windowed))
    post_run_budget = assert_compact_project_budget(project)
    report_path = ARTIFACT_ROOT / "g19_compact_2k_on_demand_report.json"
    report_path.write_text(
        json.dumps(
            {
                "project": str(project),
                "lock": lock,
                "engines": results,
                "pre_run_budget": pre_run_budget,
                "post_run_budget": post_run_budget,
                "profile": PROFILE_ID,
                "implementation": "compact_2k_on_demand_procedural_streaming",
                "budget": {
                    "max_generated_file_bytes": MAX_GENERATED_FILE_BYTES,
                    "max_generated_total_bytes": MAX_GENERATED_TOTAL_BYTES,
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
        "WT_VALIDATION_G19_COMPACT_2K_ON_DEMAND_SMOKE_PASS "
        f"engines={len(results)} "
        f"max_file_bytes={post_run_budget['max_file_bytes']} "
        f"total_bytes={post_run_budget['total_bytes']} "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
