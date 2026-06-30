# G42 - Collision traversal stability quality

Status: complete when `WT_VALIDATION_G42_CONTRACT_PASS` and
`WT_VALIDATION_G42_COLLISION_TRAVERSAL_STABILITY_SMOKE_PASS` both pass.

G42 is the active runtime terrain quality gate for collision traversal stability
quality. It drives the real validation player across flat baseline terrain,
mountain/sloped terrain, and edited compact 2K terrain while checking floor
contact, movement distance, control state, vertical stability, active resources,
and fade/blink resources.

Exit:

- flat, mountain/sloped, and edited compact 2K terrain cases are exercised;
- every case reaches the normal playable scene with human input disabled;
- scripted movement remains active through the real player controller;
- total player motion crosses the minimum route distance;
- floor contact ratio stays above the stability threshold;
- no long off-floor streak, falling through terrain, or excessive vertical
  velocity is observed;
- camera/control state remains valid during traversal;
- edited terrain traversal includes a real terrain edit before movement;
- transient active resources stay bounded;
- render fade/blink resources stay at zero;
- dense near-2K source/world files are not reintroduced.

Boundary:

- G42 detects collision traversal regressions in current validation profiles. It
  does not claim final character controller design, final terrain art, seamless
  dynamic LOD, GPU/compute generation, fluids, biomes, vegetation, buildings,
  multiplayer, or a separate game repository.

Run:

```console
python tools/g42_collision_traversal_stability_quality.py
```

Expected markers:

```text
WT_VALIDATION_G42_CONTRACT_PASS implementation=collision_traversal_stability_quality
WT_VALIDATION_G42_COLLISION_TRAVERSAL_STABILITY_PASS profile_cases=3 route_segments=... edited_segments=... total_motion=... min_floor_contact_ratio=... max_off_floor_streak=... min_player_y=... max_abs_vertical_velocity=... max_render_resources=... max_collision_resources=... max_active_records=... max_render_fading_resources=0 dense_world_files=0
WT_VALIDATION_G42_COLLISION_TRAVERSAL_STABILITY_SMOKE_PASS engines=... profile_cases=3 route_segments=... total_motion=... min_floor_contact_ratio=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g42_collision_traversal_stability_quality/g42_collision_traversal_stability_quality_report.json
```
