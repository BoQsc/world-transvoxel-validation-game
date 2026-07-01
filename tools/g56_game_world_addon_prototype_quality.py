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
from prepare_human_playtest import run_project_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g56_game_world_addon_prototype_quality"
PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g56_game_world_addon_prototype_quality.gd"
MARKER = "WT_VALIDATION_G56_GAME_WORLD_ADDON_PROTOTYPE_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G56_GAME_WORLD_ADDON_PROTOTYPE_SMOKE_PASS"
ADDON_ID = "world_transvoxel_game_world"
MAX_RUNTIME_SECONDS = 180.0
FORBIDDEN_PROJECT_FILES = (
    Path("build") / "g19-compact-on-demand" / "g19_compact_2k_on_demand" / "world.wtworld",
    Path("build") / "g19-compact-on-demand" / "g19_compact_2k_on_demand" / "streaming.wtworld",
    Path("build") / "g19-compact-on-demand" / "g19_compact_2k_on_demand" / "procedural.wtseed",
)


def parse_marker(marker_line: str) -> dict[str, str]:
    return dict(token.split("=", 1) for token in marker_line.split()[1:] if "=" in token)


def reset_runtime_state(project: Path) -> None:
    root = project / "build" / "g19-compact-on-demand"
    if root.exists():
        shutil.rmtree(root)


def static_audit() -> dict[str, object]:
    required = {
        "addons/world_transvoxel_game_world/plugin.cfg": (
            "World Transvoxel Game World Prototype",
            "plugin.gd",
        ),
        "addons/world_transvoxel_game_world/wt_game_world_node.gd": (
            "ADDON_ID",
            "configure_game_world",
            "setup_standard_world",
            "attach_player",
            "update_player_viewer",
            "submit_sphere_edit",
            "get_game_world_summary",
        ),
        "tools/compose_validation_project.py": (
            "world_transvoxel_game_world",
            "addons",
        ),
        "tests/g56_game_world_addon_prototype_quality.gd": (
            MARKER,
            "WorldTransvoxelGameWorld",
            "submit_sphere_edit",
            "player_viewer_updates",
        ),
    }
    errors: list[str] = []
    for relative, phrases in required.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing G56 file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{relative} missing phrase: {phrase}")
        if path.suffix in {".gd", ".py"} and len(text.splitlines()) > 320:
            errors.append(f"G56 source file exceeds line limit: {relative}")
    if errors:
        raise RuntimeError("; ".join(errors))
    return {"implementation": "game_world_addon_prototype_quality", "addon": ADDON_ID}


def assert_no_dense_files(project: Path) -> None:
    for relative in FORBIDDEN_PROJECT_FILES:
        path = project / relative
        if path.exists():
            raise RuntimeError(f"G56 must not create dense compact-2K file: {path}")


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
    (ARTIFACT_ROOT / f"godot-{version}-g56.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g56.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G56 game-world addon prototype failed on {version}")
    if duration > MAX_RUNTIME_SECONDS:
        raise RuntimeError(f"G56 runtime exceeded {MAX_RUNTIME_SECONDS:.0f}s on {version}: {duration:.3f}s")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    fields = parse_marker(marker_line)
    for key in ("standard_world_node", "terrain_node_ready", "player_attached"):
        if fields.get(key) != "1":
            raise RuntimeError(f"G56 missing required {key}: {marker_line}")
    if fields.get("addon") != ADDON_ID or fields.get("api_version") != "1":
        raise RuntimeError(f"G56 addon identity mismatch: {marker_line}")
    if int(fields.get("player_viewer_updates", "0")) < 2 or int(fields.get("edit_replacements", "0")) <= 0:
        raise RuntimeError(f"G56 integration counters invalid: {marker_line}")
    if int(fields.get("render_resources", "0")) != 25 or int(fields.get("collision_resources", "0")) != 25:
        raise RuntimeError(f"G56 compact resources invalid: {marker_line}")
    assert_no_dense_files(project)
    return {"engine": version, "duration_seconds": duration, "marker": marker_line, "fields": fields}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run G56 game-world addon prototype validation.")
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
    assert_no_dense_files(project)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_project_import(project, version, engine, ARTIFACT_ROOT)
        results.append(run_runtime(project, version, engine))
    report_path = ARTIFACT_ROOT / "g56_game_world_addon_prototype_quality_report.json"
    report_path.write_text(
        json.dumps({"project": str(project), "lock": lock, "audit": audit, "engines": results}, indent=2) + "\n",
        encoding="utf-8",
    )
    max_duration = max(float(result["duration_seconds"]) for result in results)
    max_player_updates = max(int(dict(result["fields"]).get("player_viewer_updates", 0)) for result in results)
    max_edit_replacements = max(int(dict(result["fields"]).get("edit_replacements", 0)) for result in results)
    print(
        f"{SUMMARY_MARKER} addon={ADDON_ID} api_version=1 engines={len(results)} "
        f"max_engine_seconds={max_duration:.3f} player_viewer_updates={max_player_updates} "
        f"edit_replacements={max_edit_replacements} render_resources=25 collision_resources=25 "
        f"dense_world_files=0 report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
