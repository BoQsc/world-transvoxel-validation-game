# G46 - Terrain addon API contract quality

Status: complete when `WT_VALIDATION_G46_CONTRACT_PASS` and
`WT_VALIDATION_G46_TERRAIN_ADDON_API_CONTRACT_SMOKE_PASS` both pass.

G46 is the terrain addon API contract quality gate. It locks the first minimal game-facing API contract for
`world-transvoxel-terrain`. The validation game must be able to start terrain,
stream a viewer, submit an edit, query authoritative samples, inspect storage
and telemetry state, and read a debug snapshot through `WtTerrainWorld` public
methods and signals.

## Exit

- `WtTerrainWorld` exposes stable public lifecycle aliases:
  `start_world`, `stop_world`, `is_world_running`, `get_world_state_name`,
  `get_world_revision`, `get_world_source_revision`, and
  `get_world_page_count`.
- `WtTerrainWorld` exposes public profile, streaming, editing, storage,
  telemetry, and debug API groups through `get_terrain_api_contract_summary`.
- Authoritative sample requests are available through public
  `request_authoritative_sample` and `request_authoritative_samples` methods
  plus public ready/failed signals.
- The validation gate uses the public API path with no direct backend calls and reports
  `direct_backend_calls=0`.
- The compact 2K runtime starts, streams to the normal 25-resource detail
  window, commits a construct edit, verifies the edited authoritative sample,
  and reads runtime/debug summaries through the public terrain addon API.
- Dense near-2K source/world files are not reintroduced.

## Boundary

- G46 locks the minimal terrain addon API surface required by a normal Godot
  game. It does not remove every old validation helper, complete material art,
  finish underground generation, solve LOD seams, add water/vegetation/buildings,
  or prove a separate game repository.
- Validation-game workaround removal remains G47.

## Evidence

```text
python tools/validate_g46_contract.py
python tools/g46_terrain_addon_api_contract_quality.py
WT_VALIDATION_G46_CONTRACT_PASS implementation=terrain_addon_api_contract_quality
WT_VALIDATION_G46_TERRAIN_ADDON_API_CONTRACT_PASS profile=g19_compact_2k_on_demand api_version=1 public_methods=22 stable_groups=7 lifecycle=1 streaming=1 edits=1 storage=1 telemetry=1 debug=1 samples=... edit_committed=1 world_revision_delta=... max_render_resources=25 max_collision_resources=25 max_active_records=25 direct_backend_calls=0 dense_world_files=0
WT_VALIDATION_G46_TERRAIN_ADDON_API_CONTRACT_SMOKE_PASS profile=g19_compact_2k_on_demand engines=... api_version=1 public_methods=22 stable_groups=7 direct_backend_calls=0 quality_track=runtime_terrain dense_world_files=0 report=artifacts/g46_terrain_addon_api_contract_quality/g46_terrain_addon_api_contract_quality_report.json
```
