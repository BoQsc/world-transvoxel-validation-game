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
confirmation remains pending. G1 is not the final playable-world gate.

Exit:

- open the generated validation project;
- run `res://scenes/validation_playtest.tscn`;
- confirm that the scene shows more than a gray rectangle: terrain or an
  explicit failure status, orientation markers, and validation status text;
- confirm that a playable character and follow camera are present;
- confirm programmatically that the visible terrain mesh has nonzero triangle
  geometry, terrain collision resources, and scripted player movement;
- keep a captured viewport image as automated evidence before asking for human
  confirmation;
- confirm whether there are obvious orientation, artifact, popping,
  missing-backside, or performance issues;
- record failures as addon work, not as hidden validation-game workarounds.

## G2 - First-person playable baseline

Status: complete by `WT_VALIDATION_G2_CONTRACT_PASS` and
`WT_VALIDATION_G2_SMOKE_PASS`. G1 human-visible rerun confirmation remains
pending, but the automated G2 gate is not blocked by that human confirmation.

Exit:

- first-person camera and crosshair are present for human play;
- flat terrain remains the default reproducible baseline;
- generated project supports player walk/jump against terrain collision;
- automated tests disable human input and prove scripted movement;
- visual capture shows terrain and player/play HUD evidence.

## G3 - Terrain generation modes

Status: complete by `WT_VALIDATION_G3_CONTRACT_PASS` and
`WT_VALIDATION_G3_SMOKE_PASS`.

Exit:

- flat baseline remains selectable;
- mountain/large-terrain profile exists with deterministic seed;
- chunking/streaming counters prove bounded work and cold idle;
- captures cover flat and mountain modes.

## G4 - Terrain edit interaction

Status: complete by `WT_VALIDATION_G4_CONTRACT_PASS` and
`WT_VALIDATION_G4_SMOKE_PASS`.

Exit:

- first-person dig/place affordance exists;
- edit shape policy is explicit, with standard sphere/box and optional alternate
  shapes only when justified;
- edit latency and restore/recovery behavior are measured;
- automated tests prove terrain and collision update after edits.

## G5 - Material and performance baseline

Status: active next.

Exit:

- small texture/material path exists without hiding performance cost;
- baseline watt/performance behavior is measured;
- optional GPU burst/full-GPU paths remain decisions, not assumptions.
