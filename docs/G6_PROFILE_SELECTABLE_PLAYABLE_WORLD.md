# G6 Profile-Selectable Playable World

Status: complete by `WT_VALIDATION_G6_CONTRACT_PASS` and
`WT_VALIDATION_G6_SMOKE_PASS`.

## What this gate proves

G6 moves the playable validation scene beyond a single default fixture:

- `ValidationPlaytest.configure_playtest_profile()` exposes selectable playable
  profiles;
- `flat_large` and `mountain_large` load through the same generated playtest
  scene, first-person player, crosshair, terrain materializer, and interactor;
- despite the profile names, these are small multi-chunk validation fixtures,
  not exploration-scale large terrain;
- each multi-chunk profile submits 16 viewer positions, keeps render and
  collision telemetry live, and reaches cold idle;
- the smoke disables human input before the scene enters the tree;
- both profiles perform automated carve and construct/place submissions through
  `ValidationTerrainInteractor`;
- both profiles apply the checker terrain material and save windowed
  first-person plus overview captures before human visual handoff.
- human playtest input captures mouse on start, overlay controls ignore mouse
  events, and a recapture click is suppressed so it does not also carve/place.
- human playtest feedback reported that the fixture still looks small, visible
  multi-chunk evidence is not obvious to a player, and real performance cannot
  be judged from this scale.

Expected markers:

```text
WT_VALIDATION_G6_CONTRACT_PASS implementation=profile_selectable_playable_world next=human_visual_verification
WT_VALIDATION_G6_SMOKE_PASS profiles=2 engines=2 report=artifacts/g6_profile_selectable_playable_world/g6_profile_selectable_playable_world_report.json
WT_VALIDATION_HUMAN_INPUT_CAPTURE_SMOKE_PASS engines=2 report=artifacts/human_input_capture/human_input_capture_report.json
```

## Not claimed

G6 is still not final production terrain. It does not claim seamless dynamic
LOD, 2K-world exploration, water/lava, vegetation, buildings, multiplayer,
compute-shader acceleration, production art, or final performance budgets.
