# G24 - Autonomous large-terrain acceptance

Status: complete when `WT_VALIDATION_G24_CONTRACT_PASS` and
`WT_VALIDATION_G24_AUTONOMOUS_LARGE_TERRAIN_ACCEPTANCE_SMOKE_PASS` both pass.

G24 replaces the next human-review step with an autonomous large-terrain gate.
No human validation is requested until this gate proves the compact 2K terrain
behaves as expected inside the current project boundary.

Required behavior:

- the compact `g19_compact_2k_on_demand` profile represents a 2048 by 2048
  block terrain with 16,384 indexed pages;
- autonomous checks cover map-scale positions including origin edge, interior
  quadrants, center, and far corner;
- every sampled position settles to the expected bounded active window;
- player movement at each sampled position drives terrain viewer updates;
- first-person camera input changes camera rotation;
- left click carves and right click constructs/places through normal input;
- terrain materials are applied before captures;
- captures are written for every sampled region and contain colored terrain;
- active render and collision resources never exceed 25;
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

- G24 is the autonomous prerequisite before any future human visual validation.
- G24 proves the current compact validation-game terrain is large enough,
  bounded, playable, editable, materialized, and captured under automated
  checks.
- G24 still does not claim final terrain art, seamless dynamic LOD, GPU/compute
  generation, fluids, biomes, vegetation, buildings, multiplayer, or a separate
  game repository.
