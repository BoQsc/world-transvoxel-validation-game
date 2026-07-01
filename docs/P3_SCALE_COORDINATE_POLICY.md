# P3 - Scale and coordinate policy beyond compact 2K

Status: complete when `WT_VALIDATION_P3_CONTRACT_PASS` and
`WT_VALIDATION_P3_SCALE_COORDINATE_POLICY_PASS` both pass.

P3 closes register gap `P3-SCALE-COORDINATES`.

The standard compact 2K terrain remains the default production baseline. P3
adds the first optional larger-than-2K policy profile without claiming that every
larger world is production-ready.

## Standard scale vocabulary

- `compact_2k`: 2048 by 2048 blocks, 128 by 128 chunks, 16384 pages.
- `large_4k_optional`: 4096 by 4096 blocks, 256 by 256 chunks, 65536 pages.
- `huge_or_planetary`: anything requiring origin shifting, large-world
  coordinates, spherical topology, or non-flat gravity.

## Coordinate policy

- 1 block is treated as 1 meter in the terrain profile vocabulary.
- `compact_2k` and `large_4k_optional` use normal single-precision local terrain
  coordinates.
- origin shifting is not required for `large_4k_optional`.
- origin shifting must be researched before advertising worlds beyond 32768
  blocks in either horizontal axis.
- Godot large-world coordinates are reserved for space/planetary-scale work, not
  required for the compact 2K or optional 4K terrain policy.

## Optional 4K budget proof

The P3 proof validates:

- `large_4k_optional` is larger than compact 2K;
- the optional profile has 65536 logical pages but only 169 active resources for
  radius 6 streaming;
- active resources stay inside the 256 active-resource capacity;
- the optional profile remains on-demand and does not create dense world files;
- file, load, memory, and visible-presentation budgets are explicit.

Expected marker:

```text
WT_VALIDATION_P3_SCALE_COORDINATE_POLICY_PASS profile=large_4k_optional map_blocks=4096 chunk_grid=256x256 pages=65536 active_radius=6 active_resources=169 active_capacity=256 max_file_bytes=1024 total_bytes=1024 load_budget_seconds=30 memory_budget_mb=64 full_visual_blocks=4096x4096 origin_policy=single_precision_no_shift next=P4_production_rendering_materials_object_density
```

Validator marker:

```text
WT_VALIDATION_P3_CONTRACT_PASS implementation=scale_coordinate_policy
```
