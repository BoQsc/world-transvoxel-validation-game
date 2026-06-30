# G34 - Edit latency persistence quality

Status: complete when `WT_VALIDATION_G34_CONTRACT_PASS` and
`WT_VALIDATION_G34_EDIT_LATENCY_PERSISTENCE_SMOKE_PASS` both pass.

G34 is the active runtime terrain quality gate for edit latency and persistence.
It runs the compact 2K terrain path from a clean runtime state, performs timed
carve and construct edits, verifies authoritative samples, verifies edit journal
creation, reloads the scene, and verifies the edits replay from persistent
storage.

Exit:

- this is an active runtime terrain quality gate;
- a clean compact runtime state is used for each engine run;
- carve and construct edits commit inside the frame and millisecond budgets;
- terrain settles without pending retirements or render fade/blink resources;
- authoritative samples match the edited density/material values before reload;
- `world.wtedit` is created and remains inside the compact storage budget;
- a fresh scene reload replays both edits from storage;
- active render and collision resources remain bounded to 25;
- dense near-2K source/world files are not reintroduced.

Boundary:

- G34 proves edit latency and persistence for the current compact CPU/native
  terrain path. It does not claim final terrain art, seamless dynamic LOD,
  GPU/compute generation, fluids, biomes, vegetation, buildings, multiplayer,
  or a separate game repository.

Run:

```console
python tools/g34_edit_latency_persistence_quality.py
```

Expected markers:

```text
WT_VALIDATION_G34_CONTRACT_PASS implementation=edit_latency_persistence_quality
WT_VALIDATION_G34_EDIT_LATENCY_PERSISTENCE_PASS profile=g19_compact_2k_on_demand edits=2 replayed=2 max_commit_frames=... max_settle_frames=... max_commit_ms=... max_settle_ms=... journal_bytes=... max_render_resources=25 max_collision_resources=25 dense_world_files=0
WT_VALIDATION_G34_EDIT_LATENCY_PERSISTENCE_SMOKE_PASS profile=g19_compact_2k_on_demand engines=... edits=2 replayed=2 max_commit_frames=... max_settle_frames=... max_commit_ms=... max_settle_ms=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g34_edit_latency_persistence_quality/g34_edit_latency_persistence_quality_report.json
```
