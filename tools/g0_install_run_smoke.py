#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

from compose_validation_project import DEFAULT_OUTPUT, ROOT, compose


ARTIFACT_ROOT = ROOT / "artifacts" / "g0_install_run_smoke"
SCRIPT = "res://tests/g0_install_run_smoke.gd"
MARKER = "WT_VALIDATION_G0_GODOT_PASS"
ENGINE_VERSIONS = ("4.6.3", "4.7")


def discover_engines(explicit: list[Path]) -> list[tuple[str, Path]]:
    if explicit:
        return [(path.stem, path.resolve()) for path in explicit]

    sibling = ROOT.parent / "world-transvoxel" / ".tools" / "godot"
    discovered: list[tuple[str, Path]] = []
    for version in ENGINE_VERSIONS:
        folder = sibling / version
        candidates = sorted(folder.glob("Godot*_win64.exe"))
        if candidates:
            discovered.append((version, candidates[0].resolve()))
    if discovered:
        return discovered

    environment = os.environ.get("GODOT")
    if environment:
        return [("environment", Path(environment).resolve())]

    executable = shutil.which("godot")
    if executable:
        return [("path", Path(executable).resolve())]

    raise RuntimeError("No Godot executable found. Pass --godot or set GODOT.")


def has_godot_error(combined: str) -> bool:
    return (
        "SCRIPT ERROR:" in combined
        or combined.startswith("ERROR:")
        or "\nERROR:" in combined
    )


def run_import(project: Path, version: str, engine: Path) -> None:
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    extension_cache = project / ".godot" / "extension_list.cfg"
    attempts: list[str] = []
    result: subprocess.CompletedProcess[str] | None = None
    for _attempt in range(2):
        result = subprocess.run(
            [str(engine), "--headless", "--path", str(project), "--import"],
            cwd=project,
            check=False,
            text=True,
            capture_output=True,
            errors="replace",
            timeout=180,
        )
        combined_attempt = result.stdout + result.stderr
        attempts.append(combined_attempt)
        cache_valid = (
            extension_cache.is_file()
            and "res://addons/world_transvoxel/world_transvoxel.gdextension"
            in extension_cache.read_text(encoding="utf-8", errors="replace")
        )
        if cache_valid and not has_godot_error(combined_attempt):
            break
    (ARTIFACT_ROOT / f"godot-{version}-import.stdout.txt").write_text(
        "\n".join(attempts), encoding="utf-8"
    )
    (ARTIFACT_ROOT / f"godot-{version}-import.stderr.txt").write_text(
        "", encoding="utf-8"
    )
    combined = "\n".join(attempts)
    cache_valid = (
        extension_cache.is_file()
        and "res://addons/world_transvoxel/world_transvoxel.gdextension"
        in extension_cache.read_text(encoding="utf-8", errors="replace")
    )
    if result is None or has_godot_error(combined) or not cache_valid:
        raise RuntimeError(f"G0 validation import failed on {version}")


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
        raise RuntimeError(f"G0 validation smoke failed on {version}")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    return {
        "engine": version,
        "executable": str(engine),
        "marker": marker_line,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the G0 install/run validation smoke in a composed Godot project."
    )
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    project = arguments.project.resolve()
    lock = compose(project)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_import(project, version, engine)
        results.append(run_smoke(project, version, engine))

    report_path = ARTIFACT_ROOT / "g0_install_run_smoke_report.json"
    report_path.write_text(
        json.dumps(
            {
                "project": str(project),
                "lock": lock,
                "engines": results,
                "implementation": "install_run_validation",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        "WT_VALIDATION_G0_SMOKE_PASS "
        f"engines={len(results)} report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
