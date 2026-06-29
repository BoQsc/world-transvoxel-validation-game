# G17 - Generated 128x128 human visual handoff

Status: complete when `WT_VALIDATION_G17_CONTRACT_PASS` and
`WT_VALIDATION_G17_GENERATED_128X128_HUMAN_HANDOFF_READY` both pass.

G17 prepares the G16 near-2K generated project for human visual playtesting.
This is not a new terrain-size milestone. It is the handoff gate after the
automated G16 runtime proof.

Exit:

- the saved G16 runtime report exists and still proves two engine runs;
- the generated project is composed from the current local addons;
- the G16 baked world is copied into the generated project;
- `validation_playtest.tscn` is pinned to `g16_generated_128x128`;
- Godot import passes before asking a human to open the project;
- the report records `human_confirmation` as pending.

Commands:

```console
python tools/validate_g17_contract.py
python tools/g17_generated_128x128_human_handoff.py --import-project
```

Expected markers:

```text
WT_VALIDATION_G17_CONTRACT_PASS implementation=generated_128x128_human_handoff
WT_VALIDATION_G17_GENERATED_128X128_HUMAN_HANDOFF_READY profile=g16_generated_128x128 imported=true project=... scene=res://scenes/validation_playtest.tscn fullscreen=false report=artifacts/g17_generated_128x128_human_handoff/g17_generated_128x128_human_handoff_report.json
```
