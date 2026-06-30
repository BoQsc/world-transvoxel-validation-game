# G29 - Compact 2K human-ready handoff

Status: complete when `WT_VALIDATION_G29_CONTRACT_PASS` and
`WT_VALIDATION_G29_COMPACT_2K_HUMAN_READY_HANDOFF_PASS` both pass.

G29 prepares the human-ready compact 2K handoff project. G27 proves the
scene-level full-terrain behavior and G28 proves the normal launch path. G29
creates the actual generated project that a human should open, with human input
enabled and a local `HUMAN_REVIEW.md` file inside the generated project.

Exit:

- No human validation is requested until this gate passes;
- the generated handoff project is separate from automation-preflight projects;
- the scene is pinned to `g19_compact_2k_on_demand`;
- `human_input_enabled = true` is present in the generated handoff scene;
- `human_input_enabled = false` is absent from the generated handoff scene;
- `project.godot` launches `res://scenes/validation_playtest.tscn`;
- current G27 and G28 prerequisite reports are present and match the current
  addon source commits;
- Godot import passes for the generated handoff project;
- a local `HUMAN_REVIEW.md` file records controls, expected baseline, source
  commits, and known boundaries;
- dense near-2K source/world files are not reintroduced.

Run:

```console
python tools/validate_g29_contract.py
python tools/g29_compact_2k_human_ready_handoff.py --skip-build
```

Expected markers:

```text
WT_VALIDATION_G29_CONTRACT_PASS implementation=compact_2k_human_ready_handoff
WT_VALIDATION_G29_COMPACT_2K_HUMAN_READY_HANDOFF_PASS profile=g19_compact_2k_on_demand project=... scene=res://scenes/validation_playtest.tscn human_input=true imported_engines=2 review=HUMAN_REVIEW.md dense_world_files=0 report=artifacts/g29_compact_2k_human_ready_handoff/g29_compact_2k_human_ready_handoff_report.json
```

Boundary:

- this prepares the current human review artifact; it does not mean the human
  has approved terrain art, seamless dynamic LOD, water, biomes, vegetation,
  buildings, GPU compute, multiplayer, or a separate game repository.
