# G22 - Exact compact handoff runtime proof

Status: complete when `WT_VALIDATION_G22_CONTRACT_PASS` and
`WT_VALIDATION_G22_EXACT_COMPACT_HANDOFF_RUNTIME_SMOKE_PASS` both pass.

G22 runs the exact compact G21 handoff project before asking for human visual
review. Import-only readiness is not enough for this gate.

Required behavior:

- the project is prepared by the same G21 compact handoff path;
- `validation_playtest.tscn` remains pinned to `g19_compact_2k_on_demand`;
- automated runtime disables human input from startup;
- the exact handoff project is imported, launched through Godot, and exercised;
- runtime proof covers origin, center, and far-corner compact 2K positions;
- the test captures PNG evidence before human review;
- scripted movement, carve, and construct/place all commit;
- settled windows report `render_fading_resources = 0`;
- settled windows report `pending_chunk_retirements = 0`;
- active render and collision resources stay within the 25-resource budget;
- no dense source/world files are reintroduced.

Validation:

```text
python tools/validate_g22_contract.py
python tools/g22_exact_compact_handoff_runtime_proof.py --skip-build
```

Expected marker:

```text
WT_VALIDATION_G22_CONTRACT_PASS implementation=exact_compact_handoff_runtime_proof
WT_VALIDATION_G22_EXACT_COMPACT_HANDOFF_RUNTIME_PASS profile=g19_compact_2k_on_demand captures=3 pages=16384 max_render_resources=25 max_collision_resources=25 edit_replacements=... construct_verified=1 pending_retirements=0 render_fading_resources=0 dense_world_files=0
WT_VALIDATION_G22_EXACT_COMPACT_HANDOFF_RUNTIME_SMOKE_PASS engines=2 captures=... max_file_bytes=... total_bytes=... max_engine_seconds=... report=artifacts/g22_exact_compact_handoff_runtime_proof/g22_exact_compact_handoff_runtime_proof_report.json
```

Boundary:

- G22 proves that the current compact human handoff artifact actually runs and
  produces automated visual/runtime evidence.
- G22 still does not claim final terrain art, dynamic LOD seam quality,
  GPU/compute generation, water, biomes, vegetation, buildings, multiplayer, or
  game repository readiness.
