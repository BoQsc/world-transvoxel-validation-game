# World Transvoxel Validation Game

Small Godot validation project for `world-transvoxel-terrain`.

Status: G0 install/run validation complete. G1 human-visible playtest
confirmation is next. This repository is not the sandbox and not a production
game. Its job is to import `world-transvoxel` and `world-transvoxel-terrain` as
addons, run the smallest real integration path, and report every failure back to
the addon repositories instead of hiding workarounds here.

## Boundary

- `world-transvoxel` remains the low-level MIT-backed Transvoxel addon.
- `world-transvoxel-terrain` remains the reusable terrain addon.
- This repository validates game-project integration only.
- Do not fork or copy `world-transvoxel-sandbox`.
- Do not add production gameplay systems, fluids, planets, vegetation, GPU
  compute, or 0BSD backend replacement here.

## Validate

The committed repository does not vendor addon source. The validation tool
builds an ignored Godot project under `artifacts/validation_project` from sibling
local repos.

```console
python tools/validate_g0_contract.py
python tools/g0_install_run_smoke.py
```

Expected marker:

```text
WT_VALIDATION_G0_CONTRACT_PASS implementation=install_run_validation_scaffold next=human_visible_playtest_confirmation
WT_VALIDATION_G0_SMOKE_PASS engines=2 report=artifacts/g0_install_run_smoke/g0_install_run_smoke_report.json
```

## Human-visible playtest

After running the smoke command, open:

```text
artifacts/validation_project/project.godot
```

Run `res://scenes/validation_playtest.tscn`. The scene auto-starts the addon
reference terrain world, submits one viewer update, and shows the addon debug
overlay.
