# G15 - G14 scale telemetry guard

Status: complete when `WT_VALIDATION_G15_CONTRACT_PASS` and
`WT_VALIDATION_G15_G14_SCALE_TELEMETRY_PASS` both pass.

G15 locks the evidence from the G14 64 by 64 generated terrain milestone before
the project attempts a larger generated fixture. It does not replace the G14
Godot runtime smoke; it validates the saved G14 report and source artifacts so
scale-up decisions are based on explicit measurements.

Exit:

- the G14 report still describes `g14_generated_64x64`;
- the fixture still has 4096 generated pages and source revision `146400`;
- generated source files have the expected streamed sizes:
  `density.f32 = 275298660` bytes and `materials.u16 = 137649330` bytes;
- `keys.txt` contains exactly the 64 by 64 chunk-key set;
- vertical coverage margins meet the G13 lower and upper margin policy;
- two engine runtime markers are present from the G14 smoke;
- runtime markers keep the playable scene at no more than 25 active resources
  for render and collision;
- edit replacement happened during runtime validation.

Commands:

```console
python tools/validate_g15_contract.py
python tools/g15_g14_scale_telemetry_guard.py
```

Expected markers:

```text
WT_VALIDATION_G15_CONTRACT_PASS implementation=g14_scale_telemetry_guard
WT_VALIDATION_G15_G14_SCALE_TELEMETRY_PASS pages=4096 engines=2 density_bytes=275298660 materials_bytes=137649330 max_render_resources=25 max_collision_resources=25 report=artifacts/g15_g14_scale_telemetry/g15_g14_scale_telemetry_report.json
```

Boundary:

- this is not a new terrain feature;
- this is not a human visual verification gate;
- this is the automated evidence lock that must stay green before a 128 by 128
  generated fixture or full 2K generated step is attempted.
