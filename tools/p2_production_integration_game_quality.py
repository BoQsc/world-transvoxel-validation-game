#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time

from compose_validation_project import GAMEWORLD_REPO, REPOSITORY_ROOT, TERRAIN_REPO, WORLD_TRANSVOXEL_REPO, git_output
from g0_install_run_smoke import discover_engines, has_godot_error
from g8_runtime_active_window_smoke import build_world_transvoxel
from p2_production_integration_templates import GITIGNORE, MAIN_SCENE, MAIN_SCRIPT, PLAYER_SCRIPT, PROJECT_GODOT, README


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "artifacts" / "p2_production_integration_game_quality"
DEFAULT_REPO = REPOSITORY_ROOT / "world-transvoxel-integration-game"
MARKER = "WT_PRODUCTION_GAME_P2_PASS"
SUMMARY_MARKER = "WT_VALIDATION_P2_PRODUCTION_INTEGRATION_GAME_SMOKE_PASS"
ADDON_ID = "world_transvoxel_gameworld"
PROFILES = ("flat_baseline", "g19_compact_2k_on_demand")
MAX_RUNTIME_SECONDS = 180.0
FORBIDDEN_PATHS = (
    Path("addons") / "world_transvoxel_game_world",
    Path("tests"),
    Path("tools"),
    Path("scenes") / "validation_playtest.tscn",
)
FORBIDDEN_TEXT = (
    "validation_playtest",
    "validation_profile",
    "res://scripts/validation",
    "world_transvoxel_game_world",
)


