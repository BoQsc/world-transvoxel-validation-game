# G21 - Compact 2K human visual handoff

Status: complete when `WT_VALIDATION_G21_CONTRACT_PASS` and
`WT_VALIDATION_G21_COMPACT_2K_HUMAN_HANDOFF_READY` both pass.

G21 prepares the compact G19 near-2K project for human visual playtesting. This
replaces the old G17 dense-stress handoff for current terrain review.

Required behavior:

- the saved G19 report exists and still proves two timed engine runs;
- the G20 resolution gate can validate the same compact report;
- the generated project is composed from the current local addon sources;
- `validation_playtest.tscn` is pinned to `g19_compact_2k_on_demand`;
- no dense G19 world/source files are created;
- Godot import passes before asking a human to open the project;
- the report records `human_confirmation` as pending.

Validation:

```text
python tools/validate_g21_contract.py
python tools/g21_compact_2k_human_handoff.py --import-project
```

Expected marker:

```text
WT_VALIDATION_G21_CONTRACT_PASS implementation=compact_2k_human_handoff
WT_VALIDATION_G21_COMPACT_2K_HUMAN_HANDOFF_READY profile=g19_compact_2k_on_demand imported=true project=... scene=res://scenes/validation_playtest.tscn fullscreen=false report=artifacts/g21_compact_2k_human_handoff/g21_compact_2k_human_handoff_report.json
```

Boundary:

- G21 is human visual handoff only, not a new terrain algorithm milestone.
- Human confirmation remains pending until a person actually runs and reviews
  the project.
- Final terrain art, dynamic LOD seams, GPU generation, fluids, biomes, and
  game repository readiness remain outside this gate.
