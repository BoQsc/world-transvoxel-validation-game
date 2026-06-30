# G44 - Edit policy and shape quality

Status: complete when `WT_VALIDATION_G44_CONTRACT_PASS` and
`WT_VALIDATION_G44_EDIT_POLICY_SHAPE_SMOKE_PASS` both pass.

G44 is the runtime terrain quality gate for edit policy and shape quality.
It locks the validation default edit policy before broader addon API work:
carve/place use a sphere brush, dig and place radius are 1.8, place material is
4, and alternate shape toggles are explicitly disabled in this validation layer
until the later terrain addon API contract gate.

Exit:

- the compact 2K scene reaches playable ready state with human input disabled;
- the terrain interactor exposes an edit policy summary;
- default brush shape is `sphere`;
- dig radius and place radius are both `1.8`;
- place material id is `4`;
- alternate shape toggles are explicitly disabled for this validation gate;
- at least six repeated carve/construct edits commit through the terrain
  interactor;
- center and inside-radius authoritative samples match the expected carve/place
  density and material behavior;
- outside-radius authoritative samples remain unchanged immediately after each
  edit;
- edit commit and settle frames remain within budget;
- active resources return to the 25-resource compact detail window;
- render fade/blink resources and pending retirements remain zero after each
  edit settles;
- dense near-2K source/world files are not reintroduced.

Boundary:

- G44 proves the current default sphere edit policy and repeated edit shape
  behavior. It does not claim full public terrain editing API stability, final
  mining design, non-sphere production brushes, fluids, biomes, vegetation,
  buildings, multiplayer, or a separate game repository.

Run:

```console
python tools/g44_edit_policy_shape_quality.py
```

Expected markers:

```text
WT_VALIDATION_G44_CONTRACT_PASS implementation=edit_policy_shape_quality
WT_VALIDATION_G44_EDIT_POLICY_SHAPE_PASS profile=g19_compact_2k_on_demand default_shape=sphere dig_radius=1.800 place_radius=1.800 place_material=4 alternate_shape_toggles=false edits=6 inside_samples=... outside_unchanged_samples=... max_commit_frames=... max_settle_frames=... edit_replacement_delta=... max_render_resources=25 max_collision_resources=25 max_active_records=25 max_pending_retirements=0 max_render_fading_resources=0 dense_world_files=0
WT_VALIDATION_G44_EDIT_POLICY_SHAPE_SMOKE_PASS profile=g19_compact_2k_on_demand engines=... edits=6 inside_samples=... outside_unchanged_samples=... max_commit_frames=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g44_edit_policy_shape_quality/g44_edit_policy_shape_quality_report.json
```
