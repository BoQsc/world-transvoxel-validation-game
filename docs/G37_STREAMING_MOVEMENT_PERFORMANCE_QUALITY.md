# G37 - Streaming movement performance quality

Status: complete when `WT_VALIDATION_G37_CONTRACT_PASS` and
`WT_VALIDATION_G37_STREAMING_MOVEMENT_PERFORMANCE_SMOKE_PASS` both pass.

G37 is the active runtime terrain quality gate for streaming movement
performance quality. It drives the real validation player across interior
waypoints in the compact 2K map, performs scripted local movement at each
waypoint, and measures whether the active terrain detail window settles without
resource spikes or fade/blink resources.

Exit:

- the compact 2K backend exposes all 16384 pages;
- five interior 2K route samples are exercised;
- each route sample performs real scripted player movement;
- total local player movement is at least 40 meters;
- each streaming transition settles within the frame budget;
- each settled active window returns to 25 render, collision, and chunk records;
- transient streaming overlap remains bounded to 50 records/resources;
- render fade/blink resources stay at zero;
- material auto-apply count stays bounded per route sample;
- dense near-2K source/world files are not reintroduced.

Boundary:

- G37 detects movement-streaming regressions in the current compact CPU/native
  terrain path. It does not claim final terrain art, seamless dynamic LOD,
  GPU/compute generation, fluids, biomes, vegetation, buildings, multiplayer,
  or a separate game repository.

Run:

```console
python tools/g37_streaming_movement_performance_quality.py
```

Expected markers:

```text
WT_VALIDATION_G37_CONTRACT_PASS implementation=streaming_movement_performance_quality
WT_VALIDATION_G37_STREAMING_MOVEMENT_PERFORMANCE_PASS profile=g19_compact_2k_on_demand route_samples=5 local_motion_samples=5 total_player_motion=... viewer_updates_delta=... max_settle_frames=... max_render_resources=... max_collision_resources=... max_active_records=... max_queued_render=... max_queued_collision=... max_pending_retirements=... max_render_fading_resources=0 max_material_auto_apply_delta=... dense_world_files=0
WT_VALIDATION_G37_STREAMING_MOVEMENT_PERFORMANCE_SMOKE_PASS profile=g19_compact_2k_on_demand engines=... route_samples=5 max_settle_frames=... min_total_player_motion=... max_render_resources=... max_collision_resources=... max_active_records=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g37_streaming_movement_performance_quality/g37_streaming_movement_performance_quality_report.json
```
