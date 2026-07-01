# Post-1.0 research and onward roadmap

Status: post-1.0 research contract; P1 and P2 complete, P3 next.

Research date: 2026-07-01.

Terrain 1.0 ended at G60 for the validated compact 2K terrain stack. This
document defines the next bounded direction without appending G61 to the Terrain
1.0 roadmap.

## Current project boundary

The project currently has:

- `world-transvoxel`: low-level MIT-backed Transvoxel backend;
- `world-transvoxel-terrain`: reusable terrain addon;
- `world-transvoxel-gameworld`: reusable game-world addon with addon id
  `world_transvoxel_gameworld`;
- `world-transvoxel-integration-game`: separate proof game consuming
  `world_transvoxel`, `world_transvoxel_terrain`, and
  `world_transvoxel_gameworld`.

The old `world_transvoxel_game_world` identifier is historical prototype
evidence from G56/G57 only. P1 migrated that prototype into the cleaner final
addon id `world_transvoxel_gameworld`.

The next work must preserve the addon/repository boundary and move to scale
policy. It must not start fluids, vegetation, voxel buildings, planets,
multiplayer, or compute-shader acceleration as default terrain behavior before
the P3 scale and coordinate policy is real.

## Research facts that constrain the next step

1. Transvoxel remains the correct low-level terrain LOD seam technology for this
   project. The official Transvoxel description says transition cells join
   multiresolution voxel terrain boundaries and require only local voxel data,
   which matches the current edit/streaming architecture.

2. Godot GDExtension remains the correct default terrain hot-path boundary.
   The Godot C++ binding compatibility policy allows an extension built against
   an earlier Godot minor version to work on later minor versions, not the other
   way around. That supports continuing to validate against the oldest supported
   Godot minor version.

3. Compute shaders are useful, but they should be optional after measurement,
   not the default next step. Godot compute shaders require RenderingDevice-based
   renderers, use GLSL/SPIR-V, and can stall the CPU if synchronized
   immediately. Long compute work can trigger Windows TDR, so GPU meshing or
   generation must be split into bounded dispatches with telemetry.

4. The compact 2K map does not require a planetary coordinate solution.
   Godot's large-world documentation treats large world coordinates as useful
   for space or planetary-scale simulation, with performance/memory costs.
   Larger future worlds need an explicit coordinate/origin strategy before they
   are advertised.

5. Rendering only useful visible work should combine several layers:
   player-centered terrain streaming, normal frustum culling, occlusion/HLOD
   where scene layout permits it, and chunk/cell splitting for vegetation and
   entities. Godot documents visibility ranges, mesh LOD, occlusion culling, and
   MultiMesh as separate tools; none replaces terrain streaming.

6. Water/lava should be a separate post-1.0 system. Initial water should be a
   bounded surface/heightfield or local-cell simulation with terrain coupling.
   Fully volumetric water inside the Transvoxel density field is high-risk and
   should not be the first post-1.0 default.

7. Production terrain texture support is not far-future work. G51 proves the
   baseline material/texture path, but it is intentionally small deterministic
   evidence, not a production art pipeline. Godot's standard 3D material path
   already supports normal artist-facing texture channels and triplanar mapping
   options, while Godot texture import has explicit memory, disk-size, and VRAM
   compression tradeoffs. The project needs a bounded production terrain
   material/texture milestone before vegetation, fluids, buildings, or advanced
   biome systems are treated as normal work.

## Decision

The first post-1.0 track was:

`P1 - Game-world addon extraction and production boundary`

Rationale:

- it closes the largest documented remaining gap: the game-world addon is still
  validation-owned prototype code;
- it directly supports future game repositories without requiring copied
  validation internals;
- it keeps terrain stable while enabling future water, vegetation, buildings,
  player interaction, and editor tooling to attach through a standard world API;
- it avoids starting GPU acceleration before the CPU/native baseline has a clean
  game-world boundary and measurable bottlenecks.

P1 is now complete. P2 is also complete and proves the addon stack from a normal
minimal game repository. The next bounded track is:

`P3 - Scale and coordinate policy beyond compact 2K`

The first near-term presentation track after P3 is P4, and P4 must explicitly
include production terrain materials/textures. Do not leave production texturing
implicit under the completed G51 baseline gate.

The recommended repository/addon naming is:

- repository: `world-transvoxel-gameworld`;
- addon folder: `addons/world_transvoxel_gameworld`;
- addon id: `world_transvoxel_gameworld`;
- public root node: `WtGameWorld`;
- terrain dependency: `world-transvoxel-terrain`;
- low-level dependency remains hidden behind `world-transvoxel-terrain`.

Do not use `world-transvoxel-core` for this project structure.

## Bounded post-1.0 roadmap

### P1 - Game-world addon extraction and production boundary

Status: complete.

