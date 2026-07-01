#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time

from compose_validation_project import ROOT, GAMEWORLD_REPO, compose, git_output
from g0_install_run_smoke import discover_engines, has_godot_error
from g8_runtime_active_window_smoke import build_world_transvoxel
from prepare_human_playtest import run_project_import


ARTIFACT_ROOT = ROOT / "artifacts" / "p1_gameworld_addon_extraction_quality"
PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/p1_gameworld_addon_extraction_quality.gd"
MARKER = "WT_VALIDATION_P1_GAMEWORLD_ADDON_EXTRACTION_PASS"
SUMMARY_MARKER = "WT_VALIDATION_P1_GAMEWORLD_ADDON_EXTRACTION_SMOKE_PASS"
ADDON_ID = "world_transvoxel_gameworld"
MAX_RUNTIME_SECONDS = 180.0
FORBIDDEN_INTERNAL_NAMES = {"tests", "tools", "scenes", "artifacts", "build"}
FORBIDDEN_INTERNAL_TEXT = (
    "world-transvoxel-validation-game",
    "validation_playtest",
    "validation_profile_catalog",
    "g56_game_world_addon_prototype_quality",
)
FORBIDDEN_PROJECT_FILES = (
    Path("build") / "g19-compact-on-demand" / "g19_compact_2k_on_demand" / "world.wtworld",
    Path("build") / "g19-compact-on-demand" / "g19_compact_2k_on_demand" / "streaming.wtworld",
    Path("build") / "g19-compact-on-demand" / "g19_compact_2k_on_demand" / "procedural.wtseed",
)


def parse_marker(marker_line: str) -> dict[str, str]:
    return dict(token.split("=", 1) for token in marker_line.split()[1:] if "=" in token)


def clean_copytree(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns(".git", "__pycache__", ".godot", "artifacts", "build"))


def assert_no_validation_internals() -> None:
    addon_root = GAMEWORLD_REPO / "addons" / ADDON_ID
    if not addon_root.is_dir():
        raise RuntimeError(f"missing gameworld addon root: {addon_root}")
    for path in GAMEWORLD_REPO.iterdir():
        if path.name in FORBIDDEN_INTERNAL_NAMES:
            raise RuntimeError(f"gameworld repo contains validation-style directory: {path.name}")
    for path in addon_root.rglob("*"):
        if path.is_file() and path.suffix in {".gd", ".cfg", ".md"}:
            text = path.read_text(encoding="utf-8")
            for phrase in FORBIDDEN_INTERNAL_TEXT:
                if phrase in text:
                    raise RuntimeError(f"gameworld addon contains validation text {phrase}: {path}")


def static_audit() -> dict[str, object]:
    assert_no_validation_internals()
    required = {
        GAMEWORLD_REPO / "README.md": ("world_transvoxel_gameworld", "must not contain validation-game scripts"),
        GAMEWORLD_REPO / "addons" / ADDON_ID / "plugin.cfg": ("World Transvoxel Gameworld", "plugin.gd"),
        GAMEWORLD_REPO / "addons" / ADDON_ID / "wt_game_world_node.gd": (
            'const ADDON_ID := "world_transvoxel_gameworld"',
            "configure_game_world",
            "submit_sphere_edit",
            "get_game_world_summary",
        ),
        ROOT / "tests" / "p1_gameworld_addon_extraction_quality.gd": (MARKER, ADDON_ID),
    }
    errors: list[str] = []
    for path, phrases in required.items():
        if not path.is_file():
            errors.append(f"missing required P1 path: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{path} missing phrase: {phrase}")
    if errors:
        raise RuntimeError("; ".join(errors))
    return {
        "implementation": "gameworld_addon_extraction_quality",
        "addon": ADDON_ID,
        "gameworld_repo": str(GAMEWORLD_REPO),
        "gameworld_commit": git_output(GAMEWORLD_REPO, "rev-parse", "HEAD") if (GAMEWORLD_REPO / ".git").exists() else "uncommitted",
    }


