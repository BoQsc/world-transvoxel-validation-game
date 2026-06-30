# G35 - Terrain correctness artifact quality

Status: complete when `WT_VALIDATION_G35_CONTRACT_PASS` and
`WT_VALIDATION_G35_TERRAIN_CORRECTNESS_ARTIFACT_SMOKE_PASS` both pass.

G35 is the runtime terrain quality gate for terrain correctness and artifact
detection. It checks the compact 2K terrain path against backend authoritative
samples, full-map surface continuity, material-id bounds, diagonal-pair
continuity, full-map capture evidence, and bounded native detail resources.

Exit:

- the full 2048 by 2048 terrain visual has the expected mesh size;
- sampled surface heights are finite and inside the expected vertical range;
- neighboring sampled heights stay below the discontinuity threshold;
- diagonal-pair sampled heights stay below the artifact threshold;
- sampled material IDs stay inside the current terrain palette;
- backend authoritative samples match the full-map visual surface;
- full-map capture contains enough colored terrain samples;
- active render and collision resources remain bounded to 25;
- dense near-2K source/world files are not reintroduced.

Boundary:

- G35 detects correctness regressions for the current compact CPU/native terrain
  path. It does not claim final terrain art, seamless dynamic LOD, GPU/compute
  generation, fluids, biomes, vegetation, buildings, multiplayer, or a separate
  game repository.

Run:

```console
python tools/g35_terrain_correctness_artifact_quality.py
```

Expected markers:

```text
WT_VALIDATION_G35_CONTRACT_PASS implementation=terrain_correctness_artifact_quality
WT_VALIDATION_G35_TERRAIN_CORRECTNESS_ARTIFACT_PASS profile=g19_compact_2k_on_demand map_blocks=2048 surface_samples=... backend_samples=... max_backend_height_error=... min_height=... max_height=... max_neighbor_delta=... max_diagonal_pair_delta=... material_ids=... capture_colored_samples=... max_render_resources=25 max_collision_resources=25 dense_world_files=0
WT_VALIDATION_G35_TERRAIN_CORRECTNESS_ARTIFACT_SMOKE_PASS profile=g19_compact_2k_on_demand engines=... map_blocks=2048 max_backend_height_error=... max_neighbor_delta=... max_diagonal_pair_delta=... min_height=... max_height=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g35_terrain_correctness_artifact_quality/g35_terrain_correctness_artifact_quality_report.json
```
