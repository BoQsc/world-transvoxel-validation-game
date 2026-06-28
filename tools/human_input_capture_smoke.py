#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
import subprocess

from compose_validation_project import ROOT, compose
from g0_install_run_smoke import discover_engines, has_godot_error, run_import


ARTIFACT_ROOT = ROOT / "artifacts" / "human_input_capture"
PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/human_input_capture_smoke.gd"
MARKER = "WT_VALIDATION_HUMAN_INPUT_CAPTURE_PASS"


def run_smoke(project: Path, version: str, engine: Path) -> dict[str, object]:
    command = [str(engine), "--path", str(project), "--script", SCRIPT]
    result = subprocess.run(
        command,
        cwd=project,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=120,
    )
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    (ARTIFACT_ROOT / f"godot-{version}-input.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-input.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"human input capture smoke failed on {version}")
    return {
        "engine": version,
        "executable": str(engine),
        "marker": next(line for line in combined.splitlines() if line.startswith(MARKER)),
    }


def main() -> None:
    project = PROJECT.resolve()
    lock = compose(project)
    engines = discover_engines([])
    results = []
    for version, engine in engines:
        run_import(project, version, engine)
        results.append(run_smoke(project, version, engine))
    report_path = ARTIFACT_ROOT / "human_input_capture_report.json"
    report_path.write_text(
        json.dumps({"project": str(project), "lock": lock, "engines": results}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        "WT_VALIDATION_HUMAN_INPUT_CAPTURE_SMOKE_PASS "
        f"engines={len(results)} report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
