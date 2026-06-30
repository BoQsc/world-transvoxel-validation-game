# G41 - Runtime frame budget telemetry quality

Status: complete when `WT_VALIDATION_G41_CONTRACT_PASS` and
`WT_VALIDATION_G41_RUNTIME_FRAME_BUDGET_TELEMETRY_SMOKE_PASS` both pass.

G41 is the active runtime terrain quality gate for runtime frame budget
telemetry quality. It measures the normal compact 2K runtime scene through
settled idle, streaming movement, real carve/construct edits, and reload after
edits. The goal is not to claim final GPU/CPU optimization; the goal is to make
runtime cost visible, bounded, and machine-readable before the next Terrain 1.0
gates build on it.

Exit:

- the compact 2K scene reaches playable ready state with human input disabled;
- telemetry covers idle, movement/streaming, edit, and reload phases;
- at least five telemetry phases and at least 240 measured frames are recorded;
- every phase reports average and max frame milliseconds;
- the maximum phase average frame time remains under the telemetry budget;
- the maximum measured frame time remains under the spike budget;
- settled active resources return to the 25-resource compact detail window;
- transient active resources remain bounded during streaming/edit/reload;
- render fade/blink resources stay at zero;
- dense near-2K source/world files are not reintroduced;
- a JSON telemetry report is written for later trend comparison.

Boundary:

- G41 creates the first production-gap runtime telemetry contract. It does not
  prove final optimization, GPU/compute acceleration, seamless dynamic LOD,
  fluids, biomes, vegetation, buildings, multiplayer, or a separate game
  repository.

Run:

```console
python tools/g41_runtime_frame_budget_telemetry_quality.py
```

Expected markers:

```text
WT_VALIDATION_G41_CONTRACT_PASS implementation=runtime_frame_budget_telemetry_quality
WT_VALIDATION_G41_RUNTIME_FRAME_BUDGET_TELEMETRY_PASS profile=g19_compact_2k_on_demand phases=... total_frames=... max_frame_ms=... max_avg_frame_ms=... movement_samples=... edits=2 reload_ready_frames=... max_render_resources=... max_collision_resources=... max_active_records=... max_queued_render=... max_queued_collision=... max_pending_retirements=... max_render_fading_resources=0 dense_world_files=0 telemetry=res://artifacts/g41_runtime_frame_budget_telemetry_quality/frame_telemetry.json
WT_VALIDATION_G41_RUNTIME_FRAME_BUDGET_TELEMETRY_SMOKE_PASS profile=g19_compact_2k_on_demand engines=... phases=... total_frames=... max_frame_ms=... max_avg_frame_ms=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g41_runtime_frame_budget_telemetry_quality/g41_runtime_frame_budget_telemetry_quality_report.json
```
