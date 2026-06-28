# G6 Profile-Selectable Playable World

Status: complete by `WT_VALIDATION_G6_CONTRACT_PASS` and
`WT_VALIDATION_G6_SMOKE_PASS`.

## What this gate proves

G6 moves the playable validation scene beyond a single default fixture:

- `ValidationPlaytest.configure_playtest_profile()` exposes selectable playable
  profiles;
- `flat_large` and `mountain_large` load through the same generated playtest
  scene, first-person player, crosshair, terrain materializer, and interactor;
- each large profile submits 16 viewer positions, keeps render and collision
  telemetry live, and reaches cold idle;
- the smoke disables human input before the scene enters the tree;
- both profiles perform automated carve and construct/place submissions through
  `ValidationTerrainInteractor`;
- both profiles apply the checker terrain material and save windowed
  first-person plus overview captures before human visual handoff.

Expected markers:

```text
WT_VALIDATION_G6_CONTRACT_PASS implementation=profile_selectable_playable_world next=human_visual_verification
WT_VALIDATION_G6_SMOKE_PASS profiles=2 engines=2 report=artifacts/g6_profile_selectable_playable_world/g6_profile_selectable_playable_world_report.json
```

## Not claimed

G6 is still not final production terrain. It does not claim seamless dynamic
LOD, 2K-world exploration, water/lava, vegetation, buildings, multiplayer,
compute-shader acceleration, production art, or final performance budgets.
