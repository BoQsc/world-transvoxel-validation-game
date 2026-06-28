# World Transvoxel Validation Game

Small Godot validation project for `world-transvoxel-terrain`.

Status: G0 install/run validation complete. G1 playable terrain/player guard
passes programmatically; larger playable-world validation remains active. This
repository is not the sandbox and not a production game. Its job is to import
`world-transvoxel` and `world-transvoxel-terrain` as addons, run real game-facing
integration paths, and report every failure back to the addon repositories
instead of hiding workarounds here.

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
```

Expected marker:

```text
WT_VALIDATION_G0_CONTRACT_PASS implementation=install_run_validation_scaffold next=human_visible_playtest_confirmation
WT_VALIDATION_ROOT_PROJECT_SAFE_IMPORT_PASS engines=2 report=artifacts/root_project_safe_import/root_project_safe_import_report.json
WT_VALIDATION_G0_SMOKE_PASS engines=2 report=artifacts/g0_install_run_smoke/g0_install_run_smoke_report.json
WT_VALIDATION_PLAYABLE_WORLD_TARGET_PASS next=g2_first_person_baseline
WT_VALIDATION_G1_CONTRACT_PASS implementation=human_visible_playtest_guard next=human_rerun_confirmation
WT_VALIDATION_G1_SMOKE_PASS engines=2 report=artifacts/g1_visible_playtest/g1_visible_playtest_report.json
WT_VALIDATION_G1_VISUAL_CAPTURE_RUN_PASS engines=2 report=artifacts/g1_visual_capture/g1_visual_capture_report.json
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

Run `res://scenes/validation_playtest.tscn`. The scene auto-starts the addon
reference terrain world, submits one viewer update, adds a small WASD/jump
playable character with a first-person camera and crosshair, shows orientation
markers, and shows a validation status overlay below the addon debug overlay.
The automated G1 guard also checks nonzero terrain triangle geometry, terrain
collision resources, player presence, crosshair presence, and scripted player
movement. A gray rectangle alone is not an acceptable G1 result.
