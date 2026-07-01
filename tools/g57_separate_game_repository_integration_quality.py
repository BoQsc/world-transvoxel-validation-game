#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time

from compose_validation_project import ROOT, REPOSITORY_ROOT, TERRAIN_REPO, WORLD_TRANSVOXEL_REPO, git_output
from g57_integration_repo_templates import (
    GITIGNORE,
    MAIN_SCENE,
    MAIN_SCRIPT,
    PLAYER_STUB,
    PROJECT_GODOT,
    README,
    RUNTIME_SCRIPT,
)
from g0_install_run_smoke import discover_engines, has_godot_error
from g8_runtime_active_window_smoke import build_world_transvoxel
from prepare_human_playtest import run_project_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g57_separate_game_repository_integration_quality"
DEFAULT_REPO = REPOSITORY_ROOT / "world-transvoxel-integration-game"
SCRIPT = "res://scripts/g57_integration_runtime.gd"
MARKER = "WT_INTEGRATION_GAME_G57_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G57_SEPARATE_GAME_REPOSITORY_SMOKE_PASS"
ADDON_ID = "world_transvoxel_game_world"
MAX_RUNTIME_SECONDS = 180.0
FORBIDDEN_PROJECT_FILES = (
    Path("build") / "g57-integration-game" / "g57_integration_2k" / "world.wtworld",
    Path("build") / "g57-integration-game" / "g57_integration_2k" / "streaming.wtworld",
    Path("build") / "g57-integration-game" / "g57_integration_2k" / "procedural.wtseed",
)
FORBIDDEN_INTERNAL_PATHS = (
    Path("scenes") / "validation_playtest.tscn",
    Path("scripts") / "validation_playtest.gd",
    Path("tests"),
    Path("tools"),
)
FORBIDDEN_INTERNAL_TEXT = (
    "world-transvoxel-validation-game",
    "validation_playtest",
    "validation_profile",
    "res://scripts/validation",
)


def parse_marker(marker_line: str) -> dict[str, str]:
    return dict(token.split("=", 1) for token in marker_line.split()[1:] if "=" in token)


