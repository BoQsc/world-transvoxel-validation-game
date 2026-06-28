#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from compose_validation_project import ROOT, compose
from g0_install_run_smoke import discover_engines, has_godot_error, run_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g1_visual_capture"
CAPTURE_PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g1_visual_capture.gd"
MARKER = "WT_VALIDATION_G1_VISUAL_CAPTURE_PASS"


def run_capture(project: Path, version: str, engine: Path, headless: bool) -> dict[str, object]:
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
        timeout=180,
    )
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    (ARTIFACT_ROOT / f"godot-{version}-capture.stdout.txt").write_text(
        result.stdout, encoding="utf-8"
    )
    (ARTIFACT_ROOT / f"godot-{version}-capture.stderr.txt").write_text(
        result.stderr, encoding="utf-8"
    )
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G1 visual capture failed on {version}")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    capture_path = project / "artifacts" / "g1_visual_capture" / "capture.png"
    if not capture_path.is_file():
        raise RuntimeError(f"G1 visual capture image missing: {capture_path}")
    copied_capture = ARTIFACT_ROOT / f"godot-{version}-capture.png"
    copied_capture.write_bytes(capture_path.read_bytes())
    return {
        "engine": version,
        "executable": str(engine),
        "marker": marker_line,
        "capture": str(copied_capture),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Capture the G1 validation playtest viewport to a PNG."
    )
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=CAPTURE_PROJECT)
    parser.add_argument("--windowed", action="store_true")
    arguments = parser.parse_args()

    project = arguments.project.resolve()
    lock = compose(project)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_import(project, version, engine)
        results.append(run_capture(project, version, engine, not arguments.windowed))

    report_path = ARTIFACT_ROOT / "g1_visual_capture_report.json"
    report_path.write_text(
        json.dumps(
            {
                "project": str(project),
                "lock": lock,
                "engines": results,
                "implementation": "visual_capture_check",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        "WT_VALIDATION_G1_VISUAL_CAPTURE_RUN_PASS "
        f"engines={len(results)} report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
