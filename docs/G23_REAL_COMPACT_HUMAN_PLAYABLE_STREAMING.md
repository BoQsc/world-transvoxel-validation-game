# G23 - Real compact human-playable streaming

Status: complete when `WT_VALIDATION_G23_CONTRACT_PASS` and
`WT_VALIDATION_G23_REAL_COMPACT_HUMAN_PLAYABLE_STREAMING_SMOKE_PASS` both pass.

G23 fixes the failed human handoff boundary. The compact 2K project must be a
real player-driven playtest, not a static startup viewer plus autonomous backend
teleports.

Required behavior:

- `g19_compact_2k_on_demand` starts inside the map, not on the clipped origin
  edge;
- startup settles to a 25-resource active window around the player;
- human input remains enabled in the playtest scene;
- mouse motion changes the first-person camera through the scene input path;
- player movement drives terrain viewer updates;
- the active terrain window follows the moved player and settles;
- left click carves through the terrain interactor input path;
- right click constructs/places through the terrain interactor input path;
- settled runtime reports `render_fading_resources = 0`;
- settled runtime reports `pending_chunk_retirements = 0`;
- no dense source/world files are reintroduced.

Validation:

```text
python tools/validate_g23_contract.py
python tools/g23_real_compact_human_playable_streaming.py --skip-build
```

Expected marker:

```text
WT_VALIDATION_G23_CONTRACT_PASS implementation=real_compact_human_playable_streaming
WT_VALIDATION_G23_REAL_COMPACT_HUMAN_PLAYABLE_STREAMING_PASS profile=g19_compact_2k_on_demand initial_resources=25 viewer_updates_delta=... player_motion=... camera_delta=... click_edits=2 pending_retirements=0 render_fading_resources=0 dense_world_files=0
WT_VALIDATION_G23_REAL_COMPACT_HUMAN_PLAYABLE_STREAMING_SMOKE_PASS engines=2 max_engine_seconds=... report=artifacts/g23_real_compact_human_playable_streaming/g23_real_compact_human_playable_streaming_report.json
```

Boundary:

- G23 proves the current compact validation-game project is actually
  human-playable enough for later visual review.
- G23 still does not claim final terrain art, dynamic LOD seam quality,
  GPU/compute generation, water, biomes, vegetation, buildings, multiplayer, or
  game repository readiness.
