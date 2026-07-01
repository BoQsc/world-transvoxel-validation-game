# Post-1.0 production gap register

Status: active gap register; P1 through P4 complete, P5 next.

Purpose: keep production gaps explicit. A completed baseline gate does not mean
the corresponding production feature is finished. Each gap below must either be
closed by a bounded milestone, deferred with a clear reason, or split into
smaller gaps before implementation.

This register is the source of truth for post-1.0 gap discovery. The roadmap in
`docs/POST_1_0_RESEARCH_AND_ROADMAP.md` pulls milestone order from this file
instead of rediscovering missing requirements one by one.

## Gap states

- `closed`: the gap has a passing command, marker, and documented failure
  boundary.
- `next`: the next implementation target.
- `planned`: accepted, ordered after the current target.
- `deferred`: real gap, intentionally outside the current near-term track.
- `split-required`: too broad to implement until divided into smaller milestones.

## Current gap register

| Gap ID | Topic | State | Owner boundary | Target | Production gap |
| --- | --- | --- | --- | --- | --- |
| `P3-SCALE-COORDINATES` | Scale and coordinate policy beyond compact 2K | closed | `world-transvoxel-terrain`, validation game | P3 | Closed by `docs/P3_SCALE_COORDINATE_POLICY.md`, `tools/validate_p3_contract.py`, and `tools/p3_scale_coordinate_policy.py`; the optional `large_4k_optional` policy records scale vocabulary, coordinate/origin boundaries, and 4K on-demand budgets. |
| `P4-TERRAIN-TEXTURES` | Production terrain material and texture pipeline | closed | `world-transvoxel-terrain`, `world-transvoxel-gameworld`, validation game | P4 | Closed by `docs/P4_PRODUCTION_TERRAIN_RENDERING_MATERIALS_OBJECT_DENSITY.md`; the terrain addon now exposes production texture slots, sample material atlases, mapping/blending/import policy, and material summary budget fields beyond G51. |
| `P4-RENDER-DENSITY` | Rendering and object-density foundation | closed | `world-transvoxel-terrain`, future object/vegetation addons | P4 | Closed by P4 policy: active terrain work remains bounded, future objects must be chunk/cell partitioned, huge unculled resources fail, and render/entity telemetry is required. |
| `P4-VISUAL-VALIDATION` | Automated visual/artifact validation | closed | validation game, integration game | P4 | Closed by P4 guardrails combining G43 view-distance presentation, G51 material/edit/streaming stability, G54 LOD seam/artifact evidence, and the new production material pipeline audit. |
| `P4-EDITOR-UX` | Editor/plugin UX and authoring tools | planned | `world-transvoxel-terrain`, `world-transvoxel-gameworld` | P5/P5A | P4 decided editor UX hardening is not blocking P4; games still need inspector presets, profile selection, debug panels, terrain authoring affordances, and clear errors without editing validation scripts. |
| `P5-GPU-ACCELERATION` | Optional GPU/compute acceleration | next | `world-transvoxel`, `world-transvoxel-terrain` | P5 | GPU paths must be optional, measured against the native CPU baseline, split into bounded dispatches, and avoid mandatory CPU/GPU sync for correctness. |
| `P6-WATER-LAVA` | Water/lava representation and terrain coupling | planned | future fluid addon plus terrain integration API | P6 | Water/lava needs a separate storage/simulation/render contract, explicit terrain coupling, and budgets before volumetric fluid work is attempted. |
| `P7-VEGETATION-BIOMES` | Vegetation and biome prototype | planned | future vegetation addon, `world-transvoxel-gameworld` | P7 | Biome/material profiles, deterministic spawn rules, edit masks, chunk/cell culling, and instance telemetry are not production-defined. |
| `P8-BLOCK-BUILDINGS` | Voxel/block building system | planned | future building addon, gameworld integration | P8 | Block/building data needs separate storage, meshing, collision, LOD/culling, and explicit terrain interaction events. |
| `POST-STORAGE-MIGRATION` | Long-term save format, migration, and recovery | planned | `world-transvoxel`, `world-transvoxel-terrain` | split-required | G45 proves compact storage recovery basics. Production still needs backward compatibility policy, migration tests, corruption handling, backups, and user-visible recovery errors. |
| `POST-LIFECYCLE-LOADING` | Loading, progress, cancellation, and graceful failure | planned | `world-transvoxel-gameworld`, terrain addon | split-required | Production games need loading screens, async progress, cancellation, failed-generation recovery, and bounded startup behavior beyond current smoke gates. |
| `POST-INTERACTION-MINING` | Player interaction, mining, restoration, and terrain equilibrium | planned | `world-transvoxel-gameworld`, terrain addon | split-required | Default sphere carve/place is proven, but production mining needs shape policy, tool policy, material rewards, restoration/regeneration rules, and optional stability/collapse semantics. |
| `POST-COLLISION-PHYSICS` | Collision and physics edge cases | planned | `world-transvoxel`, `world-transvoxel-terrain` | split-required | G42 proves traversal stability for current profiles. Production still needs more slope/cave/edit-edge cases, moving bodies, collision refresh cost, and physics failure telemetry. |
| `POST-LOD-EXPANSION` | LOD/seam quality across more terrain styles | planned | `world-transvoxel`, `world-transvoxel-terrain` | split-required | G54 proves a transition fixture. Production needs broader edited seam cases, pathological terrain, multiple material styles, and visual artifact thresholds. |
| `POST-PERFORMANCE-PRESETS` | Product performance presets and budgets | planned | `world-transvoxel-terrain`, gameworld addon | split-required | The project needs low/medium/high quality presets, CPU/GPU/memory/storage budgets, and representative runtime measurements for game settings. |
| `POST-ERROR-TELEMETRY` | Error handling and developer telemetry contract | planned | all addons | split-required | Developers need stable error codes/messages, failure summaries, debug exports, and actionable telemetry when generation, streaming, storage, or rendering fails. |
| `POST-PACKAGING-RELEASE` | Addon packaging, CI, export compatibility, and dependency versions | planned | all repos | split-required | Release quality needs build/export matrix, dependency compatibility checks, install/update docs, exported-game validation, and no generated cache artifacts in commits. |
| `POST-GAMEWORLD-SCOPE` | Gameworld addon scope boundary | planned | `world-transvoxel-gameworld` | split-required | The project must define what belongs in terrain, gameworld, future world systems, and game-specific code before adding broad gameplay features. |
| `POST-NETWORKING` | Multiplayer terrain replication | deferred | future networking/gameworld layer | split-required | Networking is not part of the current terrain correctness path. It needs authority, replication, conflict resolution, bandwidth, save sync, and security design before implementation. |
| `POST-PLANETS` | Planets/moons and non-flat world topology | deferred | future world system | split-required | Planet-scale or spherical worlds require coordinate/origin policy, gravity/up-vector policy, streaming topology, and generator changes beyond compact 2K terrain. |

