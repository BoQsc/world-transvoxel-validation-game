# G19 - Compact 2K on-demand procedural streaming

Status: complete when `WT_VALIDATION_G19_CONTRACT_PASS` and
`WT_VALIDATION_G19_COMPACT_2K_ON_DEMAND_SMOKE_PASS` both pass.

G19 is the first post-G18 production-path correction. It keeps the near-2K
terrain footprint, 128 by 128 chunks or about 2048 by 2048 blocks, but removes
the dense G16 architecture from the normal path. The addon starts a compact
procedural world from a deterministic descriptor and generates active page bytes
on demand through the existing native page baker and runtime pipeline.

This milestone exists because dense source/world files are not acceptable as a
normal game terrain path. G16 and G17 remain stress evidence only. G19 is the
replacement validation path for this scale.

Required behavior:

- `g19_compact_2k_on_demand` is a selectable playable profile;
- the profile uses `DETERMINISTIC_REFERENCE` generation, not a baked world;
- the runtime reports 16,384 indexed pages for the 128 by 128 footprint;
- no dense source directory and no baked world directory are created for G19;
- no `world.wtworld`, `streaming.wtworld`, or `procedural.wtseed` file is
  created under the G19 object root;
- the active viewer path stays bounded to at most 25 render resources and 25
  collision resources;
- an active-center carve edit commits and replaces render resources;
- generated runtime files remain under the 50 MiB per-file target and 100 MiB
  total generated-object-root ceiling.

Validation:

```text
python tools/validate_g19_contract.py
python tools/g19_compact_2k_on_demand_smoke.py
```

Expected markers:

```text
WT_VALIDATION_G19_CONTRACT_PASS implementation=compact_2k_on_demand
WT_VALIDATION_G19_COMPACT_2K_ON_DEMAND_PASS profile=g19_compact_2k_on_demand samples=5 pages=16384 max_render_resources=25 max_collision_resources=25 edit_replacements=... dense_world_files=0
WT_VALIDATION_G19_COMPACT_2K_ON_DEMAND_SMOKE_PASS engines=2 max_file_bytes=... total_bytes=... report=artifacts/g19_compact_2k_on_demand/g19_compact_2k_on_demand_report.json
```

Boundary:

- G19 proves compact deterministic on-demand terrain streaming at the near-2K
  validation footprint.
- G19 does not claim final terrain art, biomes, water, GPU generation,
  compute-shader acceleration, dynamic LOD, multiplayer, or production save-file
  design.