Goal: turn the validation-owned `world_transvoxel_game_world` prototype into a
real reusable addon/repository named `world-transvoxel-gameworld` with addon id
`world_transvoxel_gameworld`.

Exit:

- `world-transvoxel-gameworld` repository exists;
- `addons/world_transvoxel_gameworld` exists as the production addon folder;
- it imports `world-transvoxel` and `world-transvoxel-terrain` as dependencies;
- it exposes a stable world node, terrain node setup, optional player bridge,
  terrain edit bridge, telemetry bridge, and profile selection;
- it contains no validation-game scripts, scenes, tools, or artifacts;
- the validation game and integration game consume the addon from the same public
  API;
- a validator proves no copied validation internals.

Failure boundary:

- if games still need validation-game scripts, P1 is not complete.

Evidence:

- `WT_VALIDATION_P1_CONTRACT_PASS`;
- `WT_VALIDATION_P1_GAMEWORLD_ADDON_EXTRACTION_SMOKE_PASS`;
- `world-transvoxel-gameworld` repository with
  `addons/world_transvoxel_gameworld`.

### P2 - Production integration game proof

Status: complete.

Goal: make a normal minimal game repository prove the addon stack as an end-user
dependency.

Exit:

- a separate game repository opens through `project.godot`;
- it has a playable first-person character, crosshair, terrain edit input,
  terrain telemetry overlay, and profile selection;
- it runs the flat baseline and compact 2K procedural profile;
- it does not vendor validation-game tests or internal scripts;
- it has one command that validates launch, input, traversal, edit, storage, and
  cold idle.

Failure boundary:

- if the game repository needs manual patching after clone/import, P2 is not
  complete.

Evidence:

- `WT_VALIDATION_P2_CONTRACT_PASS`;
- `WT_PRODUCTION_GAME_P2_PASS` for `flat_baseline`;
- `WT_PRODUCTION_GAME_P2_PASS` for `g19_compact_2k_on_demand`;
- `WT_VALIDATION_P2_PRODUCTION_INTEGRATION_GAME_SMOKE_PASS`.

### P3 - Scale and coordinate policy beyond compact 2K

Status: next.

Goal: define how far the world can grow before origin/precision strategy changes.

Exit:

- the project records standard map scale vocabulary beyond 2K;
- the standard single-precision range, origin-shift boundary, and optional large
  world coordinate boundary are documented;
- one larger-than-2K profile validates streaming, file-size budget, load budget,
  memory budget, and visible presentation;
- the larger profile remains optional until it is as stable as compact 2K.

Failure boundary:

- if larger maps increase storage/load time without a new budget, P3 fails.

### P4 - Production terrain rendering, materials, and object-density foundation

Status: after P3.

Goal: define how terrain is presented with production-grade material/texture
support and how terrain, vegetation, props, and future buildings stay visible
only when useful.

Exit:

- production terrain material profiles expose real texture slots, at minimum
  albedo/color, normal, roughness/ORM, and material-id selection;
- the terrain shader policy is explicit: UV2/material-id baseline, triplanar or
  slope-aware mapping where appropriate, and a documented blending boundary;
- texture import policy documents resolution defaults, mipmaps/filtering,
  normal-map handling, VRAM/disk/memory budget, and fallback test assets;
- flat, mountain, compact 2K, and edit/reload cases validate that material
  assignment, texture selection, and material instances remain stable through
  streaming, edits, reloads, and mixed LOD;
- the standard sample set includes small performance-conscious terrain textures
  for at least grass/ground, rock, sand/dirt, and underground/stone materials;
- terrain material work remains event-driven and does not introduce per-frame
  material repair churn;
- terrain streaming prioritizes camera/player-facing active work without hiding
  required collision/edit chunks;
- vegetation and prop prototypes are chunk/cell split instead of one huge
  MultiMesh;
- HLOD/visibility-range and mesh-LOD policy is documented;
- occlusion is treated as optional scene-layout optimization, not a terrain
  correctness mechanism;
- automated telemetry reports visible terrain chunks, entity cells, draw calls,
  instance counts, and frame cost.

Failure boundary:

- if terrain still relies on only the 16 by 16 generated G51 checker/palette for
  normal presentation, P4 fails;
- if production texture support remains implicit under G51 instead of a measured
  P4 contract, P4 fails;
- if object systems create one huge unculled resource, P4 fails.

### P5 - Optional GPU/compute acceleration proof

Goal: prove one optional GPU path without replacing the native CPU/default path.

Exit:

- one isolated compute experiment exists for a measurable workload, such as
  height/material field generation or mesh-support preprocessing;
- dispatches are bounded to avoid long GPU stalls and Windows TDR risk;
- CPU/GPU sync is delayed or pipelined instead of immediate per-frame blocking;
- telemetry compares CPU/native baseline against GPU path on the same profile;
- disabling GPU acceleration returns to the current native path.

