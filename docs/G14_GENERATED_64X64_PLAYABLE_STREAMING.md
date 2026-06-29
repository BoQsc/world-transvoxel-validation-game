# G14 - Generated 64x64 playable streaming

Status: complete when `WT_VALIDATION_G14_CONTRACT_PASS` and
`WT_VALIDATION_G14_GENERATED_64X64_PLAYABLE_STREAMING_SMOKE_PASS` both pass.

G14 scales the dense generated terrain path from G12's 32 by 32 fixture to a 64
by 64 dense generated terrain fixture. This is roughly a 1024 by 1024 block
terrain step and contains 4096 generated pages. Because this fixture is large
enough that source files are no longer trivial, G14 also introduces a streamed
source writer for density/material source generation.

Exit:

- `g14_generated_64x64` is a selectable playable profile;
- the fixture is generated from deterministic Python density/material source and
  baked through `world-transvoxel/tools/wt_bake.py`;
- the source writer streams density and material rows to disk instead of
  accumulating one large in-memory bytearray;
- the baked world contains 4096 generated pages;
- the fixture passes the generated vertical coverage guard from G13;
- startup creates one viewer at the origin and settles to 9 active
  render/collision resources;
- the smoke moves the same viewer ID across the generated terrain and requires
  9/25/25/25/9 active render/collision resources;
- `MAX_ACTIVE_RESOURCES := 25` remains the playable-scene streaming budget for
  this generated fixture;
- player, first-person camera, crosshair, collision, materialized terrain,
  scripted motion, and active-center edit submission stay working;
- edit replacement keeps `render_fading_resources == 0`;
- this milestone does not load all 4096 generated pages as active resources and
  does not claim final 2000 by 2000 generated terrain.

Required commands:

```text
python tools/validate_g14_contract.py
python tools/g14_generated_64x64_playable_streaming_smoke.py
```

Expected markers:

```text
WT_VALIDATION_G14_CONTRACT_PASS implementation=generated_64x64_playable_streaming
WT_VALIDATION_G14_GENERATED_64X64_PLAYABLE_STREAMING_PASS profile=g14_generated_64x64 samples=5 pages=4096 max_render_resources=25 max_collision_resources=25 edit_replacements=...
WT_VALIDATION_G14_GENERATED_64X64_PLAYABLE_STREAMING_SMOKE_PASS engines=2 report=artifacts/g14_generated_64x64_playable_streaming/g14_generated_64x64_playable_streaming_report.json
```
