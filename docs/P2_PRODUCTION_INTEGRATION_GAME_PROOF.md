# P2 - Production integration game proof

Status: complete. `WT_VALIDATION_P2_CONTRACT_PASS` and
`WT_VALIDATION_P2_PRODUCTION_INTEGRATION_GAME_SMOKE_PASS` both pass.

P2 proves a normal minimal Godot game repository consumes the production addon
stack as an end-user dependency.

Required production game behavior:

- opens through `project.godot`;
- uses `world_transvoxel`, `world_transvoxel_terrain`, and
  `world_transvoxel_gameworld`;
- has a first-person player, camera, crosshair, terrain edit input, telemetry
  overlay, and profile selector;
- runs both `flat_baseline` and `g19_compact_2k_on_demand`;
- contains no validation-game tests, tools, scenes, or internal scripts;
- one validation command proves launch, input path, traversal, edit commit,
  storage journal creation, cold idle, and generated UID/cache cleanup.

Expected runtime marker:

```text
WT_PRODUCTION_GAME_P2_PASS profile=... addon=world_transvoxel_gameworld launch=project_godot player=1 camera=1 crosshair=1 profile_selector=1 telemetry=1 input_edit=1 traversal=1 edit_committed=1 storage_journal=1 cold_idle=1 render_resources=... collision_resources=... validation_internals=0
```

Expected smoke marker:

```text
WT_VALIDATION_P2_PRODUCTION_INTEGRATION_GAME_SMOKE_PASS repo=... addon=world_transvoxel_gameworld engines=2 profiles=2 validation_internals=0 launch=project_godot input_edit=1 traversal=1 edit_committed=1 storage_journal=1 cold_idle=1 generated_uid_artifacts_removed=... report=artifacts/p2_production_integration_game_quality/p2_production_integration_game_quality_report.json
```

Validator marker:

```text
WT_VALIDATION_P2_CONTRACT_PASS implementation=production_integration_game_proof
```
