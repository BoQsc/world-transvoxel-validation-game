# Terrain adoption examples

Status: G58 documentation examples source.

These examples describe the current Terrain 1.0 validation stack after G57.
They are intentionally standard-first: use the addon boundary, keep generated
runtime data ignored, and avoid copying validation-game internals into games.

## Installation

A game project should enable the three-addon stack:

```ini
[editor_plugins]

enabled=PackedStringArray(
  "res://addons/world_transvoxel/plugin.cfg",
  "res://addons/world_transvoxel_terrain/plugin.cfg",
  "res://addons/world_transvoxel_game_world/plugin.cfg"
)
```

The current external proof repository is:

```text
C:\Users\Windows10_new\Documents\github_repositories\world-transvoxel-integration-game
```

## Profile setup

Create terrain generation and storage profiles in game code, then pass them to
the game-world addon node. The public resource classes are
`WtTerrainGenerationProfile` and `WtTerrainStorageProfile`:

```gdscript
const GameWorldNode := preload("res://addons/world_transvoxel_game_world/wt_game_world_node.gd")
const GenerationProfile := preload("res://addons/world_transvoxel_terrain/generation/wt_terrain_generation_profile.gd")
const StorageProfile := preload("res://addons/world_transvoxel_terrain/storage/wt_terrain_storage_profile.gd")

var generation = GenerationProfile.new()
generation.source_mode = GenerationProfile.SourceMode.DETERMINISTIC_REFERENCE
generation.world_chunk_count_x = 128
generation.world_chunk_count_z = 128
generation.seed = 57057

var storage = StorageProfile.new()
storage.world_manifest_path = "res://build/my-game/my_profile/procedural.wtseed"
storage.object_root_path = "res://build/my-game/my_profile"
storage.edit_journal_path = "res://build/my-game/my_profile/world.wtedit"

var game_world = GameWorldNode.new()
game_world.configure_game_world(
  &"my_profile",
  generation,
  storage,
  [Vector3(1032.0, 8.0, 1032.0)],
  2,
  25,
  Vector3(1032.0, 24.0, 1032.0)
)
```

## Terrain editing

Submit edits through the game-world or terrain addon API, not through copied
validation-game interactors:

```gdscript
var accepted := game_world.submit_sphere_edit(
  &"carve",
  Vector3(1032.0, 8.0, 1032.0),
  1.8,
  -1,
  1.0
)
if not accepted:
  push_error(str(game_world.get_last_edit_summary()))
```

The current standard brush policy remains a sphere brush. Other shapes are
future optional policy, not the default Terrain 1.0 contract.

## Storage

Runtime-generated terrain data should be stored under ignored game-local paths:

```text
res://build/<game>/<profile>/
```

Commit addon source and game code. Do not commit `.godot/`, generated `build/`
terrain data, or generated `*.gd.uid` sidecars unless a repository has an
explicit reason to track them.

## Telemetry

Use the game-world summary first:

```gdscript
var summary := game_world.get_game_world_summary()
print(summary.render_resources)
print(summary.collision_resources)
print(summary.player_viewer_updates)
print(summary.edit_replacements)
```

The expected compact 2K settled state is 25 render resources, 25 collision
resources, no queued resources, no pending retirements, and no render fading.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| GDExtension dynamic library missing | Rebuild or recopy `addons/world_transvoxel/bin` and `world_transvoxel.gdextension`. |
| Terrain does not appear | Verify generation/storage profiles and call `start_world()`. |
| Player movement does not stream terrain | Confirm `player_driven_viewer_enabled` and viewer radius settings. |
| Edit is rejected | Inspect `game_world.get_last_edit_summary()` and the terrain world last error. |
| Generated files are large | Use deterministic compact profiles and keep dense normal terrain files out of the game path. |
| Git status fills with cache files | Ignore `.godot/`, `build/`, and `*.gd.uid`. |

## Validation commands

```console
python tools/g57_separate_game_repository_integration_quality.py --skip-build
python tools/g58_documentation_examples_quality.py
```

Expected markers:

```text
WT_INTEGRATION_GAME_G57_PASS
WT_VALIDATION_G57_SEPARATE_GAME_REPOSITORY_SMOKE_PASS
WT_VALIDATION_G58_DOCUMENTATION_EXAMPLES_PASS
WT_VALIDATION_G58_DOCUMENTATION_EXAMPLES_SMOKE_PASS
```

## Boundary

These examples cover terrain adoption only. They do not complete fluids,
vegetation, voxel buildings, planets, multiplayer, compute-shader acceleration,
or final game-specific art direction.
