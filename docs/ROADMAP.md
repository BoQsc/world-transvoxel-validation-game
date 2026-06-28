# Roadmap

## G0 - Install/run validation scaffold

Status: complete by `WT_VALIDATION_G0_SMOKE_PASS`.

Exit:

- compose a fresh ignored Godot project from sibling `world-transvoxel` and
  `world-transvoxel-terrain` repos;
- run one headless install/run smoke;
- provide one human-visible playtest scene;
- keep all discovered addon failures visible and attributable.

Not in scope:

- production gameplay systems;
- broad open-world exploration;
- GPU compute;
- water/lava, planets, vegetation, building blocks, or structural stability;
- 0BSD backend replacement.

## G1 - Human-visible playtest confirmation

Status: active. Automated guard passes by `WT_VALIDATION_G1_SMOKE_PASS`; visual
capture passes by `WT_VALIDATION_G1_VISUAL_CAPTURE_RUN_PASS`; human rerun
confirmation remains pending.

Exit:

- open the generated validation project;
- run `res://scenes/validation_playtest.tscn`;
- confirm that the scene shows more than a gray rectangle: terrain or an
  explicit failure status, orientation markers, and validation status text;
- confirm programmatically that the visible terrain mesh has nonzero triangle
  geometry;
- keep a captured viewport image as automated evidence before asking for human
  confirmation;
- confirm whether there are obvious orientation, artifact, popping,
  missing-backside, or performance issues;
- record failures as addon work, not as hidden validation-game workarounds.