## Roadmap consumption order

1. P3 closed `P3-SCALE-COORDINATES`.
2. P4 closed `P4-TERRAIN-TEXTURES`, `P4-RENDER-DENSITY`,
   `P4-VISUAL-VALIDATION`, and moved `P4-EDITOR-UX` to P5/P5A.
3. P5 is next and closes `P5-GPU-ACCELERATION` only after P4 produces measured
   bottleneck boundaries.
4. P6, P7, and P8 remain separate systems after terrain presentation and scale
   policy are stable.
5. `split-required` gaps must become smaller milestone documents before code
   implementation begins.

## Non-drift rules

- Do not claim a production feature is complete because a baseline gate exists.
- Do not start a planned/deferred gap before the current `next` gap is closed
  unless the roadmap is updated and validators agree.
- Do not merge future systems into smooth terrain storage or meshing without an
  explicit owner boundary and failure boundary.
- Do not add broad GDScript hot loops for runtime terrain, vegetation, storage,
  or generation paths.
- Do not commit generated Godot cache files, UID artifacts, or dense generated
  terrain files as source.

## Validator marker

```text
WT_VALIDATION_POST_1_0_GAP_REGISTER_PASS completed=P3_scale_coordinate_policy,P4_terrain_rendering_materials_object_density next=P5_gpu_acceleration
```
