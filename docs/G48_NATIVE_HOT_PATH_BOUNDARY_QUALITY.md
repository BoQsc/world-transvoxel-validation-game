# G48 - Native hot-path boundary quality

Status: complete when `WT_VALIDATION_G48_CONTRACT_PASS` and
`WT_VALIDATION_G48_NATIVE_HOT_PATH_BOUNDARY_SMOKE_PASS` both pass.

G48 locks the current implementation boundary so the validation game does not
quietly move performance-sensitive terrain work into GDScript.

## Required evidence

- `WtTerrainWorld.get_hot_path_boundary_summary()` exists in
  `world-transvoxel-terrain`;
- the summary identifies generation, meshing, streaming, edit application, and
  storage as native/backend-owned hot paths;
- normal validation-game runtime scripts do not call backend internals directly;
- normal runtime files do not contain GDScript density-volume loops,
  mesh-building loops, page-generation loops, source-file streaming loops, or
  image/pixel terrain loops;
- the compact 2K validation scene starts, streams, commits one public edit, and
  keeps the standard 25-resource local detail window.

## Commands

```console
python tools/validate_g48_contract.py
python tools/g48_native_hot_path_boundary_quality.py
```

## Expected markers

```text
WT_VALIDATION_G48_CONTRACT_PASS implementation=native_hot_path_boundary_quality
WT_VALIDATION_G48_NATIVE_HOT_PATH_BOUNDARY_PASS profile=g19_compact_2k_on_demand hot_paths=5 native_owned=5 gdscript_hot_loops=0 edit_committed=1 max_render_resources=25 max_collision_resources=25 max_active_records=25 dense_world_files=0
WT_VALIDATION_G48_NATIVE_HOT_PATH_BOUNDARY_SMOKE_PASS profile=g19_compact_2k_on_demand engines=... hot_paths=5 native_owned=5 gdscript_hot_loops=0 quality_track=runtime_terrain dense_world_files=0 report=artifacts/g48_native_hot_path_boundary_quality/g48_native_hot_path_boundary_quality_report.json
```

## Boundary

G48 proves the current compact CPU/native validation path has a safe hot-path
boundary. It does not claim final debug telemetry UI, final terrain profiles,
material texture quality, underground variation, large-world streaming radius,
LOD seam quality, map-generator budget quality, water, vegetation, buildings,
multiplayer, compute acceleration, or separate game integration.
