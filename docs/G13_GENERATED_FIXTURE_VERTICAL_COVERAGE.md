# G13 - Generated fixture vertical coverage guard

Status: complete when `WT_VALIDATION_G13_CONTRACT_PASS` and
`WT_VALIDATION_G13_GENERATED_FIXTURE_VERTICAL_COVERAGE_PASS` both pass.

G12 exposed a fixture-generation failure mode: a generated height field can
approach or exceed the active vertical chunk boundary while the runtime still
reports render/collision resources as ready. That can make the playable scene
fall through terrain even though streaming counts look correct. G13 turns that
failure into an automated generated fixture vertical coverage guard.

Exit:

- generated dense fixtures compute surface min/max height before bake;
- the computed surface must stay inside the active vertical chunk with
  `REQUIRED_LOWER_MARGIN` and `REQUIRED_UPPER_MARGIN`;
- G11, G12, G14, and G16 reports include `vertical_coverage` metadata;
- G11, G12, G14, and G16 reused fixtures must match the expected
  `source_revision`;
- stale generated fixtures fail before Godot instead of silently reusing an
  old height field;
- this milestone is a safety gate for future larger generated terrain steps, not
  a new terrain-size milestone.

Required commands:

```text
python tools/validate_g13_contract.py
python tools/g13_generated_fixture_vertical_coverage_smoke.py
```

Expected markers:

```text
WT_VALIDATION_G13_CONTRACT_PASS implementation=generated_fixture_vertical_coverage_guard
WT_VALIDATION_G13_GENERATED_FIXTURE_VERTICAL_COVERAGE_PASS profiles=4 active_y=0.0..16.0 required_lower_margin=1.00 required_upper_margin=0.75 report=artifacts/g13_generated_fixture_vertical_coverage/g13_generated_fixture_vertical_coverage_report.json
```
