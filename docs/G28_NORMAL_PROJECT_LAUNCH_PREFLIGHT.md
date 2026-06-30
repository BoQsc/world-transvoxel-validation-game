# G28 - Normal project launch preflight

Status: complete when `WT_VALIDATION_G28_CONTRACT_PASS` and
`WT_VALIDATION_G28_NORMAL_PROJECT_LAUNCH_SMOKE_PASS` both pass.

G28 is the normal project launch preflight. It proves the generated handoff
project starts through its normal
`project.godot` launch path. G27 checks the handoff scene with a runtime script;
G28 closes the remaining gap by launching the generated project normally with
`run/main_scene="res://scenes/validation_playtest.tscn"`.

Exit:

- No human validation is requested until this gate passes;
- the generated project's normal main scene is `validation_playtest.tscn`;
- the scene is pinned to `g19_compact_2k_on_demand`;
- automation disables human input from startup in the generated scene file;
- Godot is launched with `--path`, not `--script`;
- the normal launch reaches `WT_VALIDATION_PLAYTEST_READY` within the 30 second
  load-to-ready ceiling;
- the normal launch logs no Godot errors;
- dense near-2K source/world files are not reintroduced.

Run:

```console
python tools/validate_g28_contract.py
python tools/g28_normal_project_launch_preflight.py --skip-build
```

Expected markers:

```text
WT_VALIDATION_G28_CONTRACT_PASS implementation=normal_project_launch_preflight
WT_VALIDATION_G28_NORMAL_PROJECT_LAUNCH_PASS profile=g19_compact_2k_on_demand main_scene=res://scenes/validation_playtest.tscn human_input=false engines=2 max_ready_seconds=... dense_world_files=0
WT_VALIDATION_G28_NORMAL_PROJECT_LAUNCH_SMOKE_PASS engines=2 max_ready_seconds=... report=artifacts/g28_normal_project_launch_preflight/g28_normal_project_launch_preflight_report.json
```

Boundary:

- this proves normal generated-project startup reaches the playable validation
  scene; it does not replace G27's first-person capture/edit preflight and does
  not claim final terrain art, seamless dynamic LOD, GPU/compute generation,
  fluids, biomes, vegetation, buildings, multiplayer, or a separate game
  repository.
