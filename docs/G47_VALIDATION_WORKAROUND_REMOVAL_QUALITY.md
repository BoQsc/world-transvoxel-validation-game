# G47 - Validation workaround removal quality

Status: complete when `WT_VALIDATION_G47_CONTRACT_PASS` and
`WT_VALIDATION_G47_VALIDATION_WORKAROUND_REMOVAL_SMOKE_PASS` both pass.

G47 audits the validation game for terrain implementation helpers that belong in
`world-transvoxel-terrain`, moves required reusable helpers into the addon, and
quarantines historical backend-facing test references so they cannot be confused
with game-facing runtime architecture.
The audit reports quarantined historical backend references separately from
normal validation runtime scripts.

## Exit

- `ValidationTerrainMaterials` uses addon-owned `WtTerrainMaterialApplicator`.
- The validation terrain palette shader is addon-owned.
- Runtime mesh counting uses addon-owned `WtTerrainMeshStats`.
- The local validation-game files `scripts/validation_terrain_materials.gd`,
  `scripts/validation_mesh_stats.gd`, and
  `materials/validation_terrain_palette.gdshader` are absent.
- Normal validation runtime scripts do not call `get_backend_terrain` or
  `get_backend_world_state_name`.
- Remaining direct backend calls in historical tests are reported as
  quarantined audit evidence, not hidden game runtime implementation.
- The compact 2K validation scene still reaches ready state, applies terrain
  materials, reports mesh stats, and remains inside the 25-resource active
  window.

## Boundary

- G47 removes the required reusable material and mesh-inspection workarounds
  from the validation game. It does not rewrite every historical test to the
  G46 public API path, complete native hot-path policy, finish materials, solve
  underground terrain, LOD seams, streaming-radius standards, or prove a
  separate game repository.
- Native hot-path boundary quality remains G48.

## Evidence

```text
python tools/validate_g47_contract.py
python tools/g47_validation_workaround_removal_quality.py
WT_VALIDATION_G47_CONTRACT_PASS implementation=validation_workaround_removal_quality
WT_VALIDATION_G47_VALIDATION_WORKAROUND_REMOVAL_PASS profile=g19_compact_2k_on_demand moved_helpers=2 local_workaround_files=0 material_impl=terrain_addon_material_applicator mesh_stats_impl=terrain_addon_mesh_stats materialized=... max_render_resources=25 max_collision_resources=25 max_active_records=25 dense_world_files=0
WT_VALIDATION_G47_VALIDATION_WORKAROUND_REMOVAL_SMOKE_PASS profile=g19_compact_2k_on_demand engines=... moved_helpers=2 local_workaround_files=0 direct_runtime_backend_refs=0 quarantined_historical_backend_tests=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g47_validation_workaround_removal_quality/g47_validation_workaround_removal_quality_report.json
```
