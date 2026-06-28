# World Transvoxel Validation Game Implementation Charter

Status: canonical project direction for the validation game repository.

Current phase: G0 install/run validation complete. Next phase is G1
human-visible playtest confirmation.

This repository exists only because `world-transvoxel-terrain` A6 approved a
separate validation game repository when explicitly requested.

## Rules

- Validate game-project integration of `world-transvoxel` plus
  `world-transvoxel-terrain`.
- Keep addon complexity inside the addon repositories.
- Keep this repo small enough that failures are easy to attribute.
- Do not copy or fork `world-transvoxel-sandbox`.
- Do not vendor addon source in committed history during G0; compose an ignored
  local validation project from sibling repos.
- Use GDScript only for scene scaffolding, smoke harnesses, and input/debug glue.
- Keep production game systems out of scope until the install/run path is proven.

## G0 - Install/run validation scaffold

G0 is complete when:

- this repository has a minimal Godot project;
- `tools/compose_validation_project.py` creates ignored generated projects under
  `artifacts/.../project`;
- the composed project contains `world-transvoxel`, `world-transvoxel-terrain`,
  validation scenes, validation tests, and the official production lifecycle
  fixture;
- `python tools/validate_g0_contract.py` passes;
- `python tools/g0_install_run_smoke.py` passes on discovered Godot engines;
- the generated project has a human-visible playtest scene for manual review.

G0 does not claim terrain quality, production performance, seamless gameplay,
large-map exploration, or final game readiness.

## G1 - Human-visible playtest confirmation

G1 is complete when:

- generated projects open from the relevant `artifacts/.../project/project.godot`;
- `res://scenes/validation_playtest.tscn` starts the terrain world;
- the debug overlay is visible;
- the automated guard proves nonzero terrain mesh triangle count, not just a
  node name;
- any visual, interaction, terrain-orientation, popping, artifact, or performance
  issue found by human review is recorded as follow-up addon work rather than
  hidden inside this validation repo.
