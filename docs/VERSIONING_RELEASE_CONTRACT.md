# Versioning and release contract

Status: G59 release contract source.

This contract applies to the current Terrain 1.0 stack:

- `world-transvoxel`;
- `world-transvoxel-terrain`;
- `world_transvoxel_game_world` prototype addon;
- `world-transvoxel-integration-game`.

## Versioning

Terrain 1.0 uses milestone-gated release readiness. After 1.0, public addon
releases should use semantic versioning:

- patch: compatible bug fix or validation improvement;
- minor: additive public API, profile, telemetry, or documentation feature;
- major: breaking public API, storage, migration, or supported-engine change.

Each release must record the exact source commits for all three addon layers.

## Compatibility

The currently supported Godot versions are:

- Godot 4.6.3 stable;
- Godot 4.7 stable.

The currently validated native target is Windows x86_64. Additional platforms
must get their own build and runtime validation before being listed as
supported.

## Migration policy

Breaking changes require a migration note before release. Migration notes must
cover:

- public API method/property changes;
- terrain profile changes;
- storage path/schema changes;
- edit journal format changes;
- material palette or material-id changes;
- generated world source revision changes.

Existing edit journals and compact profile storage must either continue to load
or fail with a clear recovery error.

## License boundary

The current low-level Transvoxel backend uses the original MIT-licensed
Transvoxel reference code isolated under the `world-transvoxel` addon. The 0BSD
replacement backend is not the default and must not be claimed as an exact
official replacement unless a future oracle proves exact compatibility.

Terrain/game-world code must not copy MIT Transvoxel lookup tables into a 0BSD
source path. License notices and third-party source boundaries must stay
explicit.

## Source/reference policy

Reference material belongs in clearly named third-party or docs/reference paths.
Implementation code must state whether it is:

- original project code;
- isolated MIT Transvoxel-derived code;
- generated validation artifact;
- aggregate comparison/report output.

Do not mix original MIT source files into 0BSD implementation paths.

## Release checklist

Before a Terrain 1.0 release candidate:

- G41 through G59 validators pass;
- G57 external integration proof passes on both supported Godot versions;
- G58 documentation examples are current;
- no known critical correctness, collision, storage, performance, or integration
  blocker remains;
- no normal compact 2K path requires dense normal terrain files;
- generated `.godot/`, `build/`, and `*.gd.uid` files remain ignored unless a
  repository intentionally tracks a specific file.
