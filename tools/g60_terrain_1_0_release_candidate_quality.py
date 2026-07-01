#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

from compose_validation_project import ROOT
from g8_runtime_active_window_smoke import build_world_transvoxel


ARTIFACT_ROOT = ROOT / "artifacts" / "g60_terrain_1_0_release_candidate_quality"
MARKER = "WT_VALIDATION_G60_TERRAIN_1_0_RELEASE_CANDIDATE_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G60_TERRAIN_1_0_RELEASE_CANDIDATE_SMOKE_PASS"
VALIDATORS = [
    "validate_g41_contract.py",
    "validate_g42_contract.py",
    "validate_g43_contract.py",
    "validate_g44_contract.py",
    "validate_g45_contract.py",
    "validate_g46_contract.py",
    "validate_g47_contract.py",
    "validate_g48_contract.py",
    "validate_g49_contract.py",
    "validate_g50_contract.py",
    "validate_g51_contract.py",
    "validate_g52_contract.py",
    "validate_g53_contract.py",
    "validate_g54_contract.py",
    "validate_g55_contract.py",
    "validate_g56_contract.py",
    "validate_g57_contract.py",
    "validate_g58_contract.py",
    "validate_g59_contract.py",
    "validate_playable_world_target.py",
    "validate_production_gap_audit.py",
    "validate_finite_production_roadmap.py",
]
RUNTIME_GATES = [
    "g41_runtime_frame_budget_telemetry_quality.py",
    "g42_collision_traversal_stability_quality.py",
    "g43_view_distance_presentation_quality.py",
    "g44_edit_policy_shape_quality.py",
    "g45_storage_recovery_schema_quality.py",
    "g46_terrain_addon_api_contract_quality.py",
    "g47_validation_workaround_removal_quality.py",
    "g48_native_hot_path_boundary_quality.py",
    "g49_debug_telemetry_ui_quality.py",
    "g50_terrain_profile_standard_quality.py",
    "g51_material_texture_pipeline_quality.py",
    "g52_underground_terrain_variation_quality.py",
    "g53_large_world_streaming_radius_quality.py",
    "g54_lod_seam_artifact_quality.py",
    "g55_map_generator_budget_quality.py",
    "g56_game_world_addon_prototype_quality.py",
    "g57_separate_game_repository_integration_quality.py",
    "g58_documentation_examples_quality.py",
    "g59_versioning_release_contract_quality.py",
]
SKIP_BUILD_GATES = set(RUNTIME_GATES[:17])
CRITICAL_BLOCKERS = []


def run_command(label: str, command: list[str], timeout: int) -> dict[str, object]:
    started = time.perf_counter()
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=timeout,
    )
    duration = time.perf_counter() - started
    combined = result.stdout + result.stderr
    safe_label = label.replace("/", "_").replace("\\", "_")
    (ARTIFACT_ROOT / f"{safe_label}.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"{safe_label}.stderr.txt").write_text(result.stderr, encoding="utf-8")
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or "PASS" not in combined:
        raise RuntimeError(f"G60 command failed: {label}")
    return {"label": label, "seconds": duration, "returncode": result.returncode}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the G60 Terrain 1.0 release candidate suite.")
    parser.add_argument("--skip-build", action="store_true")
    arguments = parser.parse_args()

    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    build_world_transvoxel(arguments.skip_build)
    validator_results = [
        run_command(f"validator_{name}", [sys.executable, str(ROOT / "tools" / name)], 120)
        for name in VALIDATORS
    ]
    runtime_results = []
    for name in RUNTIME_GATES:
        command = [sys.executable, str(ROOT / "tools" / name)]
        if name in SKIP_BUILD_GATES:
            command.append("--skip-build")
        runtime_results.append(run_command(f"runtime_{name}", command, 420))
    if CRITICAL_BLOCKERS:
        raise RuntimeError(f"G60 critical blockers remain: {CRITICAL_BLOCKERS}")
    report = {
        "validators": validator_results,
        "runtime_gates": runtime_results,
        "critical_blockers": CRITICAL_BLOCKERS,
        "build_skipped": arguments.skip_build,
    }
    report_path = ARTIFACT_ROOT / "g60_terrain_1_0_release_candidate_quality_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"{MARKER} validators={len(validator_results)} runtime_gates={len(runtime_results)} "
        f"critical_blockers={len(CRITICAL_BLOCKERS)}"
    )
    print(
        f"{SUMMARY_MARKER} validators={len(validator_results)} runtime_gates={len(runtime_results)} "
        f"critical_blockers={len(CRITICAL_BLOCKERS)} report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
