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
from g8_runtime_active_window_smoke import build_world_transvoxel
from g19_compact_2k_on_demand_smoke import collect_directory_budget
from prepare_human_playtest import run_project_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g55_map_generator_budget_quality"
PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g55_map_generator_budget_quality.gd"
MARKER = "WT_VALIDATION_G55_MAP_GENERATOR_BUDGET_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G55_MAP_GENERATOR_BUDGET_SMOKE_PASS"
PROFILES = (
    "g19_compact_2k_on_demand",
    "g50_seeded_procedural_2k",
)
PROFILE_ROOTS = {
    "g19_compact_2k_on_demand": Path("build") / "g19-compact-on-demand" / "g19_compact_2k_on_demand",
    "g50_seeded_procedural_2k": Path("build") / "g50-seeded-procedural" / "g50_seeded_procedural_2k",
}
FORBIDDEN_PROJECT_FILES = tuple(
    root / filename
    for root in PROFILE_ROOTS.values()
    for filename in ("world.wtworld", "streaming.wtworld", "procedural.wtseed")
)
TARGET_FILE_BYTES = 50 * 1024 * 1024
HARD_FILE_BYTES = 100 * 1024 * 1024
MAX_TOTAL_BYTES = 100 * 1024 * 1024
MAX_LOAD_TO_PLAY_SECONDS = 30.0
MAX_RUNTIME_SECONDS = 180.0


def parse_marker(marker_line: str) -> dict[str, str]:
    return dict(token.split("=", 1) for token in marker_line.split()[1:] if "=" in token)


def reset_runtime_state(project: Path) -> None:
    for root in PROFILE_ROOTS.values():
        path = project / root
        if path.exists():
            shutil.rmtree(path)


def static_audit() -> dict[str, object]:
    required = {
        "tests/g55_map_generator_budget_quality.gd": (
            MARKER,
            "MAX_LOAD_MS",
            "FORBIDDEN_DENSE_FILES",
            "deterministic_reference",
        ),
        "scripts/validation_profile_catalog.gd": (
            "g19_compact_2k_on_demand",
            "g50_seeded_procedural_2k",
            "world_chunk_count_x = 128",
            "world_chunk_count_z = 128",
        ),
        "tools/g19_compact_2k_on_demand_smoke.py": (
            "MAX_GENERATED_FILE_BYTES",
            "MAX_LOAD_TO_PLAY_SECONDS",
        ),
        "tools/g50_terrain_profile_standard_quality.py": (
            "TARGET_FILE_BYTES",
            "MAX_TOTAL_BYTES",
        ),
    }
    errors: list[str] = []
    for relative, phrases in required.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing G55 file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{relative} missing phrase: {phrase}")
        if path.suffix in {".gd", ".py"} and len(text.splitlines()) > 300:
            errors.append(f"G55 source file exceeds line limit: {relative}")
    if errors:
        raise RuntimeError("; ".join(errors))
    return {"implementation": "map_generator_budget_quality", "profiles": PROFILES}


def assert_generator_budgets(project: Path) -> dict[str, object]:
    budgets: dict[str, object] = {}
    for relative in FORBIDDEN_PROJECT_FILES:
        path = project / relative
        if path.exists():
            raise RuntimeError(f"G55 must not create dense/procedural descriptor file: {path}")
    for profile_id, root in PROFILE_ROOTS.items():
        budget = collect_directory_budget(project / root)
        max_file = int(budget["max_file_bytes"])
        total = int(budget["total_bytes"])
        if max_file > HARD_FILE_BYTES:
            raise RuntimeError(f"G55 profile file exceeds 100 MiB hard ceiling: {profile_id} {budget}")
        if max_file > TARGET_FILE_BYTES:
            raise RuntimeError(f"G55 profile file exceeds 50 MiB target: {profile_id} {budget}")
        if total > MAX_TOTAL_BYTES:
            raise RuntimeError(f"G55 profile directory exceeds 100 MiB ceiling: {profile_id} {budget}")
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
    duration = time.perf_counter() - started_at
    (ARTIFACT_ROOT / f"godot-{version}-g55.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g55.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G55 map-generator budget quality failed on {version}")
    if duration > MAX_RUNTIME_SECONDS:
        raise RuntimeError(f"G55 runtime exceeded {MAX_RUNTIME_SECONDS:.0f}s on {version}: {duration:.3f}s")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    fields = parse_marker(marker_line)
    if int(fields.get("profiles", "0")) != len(PROFILES) or int(fields.get("pages", "0")) != 16384:
        raise RuntimeError(f"G55 profile/page coverage invalid: {marker_line}")
    if int(fields.get("max_load_ms", "999999")) > int(MAX_LOAD_TO_PLAY_SECONDS * 1000):
        raise RuntimeError(f"G55 load-to-play budget exceeded: {marker_line}")
    if fields.get("generator_modes") != "deterministic_reference,deterministic_reference":
        raise RuntimeError(f"G55 generator mode coverage invalid: {marker_line}")
    return {"engine": version, "duration_seconds": duration, "marker": marker_line, "fields": fields, "post_run_budgets": assert_generator_budgets(project)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run G55 map-generator budget quality validation.")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--skip-build", action="store_true")
    arguments = parser.parse_args()

    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    audit = static_audit()
    build_world_transvoxel(arguments.skip_build)
    project = arguments.project.resolve()
    lock = compose(project)
    reset_runtime_state(project)
    pre_run_budgets = assert_generator_budgets(project)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_project_import(project, version, engine, ARTIFACT_ROOT)
        results.append(run_runtime(project, version, engine))
    post_run_budgets = assert_generator_budgets(project)
    max_duration = max(float(result["duration_seconds"]) for result in results)
    max_file = max(int(dict(budget).get("max_file_bytes", 0)) for budget in post_run_budgets.values())
    max_total = max(int(dict(budget).get("total_bytes", 0)) for budget in post_run_budgets.values())
    report_path = ARTIFACT_ROOT / "g55_map_generator_budget_quality_report.json"
    report_path.write_text(
        json.dumps({"project": str(project), "lock": lock, "audit": audit, "pre_run_budgets": pre_run_budgets, "post_run_budgets": post_run_budgets, "engines": results}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"{SUMMARY_MARKER} profiles={len(PROFILES)} engines={len(results)} "
        f"max_engine_seconds={max_duration:.3f} max_file_bytes={max_file} "
        f"max_total_bytes={max_total} target_file_bytes={TARGET_FILE_BYTES} "
        f"hard_file_bytes={HARD_FILE_BYTES} dense_world_files=0 "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
