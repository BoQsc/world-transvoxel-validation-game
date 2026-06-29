#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from compose_validation_project import ROOT, compose
from g0_install_run_smoke import discover_engines, has_godot_error, run_import
from g8_runtime_active_window_smoke import build_world_transvoxel, prepare_sparse_fixture


ARTIFACT_ROOT = ROOT / "artifacts" / "g9_sparse_2k_playable_profile"
G9_PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g9_sparse_2k_playable_profile_smoke.gd"
MARKER = "WT_VALIDATION_G9_SPARSE_2K_PLAYABLE_PASS"


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
        timeout=300,
    )
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    (ARTIFACT_ROOT / f"godot-{version}-g9.stdout.txt").write_text(
        result.stdout, encoding="utf-8"
    )
    (ARTIFACT_ROOT / f"godot-{version}-g9.stderr.txt").write_text(
        result.stderr, encoding="utf-8"
    )
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G9 sparse 2K playable profile smoke failed on {version}")
    return {
        "engine": version,
        "executable": str(engine),
        "marker": next(line for line in combined.splitlines() if line.startswith(MARKER)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the G9 sparse 2K playable-profile validation smoke."
    )
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=G9_PROJECT)
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
    report_path = ARTIFACT_ROOT / "g9_sparse_2k_playable_profile_report.json"
    report_path.write_text(
        json.dumps(
            {
                "project": str(project),
                "lock": lock,
                "fixture": fixture,
                "engines": results,
                "implementation": "sparse_2k_playable_profile",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        "WT_VALIDATION_G9_SPARSE_2K_PLAYABLE_SMOKE_PASS "
        f"engines={len(results)} report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
