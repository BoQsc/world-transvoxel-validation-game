# P1 - Gameworld addon extraction and production boundary

Status: complete. `WT_VALIDATION_P1_CONTRACT_PASS` and
`WT_VALIDATION_P1_GAMEWORLD_ADDON_EXTRACTION_SMOKE_PASS` both pass.

P1 turns the validation-owned `world_transvoxel_game_world` prototype into the
real sibling `world-transvoxel-gameworld` repository with addon id
`world_transvoxel_gameworld`.

The old `world_transvoxel_game_world` addon id remains historical G56/G57
evidence only. New production integration uses `world_transvoxel_gameworld`.

Expected runtime marker:

```text
WT_VALIDATION_P1_GAMEWORLD_ADDON_EXTRACTION_PASS addon=world_transvoxel_gameworld api_version=1 standard_world_node=1 terrain_node_ready=1 player_attached=1 player_viewer_updates=... edit_replacements=... render_resources=25 collision_resources=25 validation_internals=0 dense_world_files=0
```

Expected smoke marker:

```text
WT_VALIDATION_P1_GAMEWORLD_ADDON_EXTRACTION_SMOKE_PASS addon=world_transvoxel_gameworld api_version=1 engines=2 validation_internals=0 player_viewer_updates=... edit_replacements=... render_resources=25 collision_resources=25 dense_world_files=0 report=artifacts/p1_gameworld_addon_extraction_quality/p1_gameworld_addon_extraction_quality_report.json
```

Validator marker:

```text
WT_VALIDATION_P1_CONTRACT_PASS implementation=gameworld_addon_extraction_quality
```
