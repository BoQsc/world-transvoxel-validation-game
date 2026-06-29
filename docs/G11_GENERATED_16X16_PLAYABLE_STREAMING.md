# G11 - Generated 16x16 playable streaming

Status: complete when `WT_VALIDATION_G11_CONTRACT_PASS` and
`WT_VALIDATION_G11_GENERATED_16X16_PLAYABLE_STREAMING_SMOKE_PASS` both pass.

G11 moves beyond the sparse 2K path fixture. It bakes a deterministic 16 by 16
dense generated terrain fixture through the same `world-transvoxel` bake path
used by G3, then loads it through the normal `world-transvoxel-terrain`
playable validation scene.

Exit:

- `g11_generated_16x16` is a selectable playable profile;
- the fixture is generated from deterministic Python density/material source and
  baked through `world-transvoxel/tools/wt_bake.py`;
- the baked world contains 256 generated pages;
- startup creates one viewer at the origin and settles to 9 active
  render/collision resources;
- the smoke moves the same viewer ID across the generated terrain and requires
  9/25/25/25/9 active render/collision resources;
- `MAX_ACTIVE_RESOURCES := 25` remains the playable-scene streaming budget for
  this generated fixture;
- player, first-person camera, crosshair, collision, materialized terrain,
  scripted motion, and active-center edit submission stay working;
- edit replacement keeps `render_fading_resources == 0`;
- this milestone does not load all 256 generated pages as active resources and
  does not claim final 2000 by 2000 generated terrain.

Required commands:

```text
python tools/validate_g11_contract.py
python tools/g11_generated_16x16_playable_streaming_smoke.py
```

Expected markers:

```text
WT_VALIDATION_G11_CONTRACT_PASS implementation=generated_16x16_playable_streaming
WT_VALIDATION_G11_GENERATED_16X16_PLAYABLE_STREAMING_PASS profile=g11_generated_16x16 samples=5 pages=256 max_render_resources=25 max_collision_resources=25 edit_replacements=...
WT_VALIDATION_G11_GENERATED_16X16_PLAYABLE_STREAMING_SMOKE_PASS engines=2 report=artifacts/g11_generated_16x16_playable_streaming/g11_generated_16x16_playable_streaming_report.json
```
