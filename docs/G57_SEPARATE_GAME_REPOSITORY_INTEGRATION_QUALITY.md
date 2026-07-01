# G57 - Separate game repository integration quality

Status: complete when `WT_VALIDATION_G57_CONTRACT_PASS` and
`WT_VALIDATION_G57_SEPARATE_GAME_REPOSITORY_SMOKE_PASS` both pass.

G57 proves the addon stack from outside this validation repository. The separate
repository is a minimal integration proof, not the final game.

The separate repository path is:

```text
C:\Users\Windows10_new\Documents\github_repositories\world-transvoxel-integration-game
```

The gate verifies:

- the sibling repository exists and is a Git repository;
- it imports `world_transvoxel`, `world_transvoxel_terrain`, and
  `world_transvoxel_game_world`;
- it does not copy validation-game scenes, scripts, tests, or tools;
- it runs a compact 2K deterministic profile using its own integration script;
- it attaches a local player stub, drives player-based viewer updates, and
  submits a terrain edit through the game-world addon;
- render/collision resources settle at 25;
- dense normal terrain files remain absent;
- both supported Godot engines pass.

Expected external runtime marker:

```text
WT_INTEGRATION_GAME_G57_PASS repo=world-transvoxel-integration-game addon=world_transvoxel_game_world api_version=1 validation_internals=0 player_viewer_updates=... edit_replacements=... render_resources=25 collision_resources=25 active_records=25 dense_world_files=0
```

Expected validation smoke marker:

```text
WT_VALIDATION_G57_SEPARATE_GAME_REPOSITORY_SMOKE_PASS repo=... addon=world_transvoxel_game_world engines=2 max_engine_seconds=... validation_internals=0 player_viewer_updates=... edit_replacements=... render_resources=25 collision_resources=25 dense_world_files=0 report=artifacts/g57_separate_game_repository_integration_quality/g57_separate_game_repository_integration_quality_report.json
```

Contract marker:

```text
WT_VALIDATION_G57_CONTRACT_PASS implementation=separate_game_repository_integration_quality
```
