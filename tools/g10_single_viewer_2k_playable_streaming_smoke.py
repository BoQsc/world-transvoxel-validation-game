#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from compose_validation_project import ROOT, compose
from g0_install_run_smoke import discover_engines, has_godot_error, run_import
from g8_runtime_active_window_smoke import build_world_transvoxel, prepare_sparse_fixture


ARTIFACT_ROOT = ROOT / "artifacts" / "g10_single_viewer_2k_playable_streaming"
G10_PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g10_single_viewer_2k_playable_streaming_smoke.gd"
MARKER = "WT_VALIDATION_G10_SINGLE_VIEWER_2K_PLAYABLE_STREAMING_PASS"


def run_smoke(project: Path, version: str, engine: Path, headless: bool) -> dict[str, object]:
    command = [str(engine)]
    if headless:
        command.append("--headless")
    command.extend(["--path", str(project), "--script", SCRIPT])
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(
            command,
            cwd=project,
            check=False,
            text=True,
            capture_output=True,
            errors="replace",
            timeout=360,
        )
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout or ""
        stderr = error.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        (ARTIFACT_ROOT / f"godot-{version}-g10.timeout.stdout.txt").write_text(
            stdout, encoding="utf-8"
        )
        (ARTIFACT_ROOT / f"godot-{version}-g10.timeout.stderr.txt").write_text(
            stderr, encoding="utf-8"
        )
        combined = stdout + stderr
        print(combined, end="" if combined.endswith("\n") else "\n")
        raise RuntimeError(f"G10 single-viewer 2K playable streaming smoke timed out on {version}") from error
    (ARTIFACT_ROOT / f"godot-{version}-g10.stdout.txt").write_text(
        result.stdout, encoding="utf-8"
    )
    (ARTIFACT_ROOT / f"godot-{version}-g10.stderr.txt").write_text(
        result.stderr, encoding="utf-8"
    )
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G10 single-viewer 2K playable streaming smoke failed on {version}")
    return {
        "engine": version,
        "executable": str(engine),
        "marker": next(line for line in combined.splitlines() if line.startswith(MARKER)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the G10 single-viewer 2K playable streaming validation smoke."
    )
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=G10_PROJECT)
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
    report_path = ARTIFACT_ROOT / "g10_single_viewer_2k_playable_streaming_report.json"
    report_path.write_text(
        json.dumps(
            {
                "project": str(project),
                "lock": lock,
                "fixture": fixture,
                "engines": results,
                "implementation": "single_viewer_2k_playable_streaming",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        "WT_VALIDATION_G10_SINGLE_VIEWER_2K_PLAYABLE_STREAMING_SMOKE_PASS "
        f"engines={len(results)} report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
