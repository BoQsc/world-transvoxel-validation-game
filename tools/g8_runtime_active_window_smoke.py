#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

from compose_validation_project import ROOT, WORLD_TRANSVOXEL_REPO, compose
from g0_install_run_smoke import discover_engines, has_godot_error, run_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g8_runtime_active_window"
G8_PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g8_runtime_active_window_smoke.gd"
MARKER = "WT_VALIDATION_G8_RUNTIME_ACTIVE_WINDOW_PASS"
FIXTURE_ROOT = WORLD_TRANSVOXEL_REPO / "build" / "production-lifecycle-fixture"
FIXTURE_MANIFEST = FIXTURE_ROOT / "g8_2000x2000_sparse.wtworld"


def build_world_transvoxel(skip_build: bool) -> None:
    if skip_build:
        return
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            sys.executable,
            str(WORLD_TRANSVOXEL_REPO / "scripts" / "build.py"),
            "--configuration",
            "all",
        ],
        cwd=WORLD_TRANSVOXEL_REPO,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=900,
    )
    (ARTIFACT_ROOT / "world-transvoxel-build.stdout.txt").write_text(
        result.stdout, encoding="utf-8"
    )
    (ARTIFACT_ROOT / "world-transvoxel-build.stderr.txt").write_text(
        result.stderr, encoding="utf-8"
    )
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0:
        raise RuntimeError("world-transvoxel build failed before G8 runtime smoke")


def native_lifecycle_fixture_generator() -> Path:
    scripts_path = str(WORLD_TRANSVOXEL_REPO / "scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    from wt_script_common import native_test_path

    return native_test_path("template_release", "test_wt_production_lifecycle")


def prepare_sparse_fixture(reuse_fixture: bool) -> dict[str, object]:
    if reuse_fixture and FIXTURE_MANIFEST.is_file():
        return {
            "reused": True,
            "fixture_manifest": str(FIXTURE_MANIFEST),
        }
    executable = native_lifecycle_fixture_generator()
    if not executable.is_file():
        raise RuntimeError(
            "Missing native lifecycle fixture generator after build: "
            f"{executable}"
        )
    if FIXTURE_ROOT.exists():
        shutil.rmtree(FIXTURE_ROOT)
    result = subprocess.run(
        [
            str(executable),
            "--write-godot-fixture",
            str(FIXTURE_ROOT),
        ],
        cwd=WORLD_TRANSVOXEL_REPO,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=180,
    )
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    (ARTIFACT_ROOT / "fixture-generation.stdout.txt").write_text(
        result.stdout, encoding="utf-8"
    )
    (ARTIFACT_ROOT / "fixture-generation.stderr.txt").write_text(
        result.stderr, encoding="utf-8"
    )
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if (
        result.returncode != 0
        or "PRODUCTION_G8_2000X2000_FIXTURE_PASS" not in combined
        or not FIXTURE_MANIFEST.is_file()
    ):
        raise RuntimeError("G8 sparse 2000x2000 fixture generation failed")
    return {
        "reused": False,
        "generator": str(executable),
        "fixture_manifest": str(FIXTURE_MANIFEST),
    }


def run_smoke(project: Path, version: str, engine: Path, headless: bool) -> dict[str, object]:
    command = [str(engine)]
    if headless:
        command.append("--headless")
    command.extend(["--path", str(project), "--script", SCRIPT])
    result = subprocess.run(
        command,
        cwd=project,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=240,
    )
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    (ARTIFACT_ROOT / f"godot-{version}-g8-runtime.stdout.txt").write_text(
        result.stdout, encoding="utf-8"
    )
    (ARTIFACT_ROOT / f"godot-{version}-g8-runtime.stderr.txt").write_text(
        result.stderr, encoding="utf-8"
    )
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G8 runtime active-window smoke failed on {version}")
    return {
        "engine": version,
        "executable": str(engine),
        "marker": next(line for line in combined.splitlines() if line.startswith(MARKER)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the G8 bounded 2000x2000 runtime active-window smoke."
    )
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=G8_PROJECT)
    parser.add_argument("--windowed", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--reuse-fixture", action="store_true")
    arguments = parser.parse_args()

    build_world_transvoxel(arguments.skip_build)
    fixture = prepare_sparse_fixture(arguments.reuse_fixture)
    project = arguments.project.resolve()
    lock = compose(project)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_import(project, version, engine)
        results.append(run_smoke(project, version, engine, not arguments.windowed))
    report_path = ARTIFACT_ROOT / "g8_runtime_active_window_report.json"
    report_path.write_text(
        json.dumps(
            {
                "project": str(project),
                "lock": lock,
                "fixture": fixture,
                "engines": results,
                "implementation": "bounded_2000x2000_runtime_active_window",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        "WT_VALIDATION_G8_RUNTIME_SMOKE_PASS "
        f"engines={len(results)} report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
