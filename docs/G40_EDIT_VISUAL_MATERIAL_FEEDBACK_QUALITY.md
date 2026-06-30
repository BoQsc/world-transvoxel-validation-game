# G40 - Edit visual material feedback quality

Status: complete when `WT_VALIDATION_G40_CONTRACT_PASS` and
`WT_VALIDATION_G40_EDIT_VISUAL_MATERIAL_FEEDBACK_SMOKE_PASS` both pass.

G40 is the active runtime terrain quality gate for edit visual material feedback
quality. It captures a focused terrain patch before and after real carve and
construct edits, verifies the rendered image changes, verifies material
application stabilizes, and confirms backend authoritative samples match the
edits.

Exit:

- the compact 2K edit site streams and settles before capture;
- the before and after captures contain enough colored terrain samples;
- two real edits commit through the terrain interactor;
- authoritative samples match the edited density/material values;
- the after-edit image differs from the before-edit image above threshold;
- material auto-application stabilizes after the edit replacements;
- active render and collision resources remain bounded to 25;
- dense near-2K source/world files are not reintroduced.

Boundary:

- G40 detects missing player-facing edit feedback for the current compact
  CPU/native terrain path. It does not claim final terrain art, seamless dynamic
  LOD, GPU/compute generation, fluids, biomes, vegetation, buildings,
  multiplayer, or a separate game repository.

Run:

```console
python tools/g40_edit_visual_material_feedback_quality.py
```

Expected markers:

```text
WT_VALIDATION_G40_CONTRACT_PASS implementation=edit_visual_material_feedback_quality
WT_VALIDATION_G40_EDIT_VISUAL_MATERIAL_FEEDBACK_PASS profile=g19_compact_2k_on_demand edits=2 changed_samples=... before_colored_samples=... after_colored_samples=... material_auto_apply_delta=... max_commit_frames=... max_settle_frames=... max_render_resources=25 max_collision_resources=25 edit_replacement_delta=... dense_world_files=0
WT_VALIDATION_G40_EDIT_VISUAL_MATERIAL_FEEDBACK_SMOKE_PASS profile=g19_compact_2k_on_demand engines=... edits=2 min_changed_samples=... max_commit_frames=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g40_edit_visual_material_feedback_quality/g40_edit_visual_material_feedback_quality_report.json
```