Failure boundary:

- if the GPU path becomes required for terrain correctness, P5 fails.

### P6 - Water/lava research prototype

Goal: select the first fluid representation without polluting terrain.

Exit:

- water/lava lives in a separate addon or clearly separate module;
- the first prototype is surface/heightfield/local-cell based, not full
  volumetric Transvoxel water;
- terrain coupling is explicit: sample terrain height, collision mask, carve
  changes, and storage events;
- budget includes simulation step time, render cost, memory, and storage.

Failure boundary:

- if water requires rewriting terrain storage or meshing before a prototype
  proves value, P6 fails.

### P7 - Vegetation and biome prototype

Goal: add visual richness without changing terrain correctness.

Exit:

- biome/material profiles decide spawn rules after P4 material profiles exist;
- vegetation is deterministic from seed plus edit masks;
- instances are chunk/cell partitioned for culling;
- no GDScript hot loop owns dense vegetation updates;
- telemetry reports instance counts and frame cost.

Failure boundary:

- if vegetation changes terrain correctness or creates hidden idle churn, P7
  fails.

### P8 - Voxel/block building prototype

Goal: add blocky/gridlike structures as a separate system from smooth terrain.

Exit:

- block/building data has its own storage and meshing path;
- the terrain edit API can interact with buildings only through explicit
  integration events;
- buildings have their own LOD/culling budget;
- physics/collision update cost is measured.

Failure boundary:

- if building data is mixed into smooth terrain density without a storage and
  collision contract, P8 fails.

## Immediate recommendation

Start P3. Do not begin compute shaders, fluids, vegetation, voxel buildings, or
planetary-scale work until P3 defines map scale vocabulary, coordinate/origin
boundaries, and a larger-than-compact-2K budget.

The next implementation milestone after P2 should be named:

`P3 - Scale and coordinate policy beyond compact 2K`

Texture support is not deferred to far future. The roadmap gap is closed by P4:
`Production terrain rendering, materials, and object-density foundation`. P4
must turn the G51 baseline material/texture proof into a production terrain
material and texture pipeline before vegetation, water/lava, voxel buildings, or
advanced biomes become normal work.

It should be validated by a command and marker, not by a human checklist.

## Roadmap gap handling rule

When the project discovers that a completed baseline gate does not equal a
production-ready feature, the post-1.0 roadmap must name the production gap
explicitly, place it in a bounded milestone, and add validator phrases for the
new boundary. Do not leave important systems hidden under completed proof gates.

## References checked

- Godot compute shaders:
  https://docs.godotengine.org/en/stable/tutorials/shaders/compute_shaders.html
- Godot GDExtension C++ bindings compatibility:
  https://github.com/godotengine/godot-cpp
- Godot large world coordinates:
  https://docs.godotengine.org/en/stable/tutorials/physics/large_world_coordinates.html
- Godot 3D performance, culling, and LOD:
  https://docs.godotengine.org/en/latest/tutorials/performance/optimizing_3d_performance.html
- Godot visibility ranges:
  https://docs.godotengine.org/en/stable/tutorials/3d/visibility_ranges.html
- Godot mesh LOD:
  https://docs.godotengine.org/en/stable/tutorials/3d/mesh_lod.html
- Godot StandardMaterial3D and ORM material:
  https://docs.godotengine.org/en/latest/tutorials/3d/standard_material_3d.html
- Godot texture importing:
  https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_images.html
- Godot ResourceImporterTexture compression modes:
  https://docs.godotengine.org/en/stable/classes/class_resourceimportertexture.html
- Godot CompressedTexture2D:
  https://docs.godotengine.org/en/stable/classes/class_compressedtexture2d.html
- Godot MultiMeshInstance3D:
  https://docs.godotengine.org/en/stable/classes/class_multimeshinstance3d.html
- Godot background loading:
  https://docs.godotengine.org/en/latest/tutorials/io/background_loading.html
- Godot threading:
  https://docs.godotengine.org/en/stable/tutorials/performance/using_multiple_threads.html
- Official Transvoxel overview:
  https://transvoxel.org/
- Eric Lengyel Transvoxel data tables:
  https://github.com/EricLengyel/Transvoxel
- Eric Lengyel, Voxel-Based Terrain for Real-Time Virtual Simulations:
  https://transvoxel.org/Lengyel-VoxelTerrain.pdf
- GPU geometry clipmaps:
  https://hhoppe.com/proj/gpugcm/
- GPU Gems water and fluid references:
  https://developer.nvidia.com/gpugems/gpugems/part-i-natural-effects/chapter-1-effective-water-simulation-physical-models
  https://developer.nvidia.com/gpugems/gpugems/part-vi-beyond-triangles/chapter-38-fast-fluid-dynamics-simulation-gpu
