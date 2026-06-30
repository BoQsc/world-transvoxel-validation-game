# G26 - Full terrain playable experience

Status: complete when `WT_VALIDATION_G26_CONTRACT_PASS` and
`WT_VALIDATION_G26_FULL_TERRAIN_PLAYABLE_EXPERIENCE_SMOKE_PASS` both pass.

G26 moves beyond G25's overhead diagnostic proof. The gate verifies the
first-person full-terrain playable experience: full terrain remains visible from
player-eye views at map-scale positions, the local native Transvoxel detail
window follows scripted player movement, and terrain editing still commits.

Exit:

- No human validation is requested until this gate passes;
- human input is disabled for automation;
- player-driven viewer updates remain active even when human input is disabled;
- `g19_compact_2k_on_demand` starts with full-map visual coverage and local
  native Transvoxel detail;
- first-person eye-height captures are written at origin/center/far-map
  positions;
- every sampled player position settles to the expected local detail window;
- active render/collision resources stay capped to the local detail budget;
- a terrain edit still commits through the normal interactor;
- dense near-2K source/world files are not reintroduced.

Commands:

```console
python tools/validate_g26_contract.py
python tools/g26_full_terrain_playable_experience.py --skip-build
```

Expected markers:

```text
WT_VALIDATION_G26_CONTRACT_PASS implementation=full_terrain_playable_experience
WT_VALIDATION_G26_FULL_TERRAIN_PLAYABLE_EXPERIENCE_PASS profile=g19_compact_2k_on_demand pages=16384 map_blocks=2048 captures=3 player_stream_updates=... max_render_resources=25 max_collision_resources=25 full_visual_visible=true dense_world_files=0
WT_VALIDATION_G26_FULL_TERRAIN_PLAYABLE_EXPERIENCE_SMOKE_PASS engines=2 max_engine_seconds=... report=artifacts/g26_full_terrain_playable_experience/g26_full_terrain_playable_experience_report.json
```

Boundary:

- G26 is still not final terrain art, seamless dynamic LOD approval, GPU/compute
  generation, water, biomes, vegetation, buildings, multiplayer, or separate game
  repository readiness.
- G26 is the first gate where the large terrain is checked from the actual
  first-person playable experience instead of only an overhead diagnostic view.
