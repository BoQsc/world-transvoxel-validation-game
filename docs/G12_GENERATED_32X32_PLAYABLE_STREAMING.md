# G12 - Generated 32x32 playable streaming

Status: complete when `WT_VALIDATION_G12_CONTRACT_PASS` and
`WT_VALIDATION_G12_GENERATED_32X32_PLAYABLE_STREAMING_SMOKE_PASS` both pass.

G12 scales the generated terrain path from G11's 16 by 16 fixture to a 32 by 32
dense generated terrain fixture. It is still a controlled validation fixture,
not the final 2000 by 2000 world, but it proves the same playable streaming
contract against 1024 generated pages.

Exit:

- `g12_generated_32x32` is a selectable playable profile;
- the fixture is generated from deterministic Python density/material source and
  baked through `world-transvoxel/tools/wt_bake.py`;
- the baked world contains 1024 generated pages;
- startup creates one viewer at the origin and settles to 9 active
  render/collision resources;
- the smoke moves the same viewer ID across the generated terrain and requires
  9/25/25/25/9 active render/collision resources;
- `MAX_ACTIVE_RESOURCES := 25` remains the playable-scene streaming budget for
  this generated fixture;
- player, first-person camera, crosshair, collision, materialized terrain,
  scripted motion, and active-center edit submission stay working;
- edit replacement keeps `render_fading_resources == 0`;
- this milestone does not load all 1024 generated pages as active resources and
  does not claim final 2000 by 2000 generated terrain.

Required commands:

```text
python tools/validate_g12_contract.py
python tools/g12_generated_32x32_playable_streaming_smoke.py
```

Expected markers:

```text
WT_VALIDATION_G12_CONTRACT_PASS implementation=generated_32x32_playable_streaming
WT_VALIDATION_G12_GENERATED_32X32_PLAYABLE_STREAMING_PASS profile=g12_generated_32x32 samples=5 pages=1024 max_render_resources=25 max_collision_resources=25 edit_replacements=...
WT_VALIDATION_G12_GENERATED_32X32_PLAYABLE_STREAMING_SMOKE_PASS engines=2 report=artifacts/g12_generated_32x32_playable_streaming/g12_generated_32x32_playable_streaming_report.json
```
