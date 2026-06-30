#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time

from compose_validation_project import ROOT, compose
from g0_install_run_smoke import discover_engines, has_godot_error
from g3_generation_modes_smoke import copy_worlds_into_project, generate_worlds
from g8_runtime_active_window_smoke import build_world_transvoxel
from g19_compact_2k_on_demand_smoke import collect_directory_budget
from prepare_human_playtest import run_project_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g50_terrain_profile_standard_quality"
PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g50_terrain_profile_standard_quality.gd"
MARKER = "WT_VALIDATION_G50_TERRAIN_PROFILE_STANDARD_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G50_TERRAIN_PROFILE_STANDARD_SMOKE_PASS"
STANDARD_PROFILES = (
    "flat_baseline",
    "mountain_8x8",
    "g19_compact_2k_on_demand",
    "g50_seeded_procedural_2k",
)
PROFILE_ROOTS = {
    "flat_baseline": Path("build") / "production-lifecycle-fixture",
    "mountain_8x8": Path("build") / "g3-generation-fixtures" / "mountain_8x8",
    "g19_compact_2k_on_demand": Path("build") / "g19-compact-on-demand" / "g19_compact_2k_on_demand",
    "g50_seeded_procedural_2k": Path("build") / "g50-seeded-procedural" / "g50_seeded_procedural_2k",
}
FORBIDDEN_PROJECT_FILES = (
    PROFILE_ROOTS["g19_compact_2k_on_demand"] / "world.wtworld",
    PROFILE_ROOTS["g19_compact_2k_on_demand"] / "streaming.wtworld",
    PROFILE_ROOTS["g19_compact_2k_on_demand"] / "procedural.wtseed",
    PROFILE_ROOTS["g50_seeded_procedural_2k"] / "world.wtworld",
    PROFILE_ROOTS["g50_seeded_procedural_2k"] / "streaming.wtworld",
    PROFILE_ROOTS["g50_seeded_procedural_2k"] / "procedural.wtseed",
)
MAX_LOAD_TO_PLAY_SECONDS = 30.0
MAX_RUNTIME_SECONDS = 180.0
TARGET_FILE_BYTES = 50 * 1024 * 1024
MAX_TOTAL_BYTES = 100 * 1024 * 1024


def parse_marker(marker_line: str) -> dict[str, str]:
    return dict(token.split("=", 1) for token in marker_line.split()[1:] if "=" in token)


def reset_runtime_state(project: Path) -> None:
    for profile_id in ("g19_compact_2k_on_demand", "g50_seeded_procedural_2k"):
        path = project / PROFILE_ROOTS[profile_id]
        if path.exists():
            shutil.rmtree(path)


def static_audit() -> dict[str, object]:
    required = {
        "scripts/validation_profile_catalog.gd": (
            "g50_seeded_procedural_2k",
            "50050",
            "g50-seeded-procedural",
        ),
        "scripts/validation_profile_standard_contract.gd": (
            "terrain_profile_standard_contract_v1",
            "flat_baseline",
            "mountain_8x8",
            "g19_compact_2k_on_demand",
            "g50_seeded_procedural_2k",
        ),
        "tests/g50_terrain_profile_standard_quality.gd": (
            MARKER,
            "MAX_LOAD_MS",
            "EXPECTED_PROCEDURAL_PAGE_COUNT",
        ),
    }
    errors: list[str] = []
    for relative, phrases in required.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing G50 file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{relative} missing phrase: {phrase}")
    for relative in required:
        path = ROOT / relative
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
            errors.append(f"G50 source file exceeds line limit: {relative}")
    if errors:
        raise RuntimeError("; ".join(errors))
    return {"profiles": STANDARD_PROFILES, "implementation": "terrain_profile_standard_quality"}


def assert_profile_budgets(project: Path) -> dict[str, object]:
    budgets: dict[str, object] = {}
    for relative in FORBIDDEN_PROJECT_FILES:
        path = project / relative
        if path.exists():
            raise RuntimeError(f"G50 must not create dense/procedural descriptor file: {path}")
    for profile_id, root in PROFILE_ROOTS.items():
        budget = collect_directory_budget(project / root)
        if int(budget["max_file_bytes"]) > TARGET_FILE_BYTES:
            raise RuntimeError(f"G50 profile file exceeds 50 MiB target: {profile_id} {budget}")
        if int(budget["total_bytes"]) > MAX_TOTAL_BYTES:
            raise RuntimeError(f"G50 profile directory exceeds 100 MiB ceiling: {profile_id} {budget}")
        budgets[profile_id] = budget
    return budgets


def run_runtime(project: Path, version: str, engine: Path) -> dict[str, object]:
    reset_runtime_state(project)
    started_at = time.perf_counter()
    result = subprocess.run(
        [str(engine), "--path", str(project), "--script", SCRIPT],
        cwd=project,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=300,
    )
    duration_seconds = time.perf_counter() - started_at
    (ARTIFACT_ROOT / f"godot-{version}-g50.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g50.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G50 terrain profile standard failed on {version}")
    if duration_seconds > MAX_RUNTIME_SECONDS:
        raise RuntimeError(f"G50 runtime exceeded {MAX_RUNTIME_SECONDS:.0f}s on {version}: {duration_seconds:.3f}s")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    fields = parse_marker(marker_line)
    if int(fields.get("profiles", "0")) != 4 or int(fields.get("runtime_profiles", "0")) != 4:
        raise RuntimeError(f"G50 profile coverage invalid: {marker_line}")
    if int(fields.get("deterministic", "0")) != 4 or int(fields.get("budgets", "0")) != 4:
        raise RuntimeError(f"G50 determinism/budget coverage invalid: {marker_line}")
    if int(fields.get("max_profile_load_ms", "0")) > int(MAX_LOAD_TO_PLAY_SECONDS * 1000):
        raise RuntimeError(f"G50 load-to-play budget exceeded: {marker_line}")
    return {
        "engine": version,
        "duration_seconds": duration_seconds,
        "marker": marker_line,
        "fields": fields,
        "post_run_budgets": assert_profile_budgets(project),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run G50 terrain profile standard quality validation.")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--skip-build", action="store_true")
    arguments = parser.parse_args()

    audit = static_audit()
    build_world_transvoxel(arguments.skip_build)
    bake = generate_worlds()
    project = arguments.project.resolve()
    lock = compose(project)
    copy_worlds_into_project(project)
    reset_runtime_state(project)
    pre_run_budgets = assert_profile_budgets(project)
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_project_import(project, version, engine, ARTIFACT_ROOT)
        results.append(run_runtime(project, version, engine))
    max_engine_seconds = max(float(result["duration_seconds"]) for result in results)
    post_run_budgets = assert_profile_budgets(project)
    report_path = ARTIFACT_ROOT / "g50_terrain_profile_standard_quality_report.json"
    report_path.write_text(
        json.dumps(
            {
                "project": str(project),
                "lock": lock,
                "audit": audit,
                "bake": bake,
                "pre_run_budgets": pre_run_budgets,
                "post_run_budgets": post_run_budgets,
                "engines": results,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"{SUMMARY_MARKER} profiles=4 engines={len(results)} deterministic=4 budgets=4 "
        f"max_engine_seconds={max_engine_seconds:.3f} max_file_bytes={_max_budget_file(post_run_budgets)} "
        f"dense_world_files=0 report={report_path.relative_to(ROOT).as_posix()}"
    )


def _max_budget_file(budgets: dict[str, object]) -> int:
    return max(int(dict(budget).get("max_file_bytes", 0)) for budget in budgets.values())


if __name__ == "__main__":
    main()
