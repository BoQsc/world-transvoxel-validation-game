# G56 - Game-world addon prototype quality

Status: complete when `WT_VALIDATION_G56_CONTRACT_PASS` and
`WT_VALIDATION_G56_GAME_WORLD_ADDON_PROTOTYPE_SMOKE_PASS` both pass.

G56 proves the future game-world addon boundary as a validation-owned prototype.
It does not finalize the addon name or claim separate game repository adoption;
that is G57.

The prototype lives at:

```text
addons/world_transvoxel_game_world
```

The gate verifies:

- a game-world addon plugin is copied into generated validation projects;
- a standard world node configures terrain generation and storage profiles;
- terrain setup goes through `world-transvoxel-terrain`;
- an optional player node can be attached with human input disabled for
  automation;
- player-driven viewer updates work through the game-world node;
- a terrain sphere edit can be submitted through the game-world node;
- the compact 2K runtime remains settled at 25 render and collision resources;
- dense normal compact-2K terrain files remain absent.

Expected runtime marker:

```text
WT_VALIDATION_G56_GAME_WORLD_ADDON_PROTOTYPE_PASS addon=world_transvoxel_game_world api_version=1 standard_world_node=1 terrain_node_ready=1 player_attached=1 player_viewer_updates=... edit_replacements=... render_resources=25 collision_resources=25 active_records=25 dense_world_files=0
```

Expected smoke marker:

```text
WT_VALIDATION_G56_GAME_WORLD_ADDON_PROTOTYPE_SMOKE_PASS addon=world_transvoxel_game_world api_version=1 engines=2 max_engine_seconds=... player_viewer_updates=... edit_replacements=... render_resources=25 collision_resources=25 dense_world_files=0 report=artifacts/g56_game_world_addon_prototype_quality/g56_game_world_addon_prototype_quality_report.json
```

Contract marker:

```text
WT_VALIDATION_G56_CONTRACT_PASS implementation=game_world_addon_prototype_quality
```
