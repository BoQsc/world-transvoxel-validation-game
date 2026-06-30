# Production World/Terrain Gap Audit

Status: active gap contract.

This document exists to prevent milestone drift. It states where the validation
game actually is after G52, what the expected final world/terrain target is, and
which gaps must close before this can be called production-ready large-world
terrain.

## Current claim boundary after G52

The current validated claim after G52 is:

> automated validation-grade compact 2K terrain runtime with measured frame/update telemetry, collision traversal stability, view-distance presentation coverage, default sphere edit policy/repeated edit shape validation, compact storage recovery schema evidence, a minimal game-facing terrain addon API contract, validation-workaround removal evidence, native hot-path boundary evidence, debug telemetry UI evidence, terrain profile standard evidence, material texture pipeline evidence, and underground density/material variation evidence, not production-ready large-world terrain.

That means the repository currently proves a real Godot validation project can
import the sibling addons, run the compact `2048 by 2048` block terrain profile,
stream a bounded local Transvoxel detail window, edit terrain, replay distributed
edits, remain cold when idle, measure frame/update telemetry, prove collision
traversal stability across flat, mountain/sloped, and edited terrain cases, prove
multi-position first-person view-distance presentation coverage, verify the
default sphere carve/place policy with repeated edit shape samples, verify
compact storage journal/reload/truncated-tail recovery plus sparse 2K
compaction/reopen, prove a minimal public `WtTerrainWorld` API path for profile
summaries, lifecycle, streaming, edits, authoritative samples, storage,
telemetry, and debug snapshots, move required material and mesh-inspection
helpers into the terrain addon, quarantine historical backend-facing tests as
audit evidence, lock the native hot-path boundary for generation, meshing,
streaming, edit application, storage, and normal validation runtime paths,
provide a normal-scene debug telemetry overlay/export for active chunks, queues,
frame/update cost, edit state, material state, and storage state, and lock the
standard flat baseline, mountain, compact 2K, and seeded procedural 2K terrain
profiles with deterministic seeds/source revisions and storage/load budgets, and
lock the current small deterministic material/texture pipeline through edit and
streaming stability evidence, and prove baseline underground density/material
variation with localized carve behavior.

It does not mean the final game-world terrain product is complete.

## Expected final world/terrain target

The expected final target is a solid, robust, reliable, performant, reusable
large-world terrain stack:

- `world-transvoxel` supplies the low-level Transvoxel backend;
- `world-transvoxel-terrain` supplies the reusable terrain addon;
- a future game-world addon supplies standard world/player integration defaults;
- a separate game repository proves real game usage on top of those addons.

The final terrain path must support flat baseline worlds, procedural large
terrain, player traversal, digging and placing, compact storage, deterministic
recovery, material/texture assignment, event-driven runtime behavior, bounded
streaming, useful telemetry, and clear public APIs.

The validation game must not hide terrain defects with local workarounds. If a
gap belongs in an addon, the validation result must push the fix back to the
addon repository.

## Proven by the current validation track

These items are currently backed by milestone evidence in this repository:

- compact near-2K on-demand terrain generation without normal dense
  near-2K source/world files;
- full `2048 by 2048` terrain visual coverage as a validation baseline;
- local editable/collision Transvoxel detail layer bounded to the standard
  25-resource active window after settling;
- carve and construct/place edit paths through the runtime terrain interactor;
- edit latency and persistence through an edit journal and scene reload;
- terrain correctness checks for finite heights, continuity, material bounds,
  and backend/visual height agreement;
- cold-idle behavior with no hidden viewer-update, edit-replacement, material,
  queue, retirement, or fade/blink churn after settling;
- movement streaming across multiple compact 2K regions;
- repeated streaming endurance returning to final cold idle;
- distributed edits across distant compact 2K regions with replay verification;
- visible edit/material feedback above an image-delta threshold;
- runtime frame/update telemetry across idle, movement, editing, and reload;
- scripted collision traversal stability across flat, sloped, mountainous, and
  edited validation profiles;
- first-person compact 2K view-distance presentation coverage;
- repeated default sphere edit policy and shape behavior;
- compact 2K journal/reload/truncated-tail recovery plus sparse 2K
  compaction/reopen;
- minimal public terrain addon API contract for profile summaries, lifecycle,
  streaming, edits, authoritative samples, storage, telemetry, and debug
  snapshots;
- addon-owned material applicator and mesh-stats helpers in the normal
  validation scene, with no local validation-game copies of those terrain
  helpers;
- native hot-path boundary evidence for generation, meshing, streaming, edit
  application, storage, and normal validation runtime paths;
- debug telemetry UI/export evidence for active chunks, queues, frame/update
  cost, edit state, material state, and storage state;
