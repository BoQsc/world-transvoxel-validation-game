# G24 - Autonomous large-terrain acceptance

Status: complete as capped active-window regression evidence when
`WT_VALIDATION_G24_CONTRACT_PASS` and
`WT_VALIDATION_G24_AUTONOMOUS_LARGE_TERRAIN_ACCEPTANCE_SMOKE_PASS` both pass.
G24 is superseded by G25 for full terrain visibility.

G24 no longer replaces the next human-review step. It is retained as an
autonomous regression for compact procedural storage, map-scale movement,
player-driven streaming, and local editable Transvoxel chunks. It does not prove
that the whole 2048 by 2048 terrain is visible.

Required behavior:

- the compact `g19_compact_2k_on_demand` profile represents a 2048 by 2048
  terrain descriptor with 16,384 indexed pages;
- autonomous checks cover map-scale positions including origin edge, interior
  quadrants, center, and far corner;
- every sampled position settles to the expected bounded active window;
- player movement at each sampled position drives terrain viewer updates;
- first-person camera input changes camera rotation;
- left click carves and right click constructs/places through normal input;
- terrain materials are applied before captures;
- captures are written for every sampled region and contain colored terrain;
- active render and collision resources never exceed 25 because this is a capped
  local active-window regression;
- settled runtime reports `render_fading_resources = 0`;
- settled runtime reports `pending_chunk_retirements = 0`;
- no dense near-2K source/world files are reintroduced.

Validation:

```text
python tools/validate_g24_contract.py
python tools/g24_autonomous_large_terrain_acceptance.py --skip-build
```

Expected marker:

```text
WT_VALIDATION_G24_CONTRACT_PASS implementation=autonomous_large_terrain_acceptance
WT_VALIDATION_G24_AUTONOMOUS_LARGE_TERRAIN_ACCEPTANCE_PASS profile=g19_compact_2k_on_demand samples=... pages=16384 map_blocks=2048 max_render_resources=25 max_collision_resources=25 player_stream_updates=... camera_delta=... click_edits=2 captures=... dense_world_files=0
WT_VALIDATION_G24_AUTONOMOUS_LARGE_TERRAIN_ACCEPTANCE_SMOKE_PASS engines=2 max_engine_seconds=... report=artifacts/g24_autonomous_large_terrain_acceptance/g24_autonomous_large_terrain_acceptance_report.json
```

Boundary:

- G24 is no longer the autonomous prerequisite before future human visual
  validation; G25 is required for that.
- G24 proves capped local active-window behavior across the compact 2K descriptor
  but not full-map terrain visibility.
- G24 still does not claim final terrain art, seamless dynamic LOD, GPU/compute
  generation, fluids, biomes, vegetation, buildings, multiplayer, or a separate
  game repository.
