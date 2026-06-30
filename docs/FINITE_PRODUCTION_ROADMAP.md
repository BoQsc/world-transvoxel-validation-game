# Finite Production Roadmap

Status: active roadmap contract.

This document defines the concrete remaining path from the current G48 state to
Terrain 1.0. It exists so the project does not degrade into an infinite list of
"next useful" tasks.

## Current state

Completed validation track: G0 through G48.

Current claim:

> automated validation-grade compact 2K terrain runtime with measured frame/update telemetry, collision traversal stability, view-distance presentation coverage, default sphere edit policy/repeated edit shape validation, compact storage recovery schema evidence, a minimal game-facing terrain addon API contract, validation-workaround removal evidence, and native hot-path boundary evidence, not production-ready large-world terrain.

The remaining roadmap is finite for Terrain 1.0. If new work is discovered, it
must either replace an existing gate, be folded into an existing gate, or be
explicitly deferred to post-1.0. It must not silently append an infinite tail.

## Terrain 1.0 finish line

Terrain 1.0 is reached when:

- `world-transvoxel` and `world-transvoxel-terrain` are usable from a normal
  Godot game project through public APIs;
- the default world supports a flat terrain baseline and deterministic large
  procedural terrain over the compact 2K target;
- the player can traverse, dig, and place without control loss, falling through
  terrain, edit flicker, or hidden idle churn;
- terrain streaming, collision, editing, storage, materials, and telemetry are
  measured by automated gates;
- dense near-2K source/world files are not required in the normal game path;
- validation-game workarounds are removed or moved into the correct addon;
- a separate minimal game repository can consume the addons without copying
  validation-game internals.

Terrain 1.0 does not require water, lava, vegetation, voxel buildings, planets,
multiplayer, or compute-shader acceleration. Those are post-1.0 systems unless a
specific gate below says otherwise.

## Terrain 1.0 gates

The remaining Terrain 1.0 gates after the current G48 state are G49 through
G60. G41 through G48 remain listed here as the completed evidence ladder.

### Phase A - Runtime reliability and performance

Goal: prove the current compact CPU/native terrain path behaves like real
runtime terrain, not just isolated feature checks.

1. `G41 - Runtime frame budget telemetry quality`
   - Measure idle, movement, streaming, edit, reload, active-resource, queue,
     and churn costs from the normal compact 2K runtime scene.
   - Output machine-readable frame/update telemetry and a pass marker.
   - Failure means performance is not yet a production contract.

2. `G42 - Collision traversal stability quality`
   - Drive long scripted player routes over flat, sloped, mountainous, and
     edited terrain.
   - Prove no falling through terrain, no stuck movement, no control-state loss,
     no invalid floor/contact state, and no unexpected active-window churn.
   - Failure means playable movement is not production reliable.

3. `G43 - View distance presentation quality`
   - Assert first-person visible terrain extent, horizon/presentation coverage,
     and absence of obvious one-chunk-only presentation.
   - Capture evidence from multiple compact 2K locations.
   - Failure means large-world presentation is still misleading.

4. `G44 - Edit policy and shape quality`
   - Lock the default carve/place shape, radius behavior, material behavior,
     latency budget, and optional alternate shape toggles.
   - Prove repeated edits do not create unstable artifacts or excessive churn.
   - Failure means digging/placing is not yet a stable terrain contract.

5. `G45 - Storage recovery schema quality`
   - Define and test compact binary/storage policy, edit journal versioning,
     reload behavior, recovery after interrupted writes, and journal compaction.
   - Failure means long-term worlds are not safe to persist.

### Phase B - Addon API and implementation boundary

Goal: ensure games use stable addon APIs instead of validation-game internals.

6. `G46 - Terrain addon API contract quality`
   - Lock public APIs for generation profiles, streaming control, edits,
     materials, storage, telemetry, and debug hooks.
   - Prove the validation game uses the public API path.
   - Failure means the addon is not ready for external games.

7. `G47 - Validation workaround removal quality`
   - Audit validation-game scripts and scenes for terrain logic that belongs in
     `world-transvoxel` or `world-transvoxel-terrain`.
   - Move required implementation into the correct addon or document a temporary
     blocker.
   - Failure means the validation game is masking addon incompleteness.

