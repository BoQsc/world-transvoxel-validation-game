#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from compose_validation_project import ROOT, compose
from g0_install_run_smoke import discover_engines, has_godot_error, run_import
from g3_generation_modes_smoke import copy_worlds_into_project, generate_worlds


ARTIFACT_ROOT = ROOT / "artifacts" / "g6_profile_selectable_playable_world"
G6_PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g6_profile_selectable_playable_world_smoke.gd"
MARKER = "WT_VALIDATION_G6_GODOT_PASS"


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
    (ARTIFACT_ROOT / f"godot-{version}-g6.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g6.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G6 profile-selectable playable-world smoke failed on {version}")
    captures: dict[str, str] = {}
    for profile_id in ("flat_8x8", "mountain_8x8"):
        for view_id in ("first_person", "overview"):
            capture = project / "artifacts" / "g6_profile_selectable_playable_world" / f"{profile_id}_{view_id}.png"
            if not capture.is_file():
                raise RuntimeError(f"G6 capture missing: {capture}")
            target = ARTIFACT_ROOT / f"godot-{version}-{profile_id}-{view_id}.png"
            target.write_bytes(capture.read_bytes())
            captures[f"{profile_id}_{view_id}"] = str(target)
    return {
        "engine": version,
        "executable": str(engine),
        "marker": next(line for line in combined.splitlines() if line.startswith(MARKER)),
        "captures": captures,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the G6 profile-selectable playable-world smoke.")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=G6_PROJECT)
    parser.add_argument("--windowed", action="store_true")
    arguments = parser.parse_args()

    bake_results = generate_worlds()
    project = arguments.project.resolve()
    lock = compose(project)
    copy_worlds_into_project(project)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_import(project, version, engine)
        results.append(run_smoke(project, version, engine, not arguments.windowed))
    report_path = ARTIFACT_ROOT / "g6_profile_selectable_playable_world_report.json"
    report_path.write_text(
        json.dumps({"project": str(project), "lock": lock, "bake": bake_results, "engines": results}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(
        "WT_VALIDATION_G6_SMOKE_PASS "
        f"profiles=2 engines={len(results)} report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
