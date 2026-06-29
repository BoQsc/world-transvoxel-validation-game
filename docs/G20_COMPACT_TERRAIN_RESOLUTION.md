# G20 - Compact terrain resolution gate

Status: complete when `WT_VALIDATION_G20_CONTRACT_PASS` and
`WT_VALIDATION_G20_COMPACT_TERRAIN_RESOLUTION_PASS` both pass.

G20 closes the specific G18/G19 storage and load-shape problem: the normal
near-2K validation path no longer depends on dense source files, a baked dense
world manifest, or large generated project artifacts.

Resolved scope:

- 128 by 128 chunks, roughly 2048 by 2048 blocks, are covered by
  `g19_compact_2k_on_demand`;
- terrain pages are generated on demand from the addon procedural descriptor;
- active render and collision resources stay within the 25-resource streaming
  window during the five-point near-2K traversal;
- terrain edit replacement works on the active center chunk;
- generated G19 runtime files remain below the 50 MiB per-file target and
  100 MiB total object-root ceiling;
- G16/G17 dense near-2K artifacts remain stress-only evidence, not the normal
  terrain path.

Still outside this resolution:

- final terrain art quality;
- dynamic LOD seam validation;
- GPU/compute generation;
- water, lava, biomes, vegetation, buildings, entities, multiplayer, and game
  repository readiness;
- final save-file and world-authoring policy.

Validation:

```text
python tools/validate_g20_contract.py
python tools/g20_compact_terrain_resolution.py
```

Expected marker:

```text
WT_VALIDATION_G20_CONTRACT_PASS implementation=compact_terrain_resolution
WT_VALIDATION_G20_COMPACT_TERRAIN_RESOLUTION_PASS compact_path_resolved=true map_blocks=2048 active_budget=25 max_file_bytes=... total_bytes=... report=artifacts/g19_compact_2k_on_demand/g19_compact_2k_on_demand_report.json
```
