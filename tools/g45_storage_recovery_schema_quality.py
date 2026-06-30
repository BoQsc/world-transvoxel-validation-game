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
from g19_compact_2k_on_demand_smoke import (
    PROFILE_ID,
    PROJECT_WORLD_ROOT,
    assert_compact_project_budget,
)
from prepare_human_playtest import pin_scene_profile, run_project_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g45_storage_recovery_schema_quality"
PROJECT = ARTIFACT_ROOT / "project"
JOURNAL_SCRIPT = "res://tests/g45_storage_recovery_journal.gd"
COMPACTION_SCRIPT = "res://tests/g45_storage_recovery_compaction.gd"
JOURNAL_MARKER = "WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_JOURNAL_PASS"
COMPACTION_MARKER = "WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_COMPACTION_PASS"
MARKER = "WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_SMOKE_PASS"
G45_COMPACTION_OUTPUT = Path("build/production-lifecycle-fixture/g45_compacted_snapshot")
MAX_RUNTIME_SECONDS = 120.0


def parse_marker(marker: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for token in marker.split()[1:]:
        if "=" in token:
            key, value = token.split("=", 1)
            fields[key] = value
    return fields


def reset_runtime_state(project: Path) -> None:
    for relative in (PROJECT_WORLD_ROOT, G45_COMPACTION_OUTPUT):
        path = project / relative
        if path.exists():
            shutil.rmtree(path)


def run_phase(
    project: Path,
    version: str,
    engine: Path,
    script: str,
    marker: str,
    suffix: str,
) -> dict[str, object]:
    started_at = time.perf_counter()
    result = subprocess.run(
        [str(engine), "--path", str(project), "--script", script],
        cwd=project,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=240,
    )
    duration_seconds = time.perf_counter() - started_at
    (ARTIFACT_ROOT / f"godot-{version}-{suffix}.stdout.txt").write_text(
        result.stdout, encoding="utf-8"
    )
    (ARTIFACT_ROOT / f"godot-{version}-{suffix}.stderr.txt").write_text(
        result.stderr, encoding="utf-8"
    )
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or marker not in combined or has_godot_error(combined):
        raise RuntimeError(f"G45 {suffix} phase failed on {version}")
    if duration_seconds > MAX_RUNTIME_SECONDS:
        raise RuntimeError(
            f"G45 {suffix} phase exceeded {MAX_RUNTIME_SECONDS:.0f}s on {version}: "
            f"{duration_seconds:.3f}s"
        )
    marker_line = next(line for line in combined.splitlines() if line.startswith(marker))
    return {
        "script": script,
        "duration_seconds": duration_seconds,
        "marker": marker_line,
        "fields": parse_marker(marker_line),
    }


def synthesize_marker(journal: dict[str, str], compaction: dict[str, str]) -> str:
    max_render = max(int(journal.get("render_resources", "0")), int(compaction.get("render_resources", "0")))
    max_collision = max(int(journal.get("collision_resources", "0")), int(compaction.get("collision_resources", "0")))
    max_active = max(int(journal.get("active_records", "0")), int(compaction.get("active_records", "0")))
    return (
        f"{MARKER} profile={journal.get('profile', '')} "
        f"compact_2k_edits={journal.get('compact_2k_edits', '')} "
        f"compact_2k_replayed={journal.get('compact_2k_replayed', '')} "
        f"compact_2k_recovered={journal.get('compact_2k_recovered', '')} "
        f"journal_magic={journal.get('journal_magic', '')} "
        f"journal_format_version={journal.get('journal_format_version', '')} "
        f"journal_source_revision={journal.get('journal_source_revision', '')} "
        f"journal_bytes={journal.get('journal_bytes', '')} "
        f"truncated_tail_bytes={journal.get('truncated_tail_bytes', '')} "
        f"recovery_truncated_to_bytes={journal.get('recovery_truncated_to_bytes', '')} "
        f"compaction_profile={compaction.get('compaction_profile', '')} "
        f"compacted_pages={compaction.get('compacted_pages', '')} "
        f"compacted_source_revision={compaction.get('compacted_source_revision', '')} "
        f"compacted_world_revision={compaction.get('compacted_world_revision', '')} "
        f"compacted_reopened={compaction.get('compacted_reopened', '')} "
        f"compacted_journal_exists={compaction.get('compacted_journal_exists', '')} "
        f"max_render_resources={max_render} max_collision_resources={max_collision} "
        f"max_active_records={max_active} dense_world_files=0"
    )


def run_runtime(project: Path, version: str, engine: Path) -> dict[str, object]:
    reset_runtime_state(project)
    journal_phase = run_phase(project, version, engine, JOURNAL_SCRIPT, JOURNAL_MARKER, "g45-journal")
    compaction_phase = run_phase(
        project,
        version,
        engine,
        COMPACTION_SCRIPT,
        COMPACTION_MARKER,
        "g45-compaction",
    )
    marker_line = synthesize_marker(
        journal_phase["fields"],  # type: ignore[arg-type]
        compaction_phase["fields"],  # type: ignore[arg-type]
    )
    print(marker_line)
    fields = parse_marker(marker_line)
    if fields.get("profile") != PROFILE_ID or fields.get("dense_world_files") != "0":
        raise RuntimeError(f"G45 marker fields invalid: {marker_line}")
    if (
        fields.get("journal_magic") != "WTEDIT"
        or fields.get("journal_format_version") != "1"
        or fields.get("journal_source_revision") != "190019"
    ):
        raise RuntimeError(f"G45 journal format fields invalid: {marker_line}")
    if fields.get("compact_2k_edits") != "3" or fields.get("compact_2k_replayed") != "3" or fields.get("compact_2k_recovered") != "3":
        raise RuntimeError(f"G45 compact 2K replay/recovery coverage invalid: {marker_line}")
    if fields.get("compaction_profile") != "g8_sparse_2k" or fields.get("compacted_pages") != "93":
        raise RuntimeError(f"G45 compaction coverage invalid: {marker_line}")
    if fields.get("compacted_source_revision") != "8102" or fields.get("compacted_reopened") != "1":
        raise RuntimeError(f"G45 compacted reopen fields invalid: {marker_line}")
    if fields.get("compacted_journal_exists") != "false":
        raise RuntimeError(f"G45 compacted output retained a journal: {marker_line}")
    for field in ("max_render_resources", "max_collision_resources", "max_active_records"):
        if int(fields.get(field, "0")) != 25:
            raise RuntimeError(f"G45 active resource field did not settle to 25: {field} in {marker_line}")
    return {
        "engine": version,
        "executable": str(engine),
        "duration_seconds": float(journal_phase["duration_seconds"]) + float(compaction_phase["duration_seconds"]),
        "marker": marker_line,
        "fields": fields,
        "phases": [journal_phase, compaction_phase],
        "post_run_budget": assert_compact_project_budget(project),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run storage recovery schema quality validation.")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--skip-build", action="store_true")
    arguments = parser.parse_args()

    build_world_transvoxel(arguments.skip_build)
    project = arguments.project.resolve()
    lock = compose(project)
    pin_scene_profile(project, PROFILE_ID)
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_project_import(project, version, engine, ARTIFACT_ROOT)
        results.append(run_runtime(project, version, engine))
    max_duration = max(float(result["duration_seconds"]) for result in results)
    max_journal_bytes = max(int(result["fields"]["journal_bytes"]) for result in results)
    report_path = ARTIFACT_ROOT / "g45_storage_recovery_schema_quality_report.json"
    report_path.write_text(
        json.dumps(
            {
                "project": str(project),
                "lock": lock,
                "profile": PROFILE_ID,
                "engines": results,
                "max_duration_seconds": max_duration,
                "max_journal_bytes": max_journal_bytes,
                "implementation": "storage_recovery_schema_quality",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"{SUMMARY_MARKER} profile={PROFILE_ID} engines={len(results)} compact_2k_edits=3 "
        "compact_2k_replayed=3 compact_2k_recovered=3 compaction_profile=g8_sparse_2k "
        "compacted_pages=93 compacted_reopened=1 quality_track=runtime_terrain "
        f"dense_world_files=0 report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
