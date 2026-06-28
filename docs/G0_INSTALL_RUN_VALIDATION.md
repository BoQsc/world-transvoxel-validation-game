# G0 Install/Run Validation

Status: complete.

Markers:

```text
WT_VALIDATION_G0_CONTRACT_PASS implementation=install_run_validation_scaffold next=human_visible_playtest_confirmation
WT_VALIDATION_G0_GODOT_PASS scene=terrain_world_started viewer=settled cold_idle=stable implementation=install_run_validation
WT_VALIDATION_G0_SMOKE_PASS engines=2 report=artifacts/g0_install_run_smoke/g0_install_run_smoke_report.json
```

## Purpose

G0 proves a separate Godot project can compose the two addon repositories, start
the terrain world through `world-transvoxel-terrain`, submit one viewer update,
observe a ready origin chunk, and settle cold.

The first successful run used:

- `world-transvoxel` commit `a84256e`;
- `world-transvoxel-terrain` commit `2219a0f`;
- Godot 4.6.3 and Godot 4.7.

## Boundary

G0 does not prove final terrain visuals or production performance. It only proves
the install/run path that must exist before larger game validation is meaningful.
