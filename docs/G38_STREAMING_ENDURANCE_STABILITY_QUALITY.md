# G38 - Streaming endurance stability quality

Status: complete when `WT_VALIDATION_G38_CONTRACT_PASS` and
`WT_VALIDATION_G38_STREAMING_ENDURANCE_STABILITY_SMOKE_PASS` both pass.

G38 is the active runtime terrain quality gate for streaming endurance stability
quality. It repeats the compact 2K streaming route for two cycles, performs real
scripted local player movement at each waypoint, and verifies the terrain returns
to cold idle with the standard 25-resource active window after the endurance run.

Exit:

- the compact 2K backend exposes all 16384 pages;
- two route cycles exercise ten route samples;
- each sample performs scripted player movement through the real player;
- total local player movement is at least 50 meters;
- each settled active window returns to 25 render, collision, and chunk records;
- transient streaming overlap remains bounded to 50 records/resources;
- render fade/blink resources stay at zero;
- final cold idle is true after the repeated route;
- dense near-2K source/world files are not reintroduced.

Boundary:

- G38 detects repeated movement-streaming leaks in the current compact CPU/native
  terrain path. It does not claim final terrain art, seamless dynamic LOD,
  GPU/compute generation, fluids, biomes, vegetation, buildings, multiplayer,
  or a separate game repository.

Run:

```console
python tools/g38_streaming_endurance_stability_quality.py
```

Expected markers:

```text
WT_VALIDATION_G38_CONTRACT_PASS implementation=streaming_endurance_stability_quality
WT_VALIDATION_G38_STREAMING_ENDURANCE_STABILITY_PASS profile=g19_compact_2k_on_demand route_cycles=2 route_samples=10 local_motion_samples=10 total_player_motion=... viewer_updates_delta=... max_settle_frames=... max_render_resources=... max_collision_resources=... max_active_records=... max_pending_retirements=... max_render_fading_resources=0 final_render_resources=25 final_collision_resources=25 final_active_records=25 final_cold_idle=true dense_world_files=0
WT_VALIDATION_G38_STREAMING_ENDURANCE_STABILITY_SMOKE_PASS profile=g19_compact_2k_on_demand engines=... route_cycles=2 route_samples=10 max_settle_frames=... min_total_player_motion=... final_cold_idle=true quality_track=runtime_terrain dense_world_files=0 report=artifacts/g38_streaming_endurance_stability_quality/g38_streaming_endurance_stability_quality_report.json
```
