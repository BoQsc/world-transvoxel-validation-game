#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

from compose_validation_project import ROOT, REPOSITORY_ROOT, compose
from generated_fixture_source_writer import write_streamed_height_source
from generated_fixture_vertical_coverage import (
    assert_surface_within_active_vertical_chunk,
    surface_coverage,
)
from g0_install_run_smoke import discover_engines, has_godot_error, run_import
from g8_runtime_active_window_smoke import build_world_transvoxel


ARTIFACT_ROOT = ROOT / "artifacts" / "g14_generated_64x64_playable_streaming"
SOURCE_ROOT = ARTIFACT_ROOT / "source"
WORLDS_ROOT = ARTIFACT_ROOT / "worlds"
G14_PROJECT = ARTIFACT_ROOT / "project"
PROFILE_ID = "g14_generated_64x64"
WORLD_OUTPUT = WORLDS_ROOT / PROFILE_ID
WORLD_MANIFEST = WORLD_OUTPUT / "world.wtworld"
PROJECT_WORLD_ROOT = Path("build") / "g14-generated-fixture" / PROFILE_ID
SCRIPT = "res://tests/g14_generated_64x64_playable_streaming_smoke.gd"
MARKER = "WT_VALIDATION_G14_GENERATED_64X64_PLAYABLE_STREAMING_PASS"
WORLD_TRANSVOXEL = REPOSITORY_ROOT / "world-transvoxel"
ORIGIN = (-2, -4, -2)
DIMENSIONS = (1029, 65, 1029)
SOURCE_REVISION = 146400
CHUNK_KEYS = tuple((x, 0, z, 0) for z in range(64) for x in range(64))


def remove_tree(path: Path) -> None:
    if path.exists():
        path.relative_to(ROOT)
        shutil.rmtree(path)


def height(x: int, z: int) -> float:
    centered_x = (x - 511.5) / 511.5
    centered_z = (z - 511.5) / 511.5
    ridge = 3.4 * math.exp(-3.0 * (centered_x * centered_x + centered_z * centered_z))
    long_wave = 0.85 * math.sin(x * 0.031) + 0.65 * math.cos(z * 0.027)
    diagonal = 0.45 * math.sin((x + z) * 0.014)
    local = 0.30 * math.cos((x - z) * 0.039)
    return 5.7 + ridge + long_wave + diagonal + local


def material_id(x: int, z: int, surface_height: float) -> int:
    if surface_height < 7.6:
        return 2
    if surface_height > 11.0:
        return 5
    if (x // 64 + z // 64) % 3 == 0:
        return 4
    return 3


def vertical_coverage() -> dict[str, float | str]:
    return assert_surface_within_active_vertical_chunk(
        surface_coverage(
            label=PROFILE_ID,
            height_function=height,
            origin=ORIGIN,
            dimensions=DIMENSIONS,
        )
    )


def write_source() -> tuple[Path, Path, Path]:
    return write_streamed_height_source(
        source_root=SOURCE_ROOT,
        origin=ORIGIN,
        dimensions=DIMENSIONS,
        chunk_keys=CHUNK_KEYS,
        height_function=height,
        material_function=material_id,
    )


def bake_fixture(reuse_fixture: bool) -> dict[str, object]:
    if reuse_fixture and WORLD_MANIFEST.is_file():
        return validate_fixture(reused=True)
    remove_tree(SOURCE_ROOT)
    remove_tree(WORLD_OUTPUT)
    vertical_coverage()
    density, materials, keys = write_source()
    command = [
        sys.executable,
        str(WORLD_TRANSVOXEL / "tools" / "wt_bake.py"),
        str(density),
        str(keys),
        str(WORLD_OUTPUT),
        "--materials",
        str(materials),
        "--origin",
        *(str(value) for value in ORIGIN),
        "--dimensions",
        *(str(value) for value in DIMENSIONS),
        "--spacing",
        "1",
        "--source-revision",
        str(SOURCE_REVISION),
        "--configuration",
        "template_release",
    ]
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        command,
        cwd=WORLD_TRANSVOXEL,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=2400,
    )
    (ARTIFACT_ROOT / "fixture-bake.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / "fixture-bake.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or not WORLD_MANIFEST.is_file():
        raise RuntimeError("G14 generated 64x64 fixture bake failed")
    return validate_fixture(reused=False)


def validate_fixture(reused: bool) -> dict[str, object]:
    result = subprocess.run(
        [
            sys.executable,
            str(WORLD_TRANSVOXEL / "tools" / "wt_storage.py"),
            "validate",
            str(WORLD_MANIFEST),
        ],
        cwd=WORLD_TRANSVOXEL,
        check=True,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=300,
    )
    metadata = json.loads(result.stdout)
    if metadata.get("pages") != len(CHUNK_KEYS):
        raise RuntimeError(f"G14 generated 64x64 page count mismatch: {metadata}")
    if metadata.get("source_revision") != SOURCE_REVISION:
        raise RuntimeError(f"G14 generated 64x64 source revision mismatch: {metadata}")
    return {
        "reused": reused,
        "profile": PROFILE_ID,
        "world": str(WORLD_MANIFEST),
        "metadata": metadata,
        "vertical_coverage": vertical_coverage(),
        "chunk_pages": len(CHUNK_KEYS),
        "source_writer": "streamed_height_source",
    }


def copy_fixture_into_project(project: Path) -> None:
    target = project / PROJECT_WORLD_ROOT
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(WORLD_OUTPUT, target)


def run_smoke(project: Path, version: str, engine: Path, headless: bool) -> dict[str, object]:
    command = [str(engine)]
    if headless:
        command.append("--headless")
    command.extend(["--path", str(project), "--script", SCRIPT])
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        command,
        cwd=project,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=900,
    )
    (ARTIFACT_ROOT / f"godot-{version}-g14.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g14.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G14 generated 64x64 playable streaming smoke failed on {version}")
    return {
        "engine": version,
        "executable": str(engine),
        "marker": next(line for line in combined.splitlines() if line.startswith(MARKER)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bake and run the G14 generated 64x64 playable streaming validation smoke."
    )
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=G14_PROJECT)
    parser.add_argument("--windowed", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--reuse-fixture", action="store_true")
    arguments = parser.parse_args()

    build_world_transvoxel(arguments.skip_build)
    fixture = bake_fixture(arguments.reuse_fixture)
    project = arguments.project.resolve()
    lock = compose(project)
    copy_fixture_into_project(project)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_import(project, version, engine)
        results.append(run_smoke(project, version, engine, not arguments.windowed))
    report_path = ARTIFACT_ROOT / "g14_generated_64x64_playable_streaming_report.json"
    report_path.write_text(
        json.dumps(
            {
                "project": str(project),
                "lock": lock,
                "fixture": fixture,
                "engines": results,
                "implementation": "generated_64x64_playable_streaming",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        "WT_VALIDATION_G14_GENERATED_64X64_PLAYABLE_STREAMING_SMOKE_PASS "
        f"engines={len(results)} report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
