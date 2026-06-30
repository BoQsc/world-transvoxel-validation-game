# G50 - Terrain profile standard quality

Status: complete when `WT_VALIDATION_G50_CONTRACT_PASS` and
`WT_VALIDATION_G50_TERRAIN_PROFILE_STANDARD_SMOKE_PASS` both pass.

G50 locks the Terrain 1.0 standard terrain profile set before material,
underground, large-radius streaming, seam/artifact, and map-generator work
continue.

## Standard profiles

The standard set is:

1. `flat_baseline`
   - role: default flat baseline;
   - source mode: `FLAT`;
   - expected active resources: 1.
2. `mountain_8x8`
   - role: default mountain fixture;
   - source mode: `BAKED_WORLD`;
   - expected active resources: 64.
3. `g19_compact_2k_on_demand`
   - role: compact 2K on-demand procedural baseline;
   - source mode: `DETERMINISTIC_REFERENCE`;
   - seed: `19019`;
   - source revision: `190019`;
   - expected active resources: 25.
4. `g50_seeded_procedural_2k`
   - role: seeded procedural 2K standard profile;
   - source mode: `DETERMINISTIC_REFERENCE`;
   - seed: `50050`;
   - source revision: `50050`;
   - expected active resources: 25.

## Quality bar

The gate requires:

- `scripts/validation_profile_catalog.gd` exposes the standard profile IDs and
  deterministic generation/storage descriptors;
- `scripts/validation_profile_standard_contract.gd` returns a stable
  `terrain_profile_standard_contract_v1` summary;
- the normal validation playtest scene runs all four profiles with human input
  and player-driven viewer updates disabled so G50 measures the profile-defined
  viewer windows;
- each profile reaches ready state and cold idle;
- each profile stays inside its expected active-resource count;
- each profile reaches load-to-play within 30 seconds;
- no normal profile file exceeds the 50 MiB target;
- no profile directory exceeds the 100 MiB ceiling;
- the compact and seeded procedural 2K profiles do not create dense
  `world.wtworld`, `streaming.wtworld`, or `procedural.wtseed` files.

## Commands

```bash
python tools/validate_g50_contract.py
python tools/g50_terrain_profile_standard_quality.py --skip-build
```

Expected markers:

```text
WT_VALIDATION_G50_CONTRACT_PASS implementation=terrain_profile_standard_quality
WT_VALIDATION_G50_TERRAIN_PROFILE_STANDARD_PASS profiles=4 runtime_profiles=4 deterministic=4 budgets=4 flat_resources=1 mountain_resources=64 compact_resources=25 seeded_resources=25 compact_seed=19019 seeded_seed=50050 max_profile_load_ms=... dense_world_files=0
WT_VALIDATION_G50_TERRAIN_PROFILE_STANDARD_SMOKE_PASS profiles=4 engines=... deterministic=4 budgets=4 max_engine_seconds=... max_file_bytes=... dense_world_files=0 report=artifacts/g50_terrain_profile_standard_quality/g50_terrain_profile_standard_quality_report.json
```

## Boundary

G50 does not claim final terrain art, material textures, underground variation,
larger streaming radii, LOD seam quality, map-generator budget quality, water,
vegetation, buildings, multiplayer, compute acceleration, or separate game
integration. Those remain covered by later finite Terrain 1.0 gates.
