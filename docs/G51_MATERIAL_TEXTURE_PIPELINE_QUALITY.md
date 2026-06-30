# G51 - Material texture pipeline quality

Status: complete when `WT_VALIDATION_G51_CONTRACT_PASS` and
`WT_VALIDATION_G51_MATERIAL_TEXTURE_PIPELINE_SMOKE_PASS` both pass.

G51 locks the current Terrain 1.0 material/texture quality contract for the
normal compact 2K validation path. It is a deterministic small-asset pipeline
gate, not a final art gate.

## Quality bar

The gate requires:

- material application remains addon-owned through
  `WtTerrainMaterialApplicator`;
- the material profile exposes `terrain_material_profile_contract_v1`;
- the applicator exposes `terrain_material_texture_pipeline_v1`;
- terrain uses the UV2 material-id shader path;
- the standard generated checker texture is deterministic;
- the generated texture remains small: 16 by 16 `RGBA8`, 1024 bytes, under the
  4 KiB G51 budget;
- the standard material IDs are `1,2,3,4,7`;
- all active compact 2K terrain meshes receive the same shared material instance;
- the material instance remains stable after a real construct edit;
- the material instance remains stable after two explicit viewer-streaming
  windows;
- an authoritative sample after construct observes material ID `4`;
- the material capture contains enough colored terrain pixels for automated
  visual evidence;
- no dense compact 2K world files are created.

## Commands

```bash
python tools/validate_g51_contract.py
python tools/g51_material_texture_pipeline_quality.py --skip-build
```

Expected markers:

```text
WT_VALIDATION_G51_CONTRACT_PASS implementation=material_texture_pipeline_quality
WT_VALIDATION_G51_MATERIAL_TEXTURE_PIPELINE_PASS profile=g19_compact_2k_on_demand materialized_initial=25 materialized_after_edit=25 materialized_after_stream=25 texture_resolution=16 texture_bytes=1024 texture_checksum=... palette_ids=1,2,3,4,7 deterministic=1 shader_mode=addon_uv2_checker edit_material=4 material_instance_stable=1 stream_windows=2 capture_colored_samples=... material_auto_apply_delta=... max_render_resources=25 max_collision_resources=25 dense_world_files=0
WT_VALIDATION_G51_MATERIAL_TEXTURE_PIPELINE_SMOKE_PASS profile=g19_compact_2k_on_demand engines=... texture_resolution=16 texture_bytes_max=4096 material_instance_stable=1 max_engine_seconds=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g51_material_texture_pipeline_quality/g51_material_texture_pipeline_quality_report.json
```

## Boundary

G51 does not claim final production terrain art, external texture packs, biome
materials, underground material variation, large-world streaming radius, LOD seam
quality, map-generator budget quality, water, vegetation, buildings,
multiplayer, compute acceleration, or separate game integration.
