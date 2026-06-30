#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import subprocess
import time

from compose_validation_project import ROOT
from g0_install_run_smoke import discover_engines, has_godot_error
from g19_compact_2k_on_demand_smoke import PROFILE_ID, assert_compact_project_budget
from g31_review_bundle_launch_preflight import (
    SOURCE_BUNDLE,
    assert_original_bundle_human_ready,
    load_manifest,
    prepare_launch_copy,
    reset_directory,
)
from prepare_human_playtest import run_project_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g32_review_bundle_runtime_proof"
RUNTIME_BUNDLE = ARTIFACT_ROOT / "bundle_runtime_copy"
MARKER = "WT_VALIDATION_G32_REVIEW_BUNDLE_RUNTIME_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G32_REVIEW_BUNDLE_RUNTIME_SMOKE_PASS"
MAX_TEST_SECONDS = 180.0


@dataclass(frozen=True)
class RuntimeProofScript:
    test_id: str
    script: str
    marker: str
    project_artifact: str
    min_pngs: int


RUNTIME_SCRIPTS = (
    RuntimeProofScript(
        "g25_full_terrain_visual_baseline",
        "res://tests/g25_full_terrain_visual_baseline.gd",
        "WT_VALIDATION_G25_FULL_TERRAIN_VISUAL_BASELINE_PASS",
        "g25_full_terrain_visual_baseline",
        1,
    ),
    RuntimeProofScript(
        "g26_full_terrain_playable_experience",
        "res://tests/g26_full_terrain_playable_experience.gd",
        "WT_VALIDATION_G26_FULL_TERRAIN_PLAYABLE_EXPERIENCE_PASS",
        "g26_full_terrain_playable_experience",
        3,
    ),
    RuntimeProofScript(
        "g27_full_terrain_handoff_preflight",
        "res://tests/g27_full_terrain_handoff_preflight.gd",
        "WT_VALIDATION_G27_FULL_TERRAIN_HANDOFF_PREFLIGHT_PASS",
        "g27_full_terrain_handoff_preflight",
        2,
    ),
)


def safe_name(value: str) -> str:
    return "".join(character if character.isalnum() or character in ".-_" else "_" for character in value)


def collect_files(path: Path) -> list[Path]:
    return sorted(file_path for file_path in path.rglob("*") if file_path.is_file())


def file_record(path: Path, base: Path) -> dict[str, object]:
    return {"path": path.relative_to(base).as_posix(), "bytes": path.stat().st_size}


def reset_project_artifact(project: Path, artifact_name: str) -> Path:
    path = project / "artifacts" / artifact_name
    if path.exists():
        shutil.rmtree(path)
    return path


def copy_runtime_evidence(project: Path, version: str, proof: RuntimeProofScript) -> dict[str, object]:
    source = project / "artifacts" / proof.project_artifact
    if not source.is_dir():
        raise RuntimeError(f"G32 missing runtime evidence directory: {source}")
    target = ARTIFACT_ROOT / "evidence" / safe_name(version) / proof.test_id
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    files = collect_files(target)
    pngs = [path for path in files if path.suffix.lower() == ".png"]
    if len(pngs) < proof.min_pngs:
        raise RuntimeError(
            f"G32 expected at least {proof.min_pngs} PNG captures for {proof.test_id}, got {len(pngs)}"
        )
    return {
        "directory": str(target),
        "file_count": len(files),
        "png_count": len(pngs),
        "files": [file_record(path, ARTIFACT_ROOT) for path in files],
    }


def write_log(version: str, test_id: str, stream: str, text: str) -> None:
    path = ARTIFACT_ROOT / f"godot-{safe_name(version)}-{test_id}.{stream}.txt"
    path.write_text(text, encoding="utf-8")


def run_runtime_script(project: Path, version: str, engine: Path, proof: RuntimeProofScript) -> dict[str, object]:
    reset_project_artifact(project, proof.project_artifact)
    command = [str(engine), "--path", str(project), "--script", proof.script]
    started_at = time.perf_counter()
    result = subprocess.run(
        command,
        cwd=project,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=MAX_TEST_SECONDS + 30.0,
    )
    duration_seconds = time.perf_counter() - started_at
    write_log(version, proof.test_id, "stdout", result.stdout)
    write_log(version, proof.test_id, "stderr", result.stderr)
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or proof.marker not in combined or has_godot_error(combined):
        raise RuntimeError(f"G32 runtime proof failed for {proof.test_id} on {version}")
    if duration_seconds > MAX_TEST_SECONDS:
        raise RuntimeError(
            f"G32 runtime proof exceeded {MAX_TEST_SECONDS:.0f}s for {proof.test_id} on {version}: "
            f"{duration_seconds:.3f}s"
        )
    return {
        "engine": version,
        "test_id": proof.test_id,
        "script": proof.script,
        "duration_seconds": duration_seconds,
        "marker": next(line for line in combined.splitlines() if line.startswith(proof.marker)),
        "evidence": copy_runtime_evidence(project, version, proof),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run exact review-bundle autonomous runtime proof.")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--source-bundle", type=Path, default=SOURCE_BUNDLE)
    parser.add_argument("--output", type=Path, default=ARTIFACT_ROOT)
    arguments = parser.parse_args()

    output_root = arguments.output.resolve()
    reset_directory(output_root)
    source_bundle = arguments.source_bundle.resolve()
    manifest = load_manifest(source_bundle / "HANDOFF_MANIFEST.json")
    assert_original_bundle_human_ready(source_bundle)
    runtime_project = prepare_launch_copy(source_bundle, output_root / "bundle_runtime_copy")
    pre_run_budget = assert_compact_project_budget(runtime_project)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_project_import(runtime_project, version, engine, ARTIFACT_ROOT)
        for proof in RUNTIME_SCRIPTS:
            results.append(run_runtime_script(runtime_project, version, engine, proof))
    assert_original_bundle_human_ready(source_bundle)
    post_run_budget = assert_compact_project_budget(runtime_project)
    max_duration = max(float(result["duration_seconds"]) for result in results)
    report_path = output_root / "g32_review_bundle_runtime_proof_report.json"
    report_path.write_text(
        json.dumps(
            {
                "source_bundle": str(source_bundle),
                "runtime_project": str(runtime_project),
                "profile": PROFILE_ID,
                "manifest_implementation": manifest.get("implementation"),
                "automation_human_input_enabled": False,
                "source_bundle_human_input_enabled": True,
                "pre_run_budget": pre_run_budget,
                "post_run_budget": post_run_budget,
                "results": results,
                "implementation": "review_bundle_runtime_proof",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"{MARKER} profile={PROFILE_ID} engines={len(engines)} scripts={len(results)} "
        "exact_review_bundle=true g25=true g26=true g27=true map_blocks=2048 "
        f"max_script_seconds={max_duration:.3f} runtime_copy_human_input=false "
        "source_bundle_human_input=true dense_world_files=0"
    )
    print(
        f"{SUMMARY_MARKER} engines={len(engines)} scripts={len(results)} "
        f"max_script_seconds={max_duration:.3f} report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
