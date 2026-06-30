# G52 - Underground terrain variation quality

G52 locks the first production-track underground terrain contract.

The purpose is narrow: prove the current terrain is backed by queryable voxel
density/material samples below the visible surface. This gate does not claim
deep vertical worlds, caves, ore veins, mining progression, biome ecology, or
final art.

## Contract

- Procedural compact terrain uses `density_volume_vertical_strata_v1`.
- Same-column underground samples must expose deterministic vertical material
  strata:
  - deep material `1`;
  - mid stone material `7`;
  - shallow subsoil material `4`.
- Density must increase consistently with grid `+Y`, crossing from solid
  underground to air above the surface.
- A local carve below the surface must modify the target voxel density without
  rewriting unaffected deeper strata.
- The flat baseline must also expose volumetric density samples through the
  same public authoritative sample API.
- Normal compact 2K runtime must not require dense near-2K source/world files.

## Required evidence

Static contract:

```text
WT_VALIDATION_G52_CONTRACT_PASS implementation=underground_terrain_variation_quality
```

Runtime contract:

```text
WT_VALIDATION_G52_UNDERGROUND_TERRAIN_VARIATION_PASS profile=g19_compact_2k_on_demand flat_profile=flat_baseline strata_samples=3 flat_volume_samples=3 density_ordered=1 strata_materials=1,7,4 flat_material=7 edit_localized=1 carved_density=1.000 max_render_resources=25 max_collision_resources=25 dense_world_files=0
```

Smoke wrapper:

```text
WT_VALIDATION_G52_UNDERGROUND_TERRAIN_VARIATION_SMOKE_PASS profile=g19_compact_2k_on_demand flat_profile=flat_baseline engines=2 native_configs=2 strata_materials=1,7,4 edit_localized=1 max_engine_seconds=... dense_world_files=0 report=artifacts/g52_underground_terrain_variation_quality/g52_underground_terrain_variation_quality_report.json
```

## Boundary

Passing G52 means underground density/material variation is validated for the
current compact terrain profiles and public sample API. It does not finish
large-world streaming radius, LOD seam quality, map-generator budgets, water,
biomes, caves, ore veins, or compute/GPU acceleration.
