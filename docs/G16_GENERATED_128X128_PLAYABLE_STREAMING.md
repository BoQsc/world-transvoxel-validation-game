# G16 - Generated 128x128 playable streaming

Status: complete when `WT_VALIDATION_G16_CONTRACT_PASS` and
`WT_VALIDATION_G16_GENERATED_128X128_PLAYABLE_STREAMING_SMOKE_PASS` both pass.

G16 scales the dense generated terrain path from G14's 64 by 64 fixture to a
128 by 128 dense generated terrain fixture. This is the first near-2K generated
terrain step: 128 chunks at 16 blocks per chunk gives roughly 2048 by 2048
horizontal blocks and 16384 generated pages.

Exit:

- `g16_generated_128x128` is a selectable playable profile;
- the fixture is baked through `world-transvoxel/tools/wt_bake.py` and contains
  16384 generated pages;
- generated source writing uses the streamed source writer;
- the streamed source files are size-checked:
  `density.f32 = 1095850340` bytes and `materials.u16 = 547925170` bytes;
- the normal first-person playtest path starts with one active viewer, player,
  camera, crosshair, collision, materialized terrain, and human input disabled
  for autonomous validation;
- the smoke moves the same viewer ID through the 128 by 128 terrain and
  requires 9/25/25/25/9 active render/collision resources;
- `MAX_ACTIVE_RESOURCES := 25` remains the playable-scene streaming budget and
  the scene does not load all 16384 generated pages as active resources;
- scripted player motion and an active-center edit remain valid after
  streaming, with `render_fading_resources == 0`;
- the existing G13 vertical coverage guard includes this profile before runtime
  validation is considered complete.

Commands:

```console
python tools/validate_g16_contract.py
python tools/g16_generated_128x128_playable_streaming_smoke.py
```

Expected markers:

```text
WT_VALIDATION_G16_CONTRACT_PASS implementation=generated_128x128_playable_streaming
WT_VALIDATION_G16_GENERATED_128X128_PLAYABLE_STREAMING_PASS profile=g16_generated_128x128 samples=5 pages=16384 max_render_resources=25 max_collision_resources=25 edit_replacements=...
WT_VALIDATION_G16_GENERATED_128X128_PLAYABLE_STREAMING_SMOKE_PASS engines=2 report=artifacts/g16_generated_128x128_playable_streaming/g16_generated_128x128_playable_streaming_report.json
```