8. `G48 - Native hot-path boundary quality`
   - Verify terrain generation, meshing, streaming, edit application, storage,
     and heavy validation paths avoid GDScript hot loops.
   - Failure means the implementation boundary is not performance-safe.
   - Current status: complete when `WT_VALIDATION_G48_CONTRACT_PASS` and
     `WT_VALIDATION_G48_NATIVE_HOT_PATH_BOUNDARY_SMOKE_PASS` both pass.

9. `G49 - Debug telemetry UI quality`
   - Provide a lightweight in-game/debug overlay or exported telemetry path for
     active chunks, queues, frame/update cost, edit state, material state, and
     storage state.
   - Failure means problems are too hard to observe early.

### Phase C - Terrain generation, materials, and large-world behavior

Goal: make the terrain itself usable, inspectable, and configurable enough for
real game development.

10. `G50 - Terrain profile standard quality`
    - Lock default flat, mountain, compact 2K, and seeded procedural profiles.
    - Prove each profile is deterministic and fits storage/load budgets.
    - Failure means generation is not a stable standard.

11. `G51 - Material texture pipeline quality`
    - Prove terrain materials/textures assign deterministically, remain stable
      through edits and streaming, and use small performance-conscious assets.
    - Failure means visual terrain is not production usable.

12. `G52 - Underground terrain variation quality`
    - Define the baseline underground model for density/materials below the
      surface, including flat-world behavior.
    - Prove digging exposes voxel-based underground data rather than fake
      height-only behavior.
    - Failure means mining/deep terrain behavior is not trustworthy.

13. `G53 - Large-world streaming radius quality`
    - Validate configurable streaming radii, active-resource limits, and
      draw-distance behavior for the compact 2K target.
    - Failure means the terrain cannot scale beyond tiny visible regions.

14. `G54 - LOD seam and artifact quality`
    - Test seam/crack/artifact behavior across chunk and LOD boundaries,
      including diagonal artifacts and edited terrain.
    - Failure means the Transvoxel terrain is not visually reliable.

15. `G55 - Map generator budget quality`
    - Validate generation/loading stays inside the agreed budget: no normal
      terrain file over 100 MiB, target files near or under 50 MiB where
      practical, and load-to-play under 30 seconds for the compact 2K target.
    - Failure means the world generator is not practical for games.

### Phase D - Game-facing integration and release

Goal: prove the addon stack can be used like a real dependency, not just inside
this validation repository.

16. `G56 - Game-world addon prototype quality`
    - Prototype the future game-world addon boundary: standard world node,
      terrain node setup, optional player interaction integration, and defaults.
    - Failure means game setup is still too manual.

17. `G57 - Separate game repository integration quality`
    - Create or update a minimal separate game repository that imports
      `world-transvoxel`, `world-transvoxel-terrain`, and the game-world addon
      without copying validation-game internals.
    - Failure means the addon stack is not proven outside validation.

18. `G58 - Documentation examples quality`
    - Provide installation, profile setup, terrain editing, storage, telemetry,
      and troubleshooting examples.
    - Failure means users cannot reliably adopt the addons.

19. `G59 - Versioning release contract quality`
    - Define versioning, compatibility, migration policy, license boundary,
      source/reference policy, and supported Godot versions.
    - Failure means releases are not maintainable.

20. `G60 - Terrain 1.0 release candidate quality`
    - Run the complete Terrain 1.0 validation suite from a clean checkout.
    - Require all G41 through G59 gates to pass.
    - Require no known critical terrain correctness, performance, storage,
      collision, or integration blockers.
    - Passing G60 means Terrain 1.0 is reached.

## Post-1.0 backlog

These are important, but they are not required to finish Terrain 1.0:

- volumetric water and lava;
- vegetation;
- voxel/block building system;
- entity/large-object LOD systems;
- planets/moons;
- multiplayer terrain replication;
- compute-shader/GPU terrain acceleration;
- full biome ecosystem beyond baseline terrain/material profiles;
- massive worlds beyond the compact 2K target.

Each post-1.0 system must get its own bounded roadmap before implementation.

## Drift rule

The next milestone after G48 is G49. The finish line for this roadmap is G60.
No new Terrain 1.0 milestone may be appended after G60 unless it replaces or
merges with an existing G41-G60 gate and keeps the roadmap finite.
