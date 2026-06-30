# G36 - Cold idle performance quality

Status: complete when `WT_VALIDATION_G36_CONTRACT_PASS` and
`WT_VALIDATION_G36_COLD_IDLE_PERFORMANCE_SMOKE_PASS` both pass.

G36 is the active runtime terrain quality gate for cold-idle performance
stability. It proves that the compact 2K runtime path becomes cold after the
initial active detail window settles and stays cold for a fixed idle window.

Exit:

- the compact 2K scene reaches the expected 25 active render resources;
- collision resources and fully ready active chunk records stay at 25;
- render queues, collision queues, pending retirements, and render fade/blink
  resources stay at zero;
- viewer update count does not change while the player is not moving;
- edit replacement count does not change without edits;
- material auto-apply count does not change after material stability is reached;
- dense near-2K source/world files are not reintroduced.

Boundary:

- G36 detects idle churn and background-work regressions in the current compact
  CPU/native terrain path. It does not claim final terrain art, seamless dynamic
  LOD, GPU/compute generation, fluids, biomes, vegetation, buildings,
  multiplayer, or a separate game repository.

Run:

```console
python tools/g36_cold_idle_performance_quality.py
```

Expected markers:

```text
WT_VALIDATION_G36_CONTRACT_PASS implementation=cold_idle_performance_quality
WT_VALIDATION_G36_COLD_IDLE_PERFORMANCE_PASS profile=g19_compact_2k_on_demand idle_frames=300 viewer_update_delta=0 edit_replacement_delta=0 material_auto_apply_delta=0 max_render_resources=25 max_collision_resources=25 max_active_records=25 max_queued_render=0 max_queued_collision=0 max_pending_retirements=0 max_render_fading_resources=0 cold_idle=true dense_world_files=0
WT_VALIDATION_G36_COLD_IDLE_PERFORMANCE_SMOKE_PASS profile=g19_compact_2k_on_demand engines=... idle_frames=300 viewer_update_delta=0 edit_replacement_delta=0 material_auto_apply_delta=0 max_render_resources=25 max_collision_resources=25 max_active_records=25 quality_track=runtime_terrain dense_world_files=0 report=artifacts/g36_cold_idle_performance_quality/g36_cold_idle_performance_quality_report.json
```
