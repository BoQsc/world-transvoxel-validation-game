# G7 Human Visual Verification

Status: active. Automated handoff prep is complete when
`WT_VALIDATION_G7_CONTRACT_PASS` and `WT_VALIDATION_G7_HANDOFF_READY` pass.
Final human acceptance remains pending until both profiles are visually reviewed.

## What this gate proves

G7 is the first explicit human-review gate after the automated playable-world
checks. It does not replace technical validation; it makes the human review
reproducible:

- `flat_8x8` and `mountain_8x8` each get a separate generated Godot project;
- each generated `res://scenes/validation_playtest.tscn` is pinned to the
  intended profile, so review does not depend on manual ignored-artifact edits;
- Godot import is run before handoff when `--import-projects` is used;
- source defaults still remain compatible with G2, where `flat_baseline` is the
  default automated first-person baseline.

Expected markers:

```text
WT_VALIDATION_G7_CONTRACT_PASS implementation=human_visual_handoff next=human_profile_review
WT_VALIDATION_G7_HANDOFF_READY profiles=2 imported=true report=artifacts/g7_human_visual_handoff/g7_human_visual_handoff_report.json
```

## Run

```console
python tools/validate_g7_contract.py
python tools/g7_human_visual_handoff.py --reuse-bake --import-projects
```

Then open the generated projects:

```text
artifacts/g7_human_visual_handoff/flat_8x8/project/project.godot
artifacts/g7_human_visual_handoff/mountain_8x8/project/project.godot
```

Run `res://scenes/validation_playtest.tscn` in each project.

## Human checklist

Record any failure as addon work, not as a validation-game workaround:

- terrain is not upside down;
- terrain is more than a gray rectangle;
- terrain does not visibly blink during dig/place;
- chunk pieces do not rapidly disappear and reappear while moving;
- no obvious diagonal seam/artifact dominates the surface;
- first-person mouse capture remains usable after click/escape recapture;
- player can walk and jump against terrain collision;
- left mouse carves terrain and right mouse places terrain;
- status overlay reaches READY and reports the expected profile.

## Not claimed

G7 does not claim final production readiness, 2000×2000 block exploration,
seamless dynamic LOD, water/lava, vegetation, buildings, multiplayer,
compute-shader acceleration, production art, or final performance budgets.