def clean_copytree(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".godot", "artifacts", "build"),
    )


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def ensure_git_repo(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    if not (repo / ".git").exists():
        subprocess.run(["git", "init"], cwd=repo, check=True, text=True, capture_output=True)


def compose_integration_repo(repo: Path) -> dict[str, object]:
    ensure_git_repo(repo)
    write_file(repo / ".gitignore", GITIGNORE)
    write_file(repo / "README.md", README)
    write_file(repo / "project.godot", PROJECT_GODOT)
    write_file(repo / "scenes" / "main.tscn", MAIN_SCENE)
    write_file(repo / "scripts" / "main.gd", MAIN_SCRIPT)
    write_file(repo / "scripts" / "g57_player_stub.gd", PLAYER_STUB)
    write_file(repo / "scripts" / "g57_integration_runtime.gd", RUNTIME_SCRIPT)
    clean_copytree(WORLD_TRANSVOXEL_REPO / "addons" / "world_transvoxel", repo / "addons" / "world_transvoxel")
    clean_copytree(TERRAIN_REPO / "addons" / "world_transvoxel_terrain", repo / "addons" / "world_transvoxel_terrain")
    clean_copytree(ROOT / "addons" / "world_transvoxel_game_world", repo / "addons" / "world_transvoxel_game_world")
    return {
        "repo": str(repo),
        "world-transvoxel": git_output(WORLD_TRANSVOXEL_REPO, "rev-parse", "HEAD"),
        "world-transvoxel-terrain": git_output(TERRAIN_REPO, "rev-parse", "HEAD"),
        "world-transvoxel-game-world-prototype": git_output(ROOT, "rev-parse", "HEAD"),
    }


def reset_runtime_state(repo: Path) -> None:
    build = repo / "build" / "g57-integration-game"
    if build.exists():
        shutil.rmtree(build)


def assert_no_dense_files(repo: Path) -> None:
    for relative in FORBIDDEN_PROJECT_FILES:
        path = repo / relative
        if path.exists():
            raise RuntimeError(f"G57 must not create dense compact-2K file: {path}")


def assert_no_validation_internals(repo: Path) -> None:
    for relative in FORBIDDEN_INTERNAL_PATHS:
        if (repo / relative).exists():
            raise RuntimeError(f"G57 separate game repo contains validation internal path: {relative}")
    for relative in ("project.godot", "README.md", "scripts/main.gd", "scripts/g57_integration_runtime.gd"):
        text = (repo / relative).read_text(encoding="utf-8")
        for phrase in FORBIDDEN_INTERNAL_TEXT:
            if phrase in text:
                raise RuntimeError(f"G57 separate game repo contains validation internal text {phrase}: {relative}")


def static_audit() -> dict[str, object]:
    required = {
        "tools/g57_separate_game_repository_integration_quality.py": (
            SUMMARY_MARKER,
            "world-transvoxel-integration-game",
            "assert_no_validation_internals",
            "world_transvoxel_game_world",
        ),
        "addons/world_transvoxel_game_world/wt_game_world_node.gd": (
            "get_game_world_summary",
            "submit_sphere_edit",
        ),
    }
    errors: list[str] = []
    for relative, phrases in required.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing G57 file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{relative} missing phrase: {phrase}")
        if path.suffix in {".py", ".gd"} and len(text.splitlines()) > 460:
            errors.append(f"G57 source file exceeds line limit: {relative}")
    if errors:
        raise RuntimeError("; ".join(errors))
    return {"implementation": "separate_game_repository_integration_quality", "repo": str(DEFAULT_REPO)}


def run_runtime(repo: Path, version: str, engine: Path) -> dict[str, object]:
    reset_runtime_state(repo)
    started_at = time.perf_counter()
    result = subprocess.run(
        [str(engine), "--path", str(repo), "--script", SCRIPT],
        cwd=repo,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=300,
    )
    duration = time.perf_counter() - started_at
    (ARTIFACT_ROOT / f"godot-{version}-g57.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g57.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G57 separate game integration failed on {version}")
    if duration > MAX_RUNTIME_SECONDS:
        raise RuntimeError(f"G57 runtime exceeded {MAX_RUNTIME_SECONDS:.0f}s on {version}: {duration:.3f}s")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    fields = parse_marker(marker_line)
    if fields.get("addon") != ADDON_ID or fields.get("validation_internals") != "0":
        raise RuntimeError(f"G57 addon/internal boundary mismatch: {marker_line}")
    if int(fields.get("player_viewer_updates", "0")) < 2 or int(fields.get("edit_replacements", "0")) <= 0:
        raise RuntimeError(f"G57 integration counters invalid: {marker_line}")
    if int(fields.get("render_resources", "0")) != 25 or int(fields.get("collision_resources", "0")) != 25:
        raise RuntimeError(f"G57 compact resources invalid: {marker_line}")
    assert_no_dense_files(repo)
    assert_no_validation_internals(repo)
    return {"engine": version, "duration_seconds": duration, "marker": marker_line, "fields": fields}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run G57 separate game repository integration validation.")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    parser.add_argument("--skip-build", action="store_true")
    arguments = parser.parse_args()

    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    audit = static_audit()
    build_world_transvoxel(arguments.skip_build)
    repo = arguments.repo.resolve()
    lock = compose_integration_repo(repo)
    reset_runtime_state(repo)
    assert_no_dense_files(repo)
    assert_no_validation_internals(repo)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_project_import(repo, version, engine, ARTIFACT_ROOT)
        results.append(run_runtime(repo, version, engine))
    report_path = ARTIFACT_ROOT / "g57_separate_game_repository_integration_quality_report.json"
    report_path.write_text(
        json.dumps({"repo": str(repo), "lock": lock, "audit": audit, "engines": results}, indent=2) + "\n",
        encoding="utf-8",
    )
    max_duration = max(float(result["duration_seconds"]) for result in results)
    max_player_updates = max(int(dict(result["fields"]).get("player_viewer_updates", 0)) for result in results)
    max_edit_replacements = max(int(dict(result["fields"]).get("edit_replacements", 0)) for result in results)
    print(
        f"{SUMMARY_MARKER} repo={repo.as_posix()} addon={ADDON_ID} engines={len(results)} "
        f"max_engine_seconds={max_duration:.3f} validation_internals=0 "
        f"player_viewer_updates={max_player_updates} edit_replacements={max_edit_replacements} "
        f"render_resources=25 collision_resources=25 dense_world_files=0 "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
