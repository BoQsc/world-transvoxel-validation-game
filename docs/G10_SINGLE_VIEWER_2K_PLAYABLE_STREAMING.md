# G10 - Single-viewer 2K playable streaming

Status: complete when `WT_VALIDATION_G10_CONTRACT_PASS` and
`WT_VALIDATION_G10_SINGLE_VIEWER_2K_PLAYABLE_STREAMING_SMOKE_PASS` both pass.

G10 closes the gap between the low-level G8 runtime smoke and the playable G9
profile. G8 proved one terrain viewer can stream across a logical 2000 blocks by
2000 blocks sparse path with bounded active resources. G9 proved the normal
playable scene can load that sparse fixture, but it intentionally kept all five
path windows active at once. G10 proves the playable scene can move a single
playable viewer across that same path without keeping all 93 sparse path
resources active.

Exit:

- `g10_single_viewer_2k` is a selectable playable profile;
- the profile uses `res://build/production-lifecycle-fixture/g8_2000x2000_sparse.wtworld`;
- startup creates one viewer at the origin and settles to 9 active
  render/collision resources;
- the smoke moves the same viewer ID through the G8 path and requires
  9/25/25/25/9 active render/collision resources;
- `MAX_ACTIVE_RESOURCES := 25` is the playable-scene streaming budget for this
  sparse path;
- player, first-person camera, crosshair, collision, materialized terrain,
  scripted motion, and active-center edit submission stay working;
- edit replacement keeps `render_fading_resources == 0`;
- this milestone does not keep all 93 sparse path resources active and does not
  claim a fully generated visible 2000 by 2000 terrain surface.

Required commands:

```text
python tools/validate_g10_contract.py
python tools/g10_single_viewer_2k_playable_streaming_smoke.py
```

Expected markers:

```text
WT_VALIDATION_G10_CONTRACT_PASS implementation=single_viewer_2k_playable_streaming
WT_VALIDATION_G10_SINGLE_VIEWER_2K_PLAYABLE_STREAMING_PASS profile=g10_single_viewer_2k samples=5 pages=93 max_render_resources=25 max_collision_resources=25 edit_replacements=...
WT_VALIDATION_G10_SINGLE_VIEWER_2K_PLAYABLE_STREAMING_SMOKE_PASS engines=2 report=artifacts/g10_single_viewer_2k_playable_streaming/g10_single_viewer_2k_playable_streaming_report.json
```
