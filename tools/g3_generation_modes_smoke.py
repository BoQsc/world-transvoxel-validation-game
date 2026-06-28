#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
import shutil
import struct
import subprocess
import sys
from pathlib import Path

from compose_validation_project import ROOT, REPOSITORY_ROOT, compose
from g0_install_run_smoke import discover_engines, has_godot_error, run_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g3_generation_modes"
SOURCE_ROOT = ARTIFACT_ROOT / "source"
WORLDS_ROOT = ARTIFACT_ROOT / "worlds"
G3_PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g3_generation_modes_smoke.gd"
MARKER = "WT_VALIDATION_G3_GODOT_PASS"
WORLD_TRANSVOXEL = REPOSITORY_ROOT / "world-transvoxel"
ORIGIN = (-2, -2, -2)
DIMENSIONS = (69, 37, 69)
SOURCE_REVISION_BASE = 9300
CHUNK_KEYS = tuple((x, 0, z, 0) for z in range(4) for x in range(4))


def remove_tree(path: Path) -> None:
    if path.exists():
        path.relative_to(ROOT)
        shutil.rmtree(path)


def height(mode: str, x: int, z: int) -> float:
    if mode == "flat_large":
        return 8.0
    centered_x = (x - 31.5) / 31.5
    centered_z = (z - 31.5) / 31.5
    ridge = 4.4 * math.exp(-3.0 * (centered_x * centered_x + centered_z * centered_z))
    waves = 1.3 * math.sin(x * 0.23) + 0.9 * math.cos(z * 0.19)
    return 7.2 + ridge + waves


def write_profile_source(mode: str, material: int) -> tuple[Path, Path, Path]:
    profile_root = SOURCE_ROOT / mode
    profile_root.mkdir(parents=True, exist_ok=True)
    density_path = profile_root / "density.f32"
    material_path = profile_root / "materials.u16"
    key_path = profile_root / "keys.txt"
    densities = bytearray()
    materials = bytearray()
    for z_index in range(DIMENSIONS[2]):
        z = ORIGIN[2] + z_index
        for y_index in range(DIMENSIONS[1]):
            y = ORIGIN[1] + y_index
            for x_index in range(DIMENSIONS[0]):
                x = ORIGIN[0] + x_index
                densities.extend(struct.pack("<f", float(y) - height(mode, x, z)))
                materials.extend(struct.pack("<H", material))
    density_path.write_bytes(densities)
    material_path.write_bytes(materials)
    key_path.write_text(
        "".join(f"{x} {y} {z} {lod}\n" for x, y, z, lod in CHUNK_KEYS),
        encoding="utf-8",
    )
    return density_path, material_path, key_path


def bake_profile(mode: str, material: int, source_revision: int) -> dict[str, object]:
    density, materials, keys = write_profile_source(mode, material)
    output = WORLDS_ROOT / mode
    command = [
        sys.executable,
        str(WORLD_TRANSVOXEL / "tools" / "wt_bake.py"),
        str(density),
        str(keys),
        str(output),
        "--materials",
        str(materials),
        "--origin",
        *(str(value) for value in ORIGIN),
        "--dimensions",
        *(str(value) for value in DIMENSIONS),
        "--spacing",
        "1",
        "--source-revision",
        str(source_revision),
        "--configuration",
        "template_release",
    ]
    result = subprocess.run(command, cwd=WORLD_TRANSVOXEL, check=False, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    world_path = output / "world.wtworld"
    validation = subprocess.run(
        [sys.executable, str(WORLD_TRANSVOXEL / "tools" / "wt_storage.py"), "validate", str(world_path)],
        cwd=WORLD_TRANSVOXEL,
        check=True,
        text=True,
        capture_output=True,
    )
    metadata = json.loads(validation.stdout)
    if metadata.get("pages") != len(CHUNK_KEYS):
        raise RuntimeError(f"{mode} page count mismatch: {metadata}")
    return {"mode": mode, "world": str(world_path), "metadata": metadata}


def generate_worlds() -> list[dict[str, object]]:
    remove_tree(ARTIFACT_ROOT)
    SOURCE_ROOT.mkdir(parents=True, exist_ok=True)
    WORLDS_ROOT.mkdir(parents=True, exist_ok=True)
    results = [
        bake_profile("flat_large", 2, SOURCE_REVISION_BASE + 1),
        bake_profile("mountain_large", 3, SOURCE_REVISION_BASE + 2),
    ]
    (ARTIFACT_ROOT / "g3_generation_modes_bake_report.json").write_text(
        json.dumps({"profiles": results, "chunk_pages_per_profile": len(CHUNK_KEYS)}, indent=2) + "\n",
        encoding="utf-8",
    )
    return results


def copy_worlds_into_project(project: Path) -> None:
    target = project / "build" / "g3-generation-fixtures"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(WORLDS_ROOT, target)


def run_smoke(project: Path, version: str, engine: Path, headless: bool) -> dict[str, object]:
    command = [str(engine)]
    if headless:
        command.append("--headless")
    command.extend(["--path", str(project), "--script", SCRIPT])
    result = subprocess.run(
        command,
        cwd=project,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=180,
    )
    (ARTIFACT_ROOT / f"godot-{version}-g3.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g3.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G3 generation modes smoke failed on {version}")
    copied: dict[str, str] = {}
    for mode in ("flat_large", "mountain_large"):
        capture = project / "artifacts" / "g3_generation_modes" / f"{mode}.png"
        if not capture.is_file():
            raise RuntimeError(f"G3 capture missing: {capture}")
        target = ARTIFACT_ROOT / f"godot-{version}-{mode}.png"
        target.write_bytes(capture.read_bytes())
        copied[mode] = str(target)
    return {
        "engine": version,
        "executable": str(engine),
        "marker": next(line for line in combined.splitlines() if line.startswith(MARKER)),
        "captures": copied,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Bake and validate G3 flat/mountain generation modes.")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=G3_PROJECT)
    parser.add_argument("--windowed", action="store_true")
    arguments = parser.parse_args()

    bake_results = generate_worlds()
    project = arguments.project.resolve()
    lock = compose(project)
    copy_worlds_into_project(project)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_import(project, version, engine)
        results.append(run_smoke(project, version, engine, not arguments.windowed))
    report_path = ARTIFACT_ROOT / "g3_generation_modes_report.json"
    report_path.write_text(
        json.dumps({"project": str(project), "lock": lock, "bake": bake_results, "engines": results}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(
        "WT_VALIDATION_G3_SMOKE_PASS "
        f"profiles=2 engines={len(results)} report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()
