# G54 - LOD seam and artifact quality

Status: complete when `WT_VALIDATION_G54_CONTRACT_PASS` and
`WT_VALIDATION_G54_LOD_SEAM_ARTIFACT_SMOKE_PASS` both pass.

G54 proves that the runtime can exercise real Transvoxel mixed-LOD topology
instead of only same-LOD compact terrain windows. It uses the native production
LOD streaming proof and the Godot runtime against the mixed LOD transition
fixture.

The gate verifies:

- the production transition fixture contains 28 pages and is available as
  `transition.wtworld`;
- the native `PRODUCTION_LOD_STREAMING_PASS` proof still reports balanced LOD
  streaming and transition mesh completions;
- Godot starts the mixed LOD transition fixture through `WorldTransvoxelTerrain`;
- a `maximum_lod=1` viewer settles with both LOD0 and LOD1 render meshes;
- a coarse LOD bridge chunk and a fine seam-neighbor chunk are fully ready;
- horizontal LOD seam pairs are found from actual render mesh names and chunk
  coordinates;
- boundary vertices exist on both sides of the LOD seam and the vertical seam
  gap remains below the G54 tolerance;
- diagonal mesh edges are present and bounded, preventing a silent diagonal
  spike/artifact regression;
- an edited seam remains stable, and a post-edit LOD topology change remeshes
  transition geometry with no pending retirements or render fading;
- dense compact-2K source/world files remain unnecessary.

Expected runtime marker:

```text
WT_VALIDATION_G54_LOD_SEAM_ARTIFACT_PASS pages=28 active_records=9 render_resources=... collision_resources=... lod0=... lod1=... seam_pairs=... edited_seam_pairs=... diagonal_edges=... edited_diagonal_edges=... max_boundary_gap=... edited_boundary_gap=... transition_completions=... edit_replacements=... dense_world_files=0
```

Expected smoke marker:

```text
WT_VALIDATION_G54_LOD_SEAM_ARTIFACT_SMOKE_PASS engines=... pages=28 active_capacity=40 max_engine_seconds=... dense_world_files=0 report=artifacts/g54_lod_seam_artifact_quality/g54_lod_seam_artifact_quality_report.json
```

Contract marker:

```text
WT_VALIDATION_G54_CONTRACT_PASS implementation=lod_seam_artifact_quality
```
