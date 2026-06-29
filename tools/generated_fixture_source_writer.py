#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import struct
from typing import Callable, Iterable


def write_streamed_height_source(
    *,
    source_root: Path,
    origin: tuple[int, int, int],
    dimensions: tuple[int, int, int],
    chunk_keys: Iterable[tuple[int, int, int, int]],
    height_function: Callable[[int, int], float],
    material_function: Callable[[int, int, float], int],
) -> tuple[Path, Path, Path]:
    source_root.mkdir(parents=True, exist_ok=True)
    density_path = source_root / "density.f32"
    material_path = source_root / "materials.u16"
    key_path = source_root / "keys.txt"
    min_x = origin[0]
    min_y = origin[1]
    min_z = origin[2]
    size_x = dimensions[0]
    size_y = dimensions[1]
    size_z = dimensions[2]
    with density_path.open("wb") as density_file, material_path.open("wb") as material_file:
        for z_index in range(size_z):
            z = min_z + z_index
            surfaces = [float(height_function(min_x + x_index, z)) for x_index in range(size_x)]
            material_row = bytearray()
            for x_index, surface in enumerate(surfaces):
                material_row.extend(struct.pack("<H", int(material_function(min_x + x_index, z, surface))))
            for y_index in range(size_y):
                y = min_y + y_index
                density_row = bytearray()
                for surface in surfaces:
                    density_row.extend(struct.pack("<f", float(y) - surface))
                density_file.write(density_row)
                material_file.write(material_row)
    key_path.write_text(
        "".join(f"{x} {y} {z} {lod}\n" for x, y, z, lod in chunk_keys),
        encoding="utf-8",
    )
    return density_path, material_path, key_path
