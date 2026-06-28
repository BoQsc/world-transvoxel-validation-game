#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess

from g0_install_run_smoke import discover_engines, has_godot_error


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "artifacts" / "root_project_safe_import"
MARKER = "WT_VALIDATION_ROOT_PROJECT_SAFE_IMPORT_PASS"
FORBIDDEN_TEXT = "GDExtension dynamic library not found"


def clear_root_import_cache(project: Path) -> None:
    cache = project / ".godot"
    if cache.exists():
        shutil.rmtree(cache)


def run_import(version: str, engine: Path) -> dict[str, object]:
    clear_root_import_cache(ROOT)
    result = subprocess.run(
        [str(engine), "--headless", "--path", str(ROOT), "--import"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=180,
    )
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    (ARTIFACT_ROOT / f"godot-{version}-import.stdout.txt").write_text(
        result.stdout, encoding="utf-8"
    )
    (ARTIFACT_ROOT / f"godot-{version}-import.stderr.txt").write_text(
        result.stderr, encoding="utf-8"
    )
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or has_godot_error(combined) or FORBIDDEN_TEXT in combined:
        raise RuntimeError(f"root project safe import failed on {version}")
    return {
        "engine": version,
        "executable": str(engine),
        "marker": f"{MARKER} engine={version}",
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify the committed root project imports without addon GDExtension errors."
    )
    parser.add_argument("--godot", type=Path, action="append", default=[])
    arguments = parser.parse_args()

    engines = discover_engines(arguments.godot)
    results = [run_import(version, engine) for version, engine in engines]
    report_path = ARTIFACT_ROOT / "root_project_safe_import_report.json"
    report_path.write_text(
        json.dumps(
            {
                "project": str(ROOT),
                "engines": results,
                "implementation": "root_project_notice_only",
                "forbidden_text": FORBIDDEN_TEXT,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"{MARKER} engines={len(results)} "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