def clean_copytree(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns(".git", "__pycache__", ".godot", "artifacts", "build", "*.uid"))


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def ensure_git_repo(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    if not (repo / ".git").exists():
        subprocess.run(["git", "init"], cwd=repo, check=True, text=True, capture_output=True)


def remove_known_content(repo: Path) -> None:
    for relative in (".godot", "addons", "artifacts", "build", "scenes", "scripts"):
        path = repo / relative
        if path.exists():
            shutil.rmtree(path)
    for relative in (".gitignore", "README.md", "project.godot"):
        path = repo / relative
        if path.exists():
            path.unlink()


def compose_integration_repo(repo: Path) -> dict[str, object]:
    ensure_git_repo(repo)
    remove_known_content(repo)
    write_file(repo / ".gitignore", GITIGNORE)
    write_file(repo / "README.md", README)
    write_file(repo / "project.godot", PROJECT_GODOT)
    write_file(repo / "scenes" / "main.tscn", MAIN_SCENE)
    write_file(repo / "scripts" / "main.gd", MAIN_SCRIPT)
    write_file(repo / "scripts" / "wt_production_player.gd", PLAYER_SCRIPT)
    clean_copytree(WORLD_TRANSVOXEL_REPO / "addons" / "world_transvoxel", repo / "addons" / "world_transvoxel")
    clean_copytree(TERRAIN_REPO / "addons" / "world_transvoxel_terrain", repo / "addons" / "world_transvoxel_terrain")
    clean_copytree(GAMEWORLD_REPO / "addons" / ADDON_ID, repo / "addons" / ADDON_ID)
    clean_copytree(WORLD_TRANSVOXEL_REPO / "build" / "production-lifecycle-fixture", repo / "build" / "production-lifecycle-fixture")
    return {
        "repo": str(repo),
        "world-transvoxel": git_output(WORLD_TRANSVOXEL_REPO, "rev-parse", "HEAD"),
        "world-transvoxel-terrain": git_output(TERRAIN_REPO, "rev-parse", "HEAD"),
        "world-transvoxel-gameworld": git_output(GAMEWORLD_REPO, "rev-parse", "HEAD"),
    }


def reset_profile_state(repo: Path, profile: str) -> None:
    root = repo / "build" / "p2-production-game" / profile
    if root.exists():
        shutil.rmtree(root)
    if profile == "flat_baseline":
        for relative in (
            Path("build") / "production-lifecycle-fixture" / "world.wtedit",
            Path("build") / "production-lifecycle-fixture" / "snapshots",
        ):
            path = repo / relative
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()


def assert_no_dense_files(repo: Path, profile: str) -> None:
    root = repo / "build" / "p2-production-game" / profile
    for name in ("world.wtworld", "streaming.wtworld", "procedural.wtseed"):
        if (root / name).exists():
            raise RuntimeError(f"P2 must not create dense/procedural descriptor file: {root / name}")


def assert_no_validation_internals(repo: Path) -> None:
    for relative in FORBIDDEN_PATHS:
        if (repo / relative).exists():
            raise RuntimeError(f"P2 integration repo contains forbidden path: {relative}")
    for relative in ("project.godot", "README.md", "scripts/main.gd", "scripts/wt_production_player.gd"):
        text = (repo / relative).read_text(encoding="utf-8")
        for phrase in FORBIDDEN_TEXT:
            if phrase in text:
                raise RuntimeError(f"P2 integration repo contains forbidden text {phrase}: {relative}")


def remove_generated_uid_artifacts(repo: Path) -> int:
    removed = 0
    for path in repo.rglob("*.uid"):
        if ".git" in path.parts:
            continue
        path.unlink()
        removed += 1
    return removed


def parse_marker(marker_line: str) -> dict[str, str]:
    return dict(token.split("=", 1) for token in marker_line.split()[1:] if "=" in token)


def run_p2_project_import(repo: Path, version: str, engine: Path) -> None:
    result = subprocess.run(
        [str(engine), "--headless", "--path", str(repo), "--import"],
        cwd=repo,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=180,
    )
    combined = result.stdout + result.stderr
    (ARTIFACT_ROOT / f"godot-{version}-import.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-import.stderr.txt").write_text(result.stderr, encoding="utf-8")
    extension_cache = repo / ".godot" / "extension_list.cfg"
    cache_valid = (
        extension_cache.is_file()
        and "res://addons/world_transvoxel/world_transvoxel.gdextension"
        in extension_cache.read_text(encoding="utf-8", errors="replace")
    )
    if has_godot_error(combined) or not cache_valid:
        raise RuntimeError(f"P2 project import failed on {version}: returncode={result.returncode}")


def run_profile(repo: Path, version: str, engine: Path, profile: str) -> dict[str, object]:
    reset_profile_state(repo, profile)
    started_at = time.perf_counter()
    result = subprocess.run(
        [str(engine), "--path", str(repo), "--", "--p2-autonomous", "--p2-profile", profile],
        cwd=repo,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=300,
    )
    duration = time.perf_counter() - started_at
    safe_profile = profile.replace("/", "_")
    (ARTIFACT_ROOT / f"godot-{version}-{safe_profile}.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-{safe_profile}.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"P2 production integration game failed on {version} profile={profile}")
    if duration > MAX_RUNTIME_SECONDS:
        raise RuntimeError(f"P2 runtime exceeded {MAX_RUNTIME_SECONDS:.0f}s on {version} profile={profile}: {duration:.3f}s")
    marker_line = next(line for line in combined.splitlines() if line.startswith(MARKER))
    fields = parse_marker(marker_line)
    required_ones = ("player", "camera", "crosshair", "profile_selector", "telemetry", "input_edit", "traversal", "edit_committed", "storage_journal", "cold_idle")
    if fields.get("profile") != profile or fields.get("addon") != ADDON_ID or fields.get("launch") != "project_godot":
        raise RuntimeError(f"P2 marker identity mismatch: {marker_line}")
    for key in required_ones:
        if fields.get(key) != "1":
            raise RuntimeError(f"P2 marker missing {key}: {marker_line}")
    if fields.get("validation_internals") != "0":
        raise RuntimeError(f"P2 validation internals leaked: {marker_line}")
    expected = 1 if profile == "flat_baseline" else 25
    if int(fields.get("render_resources", "0")) != expected or int(fields.get("collision_resources", "0")) != expected:
        raise RuntimeError(f"P2 resource mismatch: {marker_line}")
    assert_no_dense_files(repo, profile)
    assert_no_validation_internals(repo)
    return {"engine": version, "profile": profile, "duration_seconds": duration, "marker": marker_line, "fields": fields}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run P2 production integration game proof.")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    parser.add_argument("--skip-build", action="store_true")
    arguments = parser.parse_args()

    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    build_world_transvoxel(arguments.skip_build)
    repo = arguments.repo.resolve()
    lock = compose_integration_repo(repo)
    assert_no_validation_internals(repo)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_p2_project_import(repo, version, engine)
        for profile in PROFILES:
            results.append(run_profile(repo, version, engine, profile))
    report_path = ARTIFACT_ROOT / "p2_production_integration_game_quality_report.json"
    report_path.write_text(
        json.dumps({"repo": str(repo), "lock": lock, "profiles": PROFILES, "engines": results}, indent=2) + "\n",
        encoding="utf-8",
    )
    generated_uid_artifacts_removed = remove_generated_uid_artifacts(repo)
    max_duration = max(float(result["duration_seconds"]) for result in results)
    print(
        f"{SUMMARY_MARKER} repo={repo.as_posix()} addon={ADDON_ID} engines={len(engines)} "
        f"profiles={len(PROFILES)} max_engine_seconds={max_duration:.3f} validation_internals=0 "
        f"launch=project_godot input_edit=1 traversal=1 edit_committed=1 storage_journal=1 cold_idle=1 "
        f"generated_uid_artifacts_removed={generated_uid_artifacts_removed} "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