def install_gameworld_addon(project: Path) -> None:
    clean_copytree(GAMEWORLD_REPO / "addons" / ADDON_ID, project / "addons" / ADDON_ID)
    project_file = project / "project.godot"
    text = project_file.read_text(encoding="utf-8")
    old = 'enabled=PackedStringArray("res://addons/world_transvoxel/plugin.cfg", "res://addons/world_transvoxel_terrain/plugin.cfg", "res://addons/world_transvoxel_game_world/plugin.cfg")'
    new = 'enabled=PackedStringArray("res://addons/world_transvoxel/plugin.cfg", "res://addons/world_transvoxel_terrain/plugin.cfg", "res://addons/world_transvoxel_game_world/plugin.cfg", "res://addons/world_transvoxel_gameworld/plugin.cfg")'
    project_file.write_text(text.replace(old, new), encoding="utf-8")


def reset_runtime_state(project: Path) -> None:
    root = project / "build" / "g19-compact-on-demand"
    if root.exists():
        shutil.rmtree(root)


def assert_no_dense_files(project: Path) -> None:
    for relative in FORBIDDEN_PROJECT_FILES:
        path = project / relative
        if path.exists():
            raise RuntimeError(f"P1 must not create dense compact-2K file: {path}")


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
    (ARTIFACT_ROOT / f"godot-{version}-p1.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-p1.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"P1 gameworld extraction runtime failed on {version}")
    if duration > MAX_RUNTIME_SECONDS:
        raise RuntimeError(f"P1 runtime exceeded {MAX_RUNTIME_SECONDS:.0f}s on {version}: {duration:.3f}s")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    fields = parse_marker(marker_line)
    if fields.get("addon") != ADDON_ID or fields.get("api_version") != "1":
        raise RuntimeError(f"P1 addon identity mismatch: {marker_line}")
    if fields.get("validation_internals") != "0":
        raise RuntimeError(f"P1 validation internals leaked: {marker_line}")
    if int(fields.get("player_viewer_updates", "0")) < 2 or int(fields.get("edit_replacements", "0")) <= 0:
        raise RuntimeError(f"P1 integration counters invalid: {marker_line}")
    if int(fields.get("render_resources", "0")) != 25 or int(fields.get("collision_resources", "0")) != 25:
        raise RuntimeError(f"P1 compact resources invalid: {marker_line}")
    assert_no_dense_files(project)
    return {"engine": version, "duration_seconds": duration, "marker": marker_line, "fields": fields}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run P1 gameworld addon extraction validation.")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--skip-build", action="store_true")
    arguments = parser.parse_args()

    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    audit = static_audit()
    build_world_transvoxel(arguments.skip_build)
    project = arguments.project.resolve()
    lock = compose(project)
    install_gameworld_addon(project)
    reset_runtime_state(project)
    assert_no_dense_files(project)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_project_import(project, version, engine, ARTIFACT_ROOT)
        results.append(run_runtime(project, version, engine))
    report_path = ARTIFACT_ROOT / "p1_gameworld_addon_extraction_quality_report.json"
    report_path.write_text(
        json.dumps({"project": str(project), "lock": lock, "audit": audit, "engines": results}, indent=2) + "\n",
        encoding="utf-8",
    )
    max_duration = max(float(result["duration_seconds"]) for result in results)
    max_player_updates = max(int(dict(result["fields"]).get("player_viewer_updates", 0)) for result in results)
    max_edit_replacements = max(int(dict(result["fields"]).get("edit_replacements", 0)) for result in results)
    print(
        f"{SUMMARY_MARKER} addon={ADDON_ID} api_version=1 engines={len(results)} "
        f"max_engine_seconds={max_duration:.3f} validation_internals=0 "
        f"player_viewer_updates={max_player_updates} edit_replacements={max_edit_replacements} "
        f"render_resources=25 collision_resources=25 dense_world_files=0 "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
