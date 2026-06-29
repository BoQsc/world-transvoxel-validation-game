# World Transvoxel Validation Game

Small Godot validation project for `world-transvoxel-terrain`.

Status: G0 install/run validation complete. G1 playable terrain/player guard
passes programmatically; G2 first-person flat baseline passes programmatically;
G3 flat/mountain generation modes pass programmatically; G4 terrain edit
interaction passes programmatically; G5 material/performance baseline passes
programmatically; G6 8 by 8 multi-chunk profile-selectable playable world passes
programmatically. Human visual verification is the next boundary. This repository is not the
sandbox and not a
production game. Its job is to import `world-transvoxel` and
`world-transvoxel-terrain` as addons, run real game-facing integration paths,
and report every failure back to the addon repositories instead of hiding
workarounds here.

## Boundary

- `world-transvoxel` remains the low-level MIT-backed Transvoxel addon.
- `world-transvoxel-terrain` remains the reusable terrain addon.
- This repository validates game-project integration only.
- Do not fork or copy `world-transvoxel-sandbox`.
- Do not add production gameplay systems, fluids, planets, vegetation, GPU
  compute, or 0BSD backend replacement here before their contracts exist.
- The larger target is tracked in
  [`docs/PLAYABLE_WORLD_TARGET.md`](docs/PLAYABLE_WORLD_TARGET.md).

## Validate

The committed repository does not vendor addon source. The validation tools
build ignored Godot projects under `artifacts/.../project` from sibling local
repos.

```console
python tools/validate_g0_contract.py
python tools/root_project_safe_import.py
python tools/g0_install_run_smoke.py
python tools/validate_playable_world_target.py
python tools/validate_g1_contract.py
python tools/g1_visible_playtest_smoke.py
python tools/g1_visual_capture.py --windowed
python tools/validate_g2_contract.py
python tools/g2_first_person_baseline_smoke.py
python tools/validate_g3_contract.py
python tools/g3_generation_modes_smoke.py --windowed
python tools/validate_g4_contract.py
python tools/g4_edit_interaction_smoke.py
python tools/validate_g5_contract.py
python tools/g5_material_performance_smoke.py --windowed
python tools/validate_g6_contract.py
python tools/g6_profile_selectable_playable_world_smoke.py --windowed
python tools/human_input_capture_smoke.py
python tools/prepare_human_playtest.py --profile flat_large --reuse-bake
```

Expected marker:

```text
WT_VALIDATION_G0_CONTRACT_PASS implementation=install_run_validation_scaffold next=human_visible_playtest_confirmation
WT_VALIDATION_ROOT_PROJECT_SAFE_IMPORT_PASS engines=2 report=artifacts/root_project_safe_import/root_project_safe_import_report.json
WT_VALIDATION_G0_SMOKE_PASS engines=2 report=artifacts/g0_install_run_smoke/g0_install_run_smoke_report.json
WT_VALIDATION_PLAYABLE_WORLD_TARGET_PASS next=human_visual_verification
WT_VALIDATION_G1_CONTRACT_PASS implementation=human_visible_playtest_guard next=human_rerun_confirmation
WT_VALIDATION_G1_SMOKE_PASS engines=2 report=artifacts/g1_visible_playtest/g1_visible_playtest_report.json
WT_VALIDATION_G1_VISUAL_CAPTURE_RUN_PASS engines=2 report=artifacts/g1_visual_capture/g1_visual_capture_report.json
WT_VALIDATION_G2_CONTRACT_PASS implementation=first_person_flat_baseline next=g3_terrain_generation_modes
WT_VALIDATION_G2_SMOKE_PASS engines=2 report=artifacts/g2_first_person_baseline/g2_first_person_baseline_report.json
WT_VALIDATION_G3_CONTRACT_PASS implementation=flat_and_mountain_baked_generation_modes next=g4_terrain_edit_interaction
WT_VALIDATION_G3_SMOKE_PASS profiles=2 engines=2 report=artifacts/g3_generation_modes/g3_generation_modes_report.json
WT_VALIDATION_G4_CONTRACT_PASS implementation=first_person_edit_interaction next=g5_material_performance_baseline
WT_VALIDATION_G4_SMOKE_PASS engines=2 report=artifacts/g4_edit_interaction/g4_edit_interaction_report.json
WT_VALIDATION_G5_CONTRACT_PASS implementation=materialized_performance_baseline next=g6_profile_selectable_playable_world
WT_VALIDATION_G5_SMOKE_PASS engines=2 report=artifacts/g5_material_performance/g5_material_performance_report.json
WT_VALIDATION_G6_CONTRACT_PASS implementation=profile_selectable_playable_world next=human_visual_verification
WT_VALIDATION_G6_SMOKE_PASS profiles=2 engines=2 report=artifacts/g6_profile_selectable_playable_world/g6_profile_selectable_playable_world_report.json
WT_VALIDATION_HUMAN_INPUT_CAPTURE_SMOKE_PASS engines=2 report=artifacts/human_input_capture/human_input_capture_report.json
WT_VALIDATION_HUMAN_PLAYTEST_READY profile=flat_large project=... scene=res://scenes/validation_playtest.tscn launch=false fullscreen=false report=artifacts/human_playtest/human_playtest_report.json
```

## Human-visible playtest

Do not open the repository-root `project.godot` for terrain playtesting. The
root project is only a safe notice project and intentionally does not vendor
addons.

After running the G1 smoke command, open:

```text
artifacts/g1_visible_playtest/project/project.godot
```

After running the G1 visual capture command, the newest generated project is:

```text
artifacts/g1_visual_capture/project/project.godot
```

For current human visual testing of the 8 by 8 multi-chunk flat fixture, prepare
the dedicated generated project instead of manually patching ignored artifacts:

```console
python tools/prepare_human_playtest.py --profile flat_large --reuse-bake --import-project
```

Then open:

```text
artifacts/human_playtest/project/project.godot
```

Run `res://scenes/validation_playtest.tscn`. The scene auto-starts the addon
reference terrain world, submits the selected profile's viewer update set, adds
a small WASD/jump playable character with a first-person camera and crosshair,
shows orientation markers, and shows a validation status overlay below the addon
debug overlay. Left mouse carves terrain and right mouse places/constructs
terrain through the terrain addon edit bridge. The automated G1/G4/G6 guards
check nonzero terrain triangle geometry, terrain collision resources, player
presence, crosshair presence, scripted player movement, edit commits,
replacement metrics, and sample updates. A gray rectangle alone is not an
acceptable G1 result.