- terrain profile standard evidence for `flat_baseline`, `mountain_8x8`,
  `g19_compact_2k_on_demand`, and `g50_seeded_procedural_2k`;
- material texture pipeline evidence for deterministic UV2 material assignment,
  small generated texture budget, construct-edit material sampling, and streaming
  material stability.

## Not production-ready yet

These are the major gaps between the current validation state and the expected
final world/terrain:

1. Large-world streaming radius and dynamic LOD seam quality are not yet final
   production contracts. The current path validates bounded local detail, not a
   finished multi-LOD terrain product.
2. World generation is not yet the final game-world generator. Flat baseline and
   compact procedural terrain are required, but biomes, veins, caves, deep
   vertical worlds, and optional quantized generation need separate standards.
3. Fluids, lava, vegetation, voxel buildings, entities, multiplayer, planets,
   and compute/GPU acceleration are future systems. They must not be treated as
   complete just because the terrain validation path exists.

## Gap closure ladder

Every gap must become a measurable milestone before it is considered closed.
Each milestone must name:

- the command that proves it;
- the marker that reports success;
- concrete thresholds;
- the failure boundary;
- whether the fix belongs in `world-transvoxel`, `world-transvoxel-terrain`, this
  validation game, or a future addon.

The finite production roadmap is
[`docs/FINITE_PRODUCTION_ROADMAP.md`](FINITE_PRODUCTION_ROADMAP.md). Terrain 1.0
is bounded to G41 through G60; G60 is the release-candidate finish line.

The first production-gap milestones are:

1. `G41 - Runtime frame budget telemetry quality`: measure real idle, movement,
   streaming, edit, and reload costs under the compact 2K profile.
2. `G42 - Collision traversal stability quality`: drive long scripted player
    routes across flat, sloped, mountainous, and edited terrain while checking
    floor/contact stability and control state.
3. `G43 - View distance presentation quality`: prove first-person compact 2K
   presentation is not a tiny one-chunk-only view.
4. `G44 - Edit policy and shape quality`: lock default sphere carve/place
   policy and prove repeated edit shape behavior.
5. `G45 - Storage recovery schema quality`: prove compact binary/storage policy,
   deterministic recovery, journal compaction, and versioned migration behavior.
6. `G46 - Terrain addon API contract quality`: lock the minimal stable
   game-facing API for generation, streaming, editing, materials, storage, and
   telemetry.
7. `G47 - Validation workaround removal quality`: move reusable terrain helpers
   out of the validation game and into the terrain addon.
8. `G48 - Native hot-path boundary quality`: lock the current native/backend
   ownership boundary for terrain hot paths and reject GDScript hot loops.
9. `G49 - Debug telemetry UI quality`: make active runtime state inspectable
   through a lightweight overlay or exported telemetry path.
10. `G50 - Terrain profile standard quality`: lock deterministic default terrain
    profiles before profile/material/underground work continues.
11. `G51 - Material texture pipeline quality`: lock deterministic small
     material/texture assignment before underground and streaming-radius work.
12. `G52 - Underground terrain variation quality`: lock baseline underground
    density/material strata, flat-world volumetric density, and localized
    underground carve behavior before streaming-radius work.

This order keeps the project focused on production terrain reliability before
adding water, vegetation, buildings, planets, multiplayer, or compute-shader
acceleration.

## Current decision

The project should not claim production-ready large-world terrain yet. It should
claim the narrower current state: automated validation-grade compact 2K terrain
runtime after G52.

G41 closed the runtime frame budget telemetry quality gap for the current
compact 2K validation path. G42 closed the collision traversal stability quality
gap for current validation profiles. G43 closed the view distance presentation
quality gap for current compact 2K first-person views. G44 closed the edit policy
and repeated shape quality gap for the default validation sphere brush. G45
closed the storage/recovery schema quality gap for compact 2K journal recovery
and sparse 2K compaction/reopen. G46 closed the minimal game-facing terrain
addon API contract gap. G47 moved required reusable validation-game terrain
helpers into the terrain addon and quarantined historical backend-facing tests as
audit evidence. G48 locked the native hot-path boundary for the current compact
2K validation path by adding addon API evidence and static/runtime validation
against GDScript terrain hot loops. G49 added a normal-scene debug telemetry
overlay/export path for active chunks, queues, frame/update cost, edit state,
material state, and storage state. G50 locked the terrain profile standard for
flat baseline, mountain, compact 2K, and seeded procedural 2K profiles. G51
locked the material texture pipeline for deterministic small UV2 material
assignment through edits and streaming. G52 locked baseline underground
density/material variation and localized underground carve behavior. The
immediate direction after G52 is G53 large-world streaming radius quality, then the
remaining finite G41-G60 Terrain 1.0 roadmap.
