#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from compose_validation_project import DEFAULT_OUTPUT, ROOT, compose
from g0_install_run_smoke import discover_engines, has_godot_error, run_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g1_visible_playtest"
G1_PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g1_visible_playtest_smoke.gd"
MARKER = "WT_VALIDATION_G1_GODOT_PASS"


def run_smoke(project: Path, version: str, engine: Path) -> dict[str, object]:
    result = subprocess.run(
        [str(engine), "--headless", "--path", str(project), "--script", SCRIPT],
        cwd=project,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=180,
    )
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    (ARTIFACT_ROOT / f"godot-{version}-smoke.stdout.txt").write_text(
        result.stdout, encoding="utf-8"
    )
    (ARTIFACT_ROOT / f"godot-{version}-smoke.stderr.txt").write_text(
        result.stderr, encoding="utf-8"
    )
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G1 visible playtest smoke failed on {version}")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    return {
        "engine": version,
        "executable": str(engine),
        "marker": marker_line,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the G1 human-visible playtest guard in a composed Godot project."
    )
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=G1_PROJECT)
    arguments = parser.parse_args()

    project = arguments.project.resolve()
    lock = compose(project)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_import(project, version, engine)
        results.append(run_smoke(project, version, engine))

    report_path = ARTIFACT_ROOT / "g1_visible_playtest_report.json"
    report_path.write_text(
        json.dumps(
            {
                "project": str(project),
                "lock": lock,
                "engines": results,
                "implementation": "human_visible_playtest_guard",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        "WT_VALIDATION_G1_SMOKE_PASS "
        f"engines={len(results)} report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
