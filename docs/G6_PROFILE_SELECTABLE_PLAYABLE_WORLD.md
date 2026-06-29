# G6 Profile-Selectable Playable World

Status: complete by `WT_VALIDATION_G6_CONTRACT_PASS` and
`WT_VALIDATION_G6_SMOKE_PASS`.

## What this gate proves

G6 moves the playable validation scene beyond a single default fixture:

- `ValidationPlaytest.configure_playtest_profile()` exposes selectable playable
  profiles;
- `flat_8x8` and `mountain_8x8` load through the same generated playtest
  scene, first-person player, crosshair, terrain materializer, and interactor;
- these are 8 by 8 multi-chunk validation fixtures, not the final 2000×2000
  block exploration target;
- each multi-chunk profile submits 4 radius-2 coverage viewer positions, keeps
  render and collision telemetry live, loads the 8 by 8 page set, and reaches
  cold idle;
- the smoke disables human input before the scene enters the tree;
- both profiles perform automated carve and construct/place submissions through
  `ValidationTerrainInteractor`;
- both profiles apply the checker terrain material and save windowed
  first-person plus overview captures before human visual handoff.
- human playtest input captures mouse on start, overlay controls ignore mouse
  events, and a recapture click is suppressed so it does not also carve/place.
- human playtest feedback reported that the previous 4 by 4 fixture looked too
  small, visible multi-chunk evidence was not obvious to a player, and real
  performance could not be judged from that scale. The current gate therefore
  bakes and loads an 8 by 8 fixture before human handoff.
- `tools/prepare_human_playtest.py` prepares a reproducible human-playtest
  project and pins `res://scenes/validation_playtest.tscn` to `flat_8x8`, so
  human testing does not depend on manual edits to ignored generated artifacts.

Expected markers:

```text
WT_VALIDATION_G6_CONTRACT_PASS implementation=profile_selectable_playable_world next=human_visual_verification
WT_VALIDATION_G6_SMOKE_PASS profiles=2 engines=2 report=artifacts/g6_profile_selectable_playable_world/g6_profile_selectable_playable_world_report.json
WT_VALIDATION_HUMAN_INPUT_CAPTURE_SMOKE_PASS engines=2 report=artifacts/human_input_capture/human_input_capture_report.json
WT_VALIDATION_HUMAN_PLAYTEST_READY profile=flat_8x8 project=... scene=res://scenes/validation_playtest.tscn launch=false fullscreen=false report=artifacts/human_playtest/human_playtest_report.json
```

## Not claimed

G6 is still not final production terrain. It does not claim seamless dynamic
LOD, 2K-world exploration, meaning 2000 by 2000 horizontal blocks at the
standard baseline of 1 block = 1 meter, water/lava, vegetation, buildings,
multiplayer, compute-shader acceleration, production art, or final performance
budgets.
