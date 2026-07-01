# G55 - Map generator budget quality

Status: complete when `WT_VALIDATION_G55_CONTRACT_PASS` and
`WT_VALIDATION_G55_MAP_GENERATOR_BUDGET_SMOKE_PASS` both pass.

G55 proves that the normal compact 2K procedural generator path remains
practical for games. It is not a biome, cave, ore, water, or vegetation system;
it is the budget gate for the current deterministic map generator path.

The gate verifies:

- `g19_compact_2k_on_demand` and `g50_seeded_procedural_2k` load through the
  normal generated Godot validation project;
- both profiles use the `deterministic_reference` generator mode;
- both profiles expose the expected 2048 by 2048 block map through 16384 pages;
- both profiles reach playable readiness under the 30 seconds load-to-play
  ceiling;
- render and collision resources settle to the expected compact active window;
- queued render/collision, pending retirements, and render fading are zero after
  settling;
- no normal generated terrain file exceeds the 100 MiB hard per-file ceiling;
- current target files remain under the 50 MiB target per-file ceiling;
- generated profile directories remain under the 100 MiB total ceiling;
- dense compact-2K source/world files are still not required.

Expected runtime marker:

```text
WT_VALIDATION_G55_MAP_GENERATOR_BUDGET_PASS profiles=2 map_blocks=2048 pages=16384 max_load_ms=... max_render_resources=25 max_collision_resources=25 generator_modes=deterministic_reference,deterministic_reference seeds=19019,50050 dense_world_files=0
```

Expected smoke marker:

```text
WT_VALIDATION_G55_MAP_GENERATOR_BUDGET_SMOKE_PASS profiles=2 engines=... max_engine_seconds=... max_file_bytes=... max_total_bytes=... target_file_bytes=52428800 hard_file_bytes=104857600 dense_world_files=0 report=artifacts/g55_map_generator_budget_quality/g55_map_generator_budget_quality_report.json
```

Contract marker:

```text
WT_VALIDATION_G55_CONTRACT_PASS implementation=map_generator_budget_quality
```
