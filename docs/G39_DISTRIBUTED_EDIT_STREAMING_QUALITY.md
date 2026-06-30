# G39 - Distributed edit streaming quality

Status: complete when `WT_VALIDATION_G39_CONTRACT_PASS` and
`WT_VALIDATION_G39_DISTRIBUTED_EDIT_STREAMING_SMOKE_PASS` both pass.

G39 is the active runtime terrain quality gate for distributed edit streaming
quality. It streams the compact 2K player to four distant map regions, applies
real carve/construct edits there, verifies authoritative backend samples, then
reloads the scene and verifies all four edits replay from the edit journal.

Exit:

- the compact 2K backend exposes all 16384 pages;
- four distant edit sites are streamed to before editing;
- carve and construct edits both commit in distant regions;
- authoritative samples match the edited density/material at each site;
- the edit journal is created and remains inside the compact storage budget;
- a fresh scene reload replays all four distributed edits;
- the replay scene returns to cold idle with 25 render and collision resources;
- render fade/blink resources stay at zero;
- dense near-2K source/world files are not reintroduced.

Boundary:

- G39 detects distributed edit and replay regressions in the current compact
  CPU/native terrain path. It does not claim final terrain art, seamless dynamic
  LOD, GPU/compute generation, fluids, biomes, vegetation, buildings,
  multiplayer, or a separate game repository.

Run:

```console
python tools/g39_distributed_edit_streaming_quality.py
```

Expected markers:

```text
WT_VALIDATION_G39_CONTRACT_PASS implementation=distributed_edit_streaming_quality
WT_VALIDATION_G39_DISTRIBUTED_EDIT_STREAMING_PASS profile=g19_compact_2k_on_demand edit_sites=4 replayed=4 max_commit_frames=... max_settle_frames=... journal_bytes=... max_render_resources=25 max_collision_resources=25 final_render_resources=25 final_collision_resources=25 final_cold_idle=true dense_world_files=0
WT_VALIDATION_G39_DISTRIBUTED_EDIT_STREAMING_SMOKE_PASS profile=g19_compact_2k_on_demand engines=... edit_sites=4 replayed=4 max_commit_frames=... max_settle_frames=... final_cold_idle=true quality_track=runtime_terrain dense_world_files=0 report=artifacts/g39_distributed_edit_streaming_quality/g39_distributed_edit_streaming_quality_report.json
```
