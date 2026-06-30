# G53 - Large-world streaming radius quality

Status: complete when `WT_VALIDATION_G53_CONTRACT_PASS` and
`WT_VALIDATION_G53_LARGE_WORLD_STREAMING_RADIUS_SMOKE_PASS` both pass.

G53 proves that the compact 2K terrain path is not locked to a tiny active
window. The validation drives the public terrain update path with human input
disabled and checks radii 1, 2, 4, and 6 against exact resource counts.

The gate verifies:

- `WtTerrainWorld.update_viewer` accepts configurable radius changes through the
  reference scene/public addon path;
- active and render resources settle exactly to 9, 25, 81, and 169;
- collision resources remain nonzero, fully ready, and bounded by the active
  radius instead of forcing collision for every far draw-distance chunk;
- active resources stay within active resource capacity 256;
- the center and four radius-edge chunks are fully ready for every radius;
- four chunks just outside the selected radius are absent for every radius;
- visible MeshInstance spread grows as radius grows;
- queued render/collision, pending retirements, and render fading are zero at
  each settled radius;
- dense compact-2K source/world files are still not required.

Expected runtime marker:

```text
WT_VALIDATION_G53_LARGE_WORLD_STREAMING_RADIUS_PASS profile=g19_compact_2k_on_demand radii=1,2,4,6 expected_resources=9,25,81,169 max_active_resources=169 active_capacity=256 inside_edge_ready=16 outside_radius_absent=16 min_span_x=... max_span_x=... min_span_z=... max_span_z=... dense_world_files=0
```

Expected smoke marker:

```text
WT_VALIDATION_G53_LARGE_WORLD_STREAMING_RADIUS_SMOKE_PASS profile=g19_compact_2k_on_demand engines=... radii=1,2,4,6 expected_resources=9,25,81,169 active_capacity=256 max_engine_seconds=... dense_world_files=0 report=artifacts/g53_large_world_streaming_radius_quality/g53_large_world_streaming_radius_quality_report.json
```

Contract marker:

```text
WT_VALIDATION_G53_CONTRACT_PASS implementation=large_world_streaming_radius_quality
```
