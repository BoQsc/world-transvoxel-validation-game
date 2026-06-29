#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import shutil
import struct
import subprocess
import sys

from compose_validation_project import ROOT, REPOSITORY_ROOT, compose
from generated_fixture_vertical_coverage import (
    assert_surface_within_active_vertical_chunk,
    surface_coverage,
)
from g0_install_run_smoke import discover_engines, has_godot_error, run_import
from g8_runtime_active_window_smoke import build_world_transvoxel


ARTIFACT_ROOT = ROOT / "artifacts" / "g11_generated_16x16_playable_streaming"
SOURCE_ROOT = ARTIFACT_ROOT / "source"
WORLDS_ROOT = ARTIFACT_ROOT / "worlds"
G11_PROJECT = ARTIFACT_ROOT / "project"
PROFILE_ID = "g11_generated_16x16"
WORLD_OUTPUT = WORLDS_ROOT / PROFILE_ID
WORLD_MANIFEST = WORLD_OUTPUT / "world.wtworld"
PROJECT_WORLD_ROOT = Path("build") / "g11-generated-fixture" / PROFILE_ID
SCRIPT = "res://tests/g11_generated_16x16_playable_streaming_smoke.gd"
MARKER = "WT_VALIDATION_G11_GENERATED_16X16_PLAYABLE_STREAMING_PASS"
WORLD_TRANSVOXEL = REPOSITORY_ROOT / "world-transvoxel"
ORIGIN = (-2, -4, -2)
DIMENSIONS = (261, 57, 261)
SOURCE_REVISION = 111600
CHUNK_KEYS = tuple((x, 0, z, 0) for z in range(16) for x in range(16))


def remove_tree(path: Path) -> None:
    if path.exists():
        path.relative_to(ROOT)
        shutil.rmtree(path)


def height(x: int, z: int) -> float:
    centered_x = (x - 127.5) / 127.5
    centered_z = (z - 127.5) / 127.5
    ridge = 4.8 * math.exp(-3.2 * (centered_x * centered_x + centered_z * centered_z))
    east_west = 1.2 * math.sin(x * 0.105)
    north_south = 0.9 * math.cos(z * 0.088)
    diagonal = 0.7 * math.sin((x + z) * 0.045)
    return 7.2 + ridge + east_west + north_south + diagonal


def material_id(x: int, z: int, surface_height: float) -> int:
    if surface_height < 7.6:
        return 2
    if (x // 32 + z // 32) % 3 == 0:
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
    SOURCE_ROOT.mkdir(parents=True, exist_ok=True)
    density_path = SOURCE_ROOT / "density.f32"
    material_path = SOURCE_ROOT / "materials.u16"
    key_path = SOURCE_ROOT / "keys.txt"
    densities = bytearray()
    materials = bytearray()
    for z_index in range(DIMENSIONS[2]):
        z = ORIGIN[2] + z_index
        for y_index in range(DIMENSIONS[1]):
            y = ORIGIN[1] + y_index
            for x_index in range(DIMENSIONS[0]):
                x = ORIGIN[0] + x_index
                surface = height(x, z)
                densities.extend(struct.pack("<f", float(y) - surface))
                materials.extend(struct.pack("<H", material_id(x, z, surface)))
    density_path.write_bytes(densities)
    material_path.write_bytes(materials)
    key_path.write_text(
        "".join(f"{x} {y} {z} {lod}\n" for x, y, z, lod in CHUNK_KEYS),
        encoding="utf-8",
    )
    return density_path, material_path, key_path


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
        timeout=900,
    )
    (ARTIFACT_ROOT / "fixture-bake.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / "fixture-bake.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or not WORLD_MANIFEST.is_file():
        raise RuntimeError("G11 generated 16x16 fixture bake failed")
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
        timeout=120,
    )
    metadata = json.loads(result.stdout)
    if metadata.get("pages") != len(CHUNK_KEYS):
        raise RuntimeError(f"G11 generated 16x16 page count mismatch: {metadata}")
    if metadata.get("source_revision") != SOURCE_REVISION:
        raise RuntimeError(f"G11 generated 16x16 source revision mismatch: {metadata}")
    return {
        "reused": reused,
        "profile": PROFILE_ID,
        "world": str(WORLD_MANIFEST),
        "metadata": metadata,
        "vertical_coverage": vertical_coverage(),
        "chunk_pages": len(CHUNK_KEYS),
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
    try:
        result = subprocess.run(
            command,
            cwd=project,
            check=False,
            text=True,
            capture_output=True,
            errors="replace",
            timeout=420,
        )
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout or ""
        stderr = error.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        (ARTIFACT_ROOT / f"godot-{version}-g11.timeout.stdout.txt").write_text(stdout, encoding="utf-8")
        (ARTIFACT_ROOT / f"godot-{version}-g11.timeout.stderr.txt").write_text(stderr, encoding="utf-8")
        print(stdout + stderr, end="" if (stdout + stderr).endswith("\n") else "\n")
        raise RuntimeError(f"G11 generated 16x16 playable streaming smoke timed out on {version}") from error
    (ARTIFACT_ROOT / f"godot-{version}-g11.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g11.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G11 generated 16x16 playable streaming smoke failed on {version}")
    return {
        "engine": version,
        "executable": str(engine),
        "marker": next(line for line in combined.splitlines() if line.startswith(MARKER)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bake and run the G11 generated 16x16 playable streaming validation smoke."
    )
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=G11_PROJECT)
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
    report_path = ARTIFACT_ROOT / "g11_generated_16x16_playable_streaming_report.json"
    report_path.write_text(
        json.dumps(
            {
                "project": str(project),
                "lock": lock,
                "fixture": fixture,
                "engines": results,
                "implementation": "generated_16x16_playable_streaming",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        "WT_VALIDATION_G11_GENERATED_16X16_PLAYABLE_STREAMING_SMOKE_PASS "
        f"engines={len(results)} report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
