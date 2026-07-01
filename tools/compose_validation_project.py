#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ROOT.parent
WORLD_TRANSVOXEL_REPO = REPOSITORY_ROOT / "world-transvoxel"
TERRAIN_REPO = REPOSITORY_ROOT / "world-transvoxel-terrain"
GAMEWORLD_REPO = REPOSITORY_ROOT / "world-transvoxel-gameworld"
DEFAULT_OUTPUT = ROOT / "artifacts" / "validation_project"

PROJECT_ITEMS = (
    "addons",
    "scenes",
    "scripts",
    "tests",
)


def git_output(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def clean_copytree(source: Path, target: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(source)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".godot", "artifacts"),
    )


def copy_project_item(relative: str, output: Path) -> None:
    source = ROOT / relative
    target = output / relative
    if source.is_dir():
        clean_copytree(source, target)
    elif source.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    else:
        raise FileNotFoundError(source)


def compose(output: Path) -> dict[str, object]:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    for relative in PROJECT_ITEMS:
        copy_project_item(relative, output)
    write_generated_project_file(output)

    clean_copytree(
        WORLD_TRANSVOXEL_REPO / "addons" / "world_transvoxel",
        output / "addons" / "world_transvoxel",
    )
    clean_copytree(
        TERRAIN_REPO / "addons" / "world_transvoxel_terrain",
        output / "addons" / "world_transvoxel_terrain",
    )
    clean_copytree(
        WORLD_TRANSVOXEL_REPO / "build" / "production-lifecycle-fixture",
        output / "build" / "production-lifecycle-fixture",
    )

    lock = {
        "project": "world-transvoxel-validation-game",
        "output": str(output),
        "sources": {
            "world-transvoxel": {
                "path": str(WORLD_TRANSVOXEL_REPO),
                "commit": git_output(WORLD_TRANSVOXEL_REPO, "rev-parse", "HEAD"),
                "remote": git_output(WORLD_TRANSVOXEL_REPO, "remote", "get-url", "origin"),
            },
            "world-transvoxel-terrain": {
                "path": str(TERRAIN_REPO),
                "commit": git_output(TERRAIN_REPO, "rev-parse", "HEAD"),
                "remote": git_output(TERRAIN_REPO, "remote", "get-url", "origin"),
            },
        },
    }
    (output / "VALIDATION_LOCK.json").write_text(
        json.dumps(lock, indent=2) + "\n", encoding="utf-8"
    )
    return lock


def write_generated_project_file(output: Path) -> None:
    (output / "project.godot").write_text(
        "\n".join(
            [
                "config_version=5",
                "",
                "[application]",
                "",
                'config/name="World Transvoxel Validation Game - Generated"',
                'run/main_scene="res://scenes/validation_playtest.tscn"',
                'config/features=PackedStringArray("4.6", "Forward Plus")',
                "",
                "[editor_plugins]",
                "",
                'enabled=PackedStringArray("res://addons/world_transvoxel/plugin.cfg", "res://addons/world_transvoxel_terrain/plugin.cfg", "res://addons/world_transvoxel_game_world/plugin.cfg")',
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compose the ignored Godot validation project from sibling addon repos."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    lock = compose(arguments.output.resolve())
    print(
        "WT_VALIDATION_PROJECT_COMPOSED "
        f"output={Path(lock['output']).as_posix()} "
        f"world_transvoxel={lock['sources']['world-transvoxel']['commit'][:7]} "
        f"terrain={lock['sources']['world-transvoxel-terrain']['commit'][:7]}"
    )


if __name__ == "__main__":
    main()
