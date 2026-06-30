# G43 - View distance presentation quality

Status: complete when `WT_VALIDATION_G43_CONTRACT_PASS` and
`WT_VALIDATION_G43_VIEW_DISTANCE_PRESENTATION_SMOKE_PASS` both pass.

G43 is the active runtime terrain quality gate for view distance presentation
quality. It captures multiple first-person views in the compact 2K world and
asserts that terrain presentation is not a tiny one-chunk patch: the full terrain
visual must cover the compact 2K footprint, captures must contain enough colored
terrain, and terrain pixels must span enough horizontal, vertical, and
mid-distance image bands.

Exit:

- the compact 2K scene reaches playable ready state with human input disabled;
- the full terrain visual reports `2048 by 2048` block coverage;
- at least three first-person map-scale captures are written;
- every capture contains enough colored terrain samples;
- every capture spans enough horizontal and vertical image bins;
- every capture contains enough mid-band terrain samples for horizon/presentation
  coverage;
- local active render and collision resources remain bounded to 25 after each
  sampled position settles;
- render fade/blink resources stay at zero;
- dense near-2K source/world files are not reintroduced.

Boundary:

- G43 detects one-chunk-only or tiny-patch first-person presentation regressions
  in the current compact CPU/native terrain path. It does not claim final art
  direction, final draw-distance policy, seamless dynamic LOD, GPU/compute
  generation, fluids, biomes, vegetation, buildings, multiplayer, or a separate
  game repository.

Run:

```console
python tools/g43_view_distance_presentation_quality.py
```

Expected markers:

```text
WT_VALIDATION_G43_CONTRACT_PASS implementation=view_distance_presentation_quality
WT_VALIDATION_G43_VIEW_DISTANCE_PRESENTATION_PASS profile=g19_compact_2k_on_demand captures=3 full_visual_blocks=2048x2048 min_colored_samples=... min_horizontal_bins=... min_vertical_bins=... min_mid_band_samples=... max_render_resources=25 max_collision_resources=25 max_render_fading_resources=0 dense_world_files=0
WT_VALIDATION_G43_VIEW_DISTANCE_PRESENTATION_SMOKE_PASS profile=g19_compact_2k_on_demand engines=... captures=3 min_colored_samples=... min_horizontal_bins=... min_mid_band_samples=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g43_view_distance_presentation_quality/g43_view_distance_presentation_quality_report.json
```
