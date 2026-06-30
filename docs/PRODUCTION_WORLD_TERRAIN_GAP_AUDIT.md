# Production World/Terrain Gap Audit

Status: active gap contract.

This document exists to prevent milestone drift. It states where the validation
game actually is after G40, what the expected final world/terrain target is, and
which gaps must close before this can be called production-ready large-world
terrain.

## Current claim boundary after G40

The current validated claim after G43 is:

> automated validation-grade compact 2K terrain runtime with measured frame/update telemetry, collision traversal stability, and view-distance presentation coverage, not production-ready large-world terrain.

That means the repository currently proves a real Godot validation project can
import the sibling addons, run the compact `2048 by 2048` block terrain profile,
stream a bounded local Transvoxel detail window, edit terrain, replay distributed
edits, remain cold when idle, measure frame/update telemetry, prove collision
traversal stability across flat, mountain/sloped, and edited terrain cases, prove
multi-position first-person view-distance presentation coverage, and produce
automated evidence for specific runtime quality gates.

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
- visible edit/material feedback above an image-delta threshold.

## Not production-ready yet

These are the major gaps between the current validation state and the expected
final world/terrain:

1. Runtime frame budget telemetry is not yet a production performance contract.
   We need measured frame-time, update-churn, memory/resource, and edit/stream
   cost evidence across idle, movement, streaming, and editing.
2. Player collision traversal is not yet a long-route stability contract. We
   need scripted traversal over flat, sloped, mountainous, and edited terrain
   with floor/contact stability, no falling through terrain, and no control
   breakage.
3. Human-facing playable view distance is not yet a production presentation
   contract. Automated full visual coverage exists, but the first-person
   presentation still needs draw-distance/horizon assertions that match the
   intended large-world experience.
4. The public terrain addon API is not yet locked as a game-facing contract.
   Games need stable generation, streaming, edit, material, storage, telemetry,
   and debug hooks without depending on validation-game internals.
5. The material/texture pipeline is not yet production quality. We need stable
   texture selection, small test assets, biome/material assignment rules, and no
   visible edit flicker.
6. Dynamic LOD and seam quality are not yet final production contracts. The
   current path validates bounded local detail, not a finished multi-LOD terrain
   product.
7. Storage/recovery is not yet a long-term schema contract. The edit journal is
   validated, but versioning, compaction, binary format policy, recovery rules,
   and migration behavior still need gates.
8. World generation is not yet the final game-world generator. Flat baseline and
   compact procedural terrain are required, but biomes, underground variation,
   veins, caves, and optional quantized generation need separate standards.
9. Fluids, lava, vegetation, voxel buildings, entities, multiplayer, planets,
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
3. `G43 - Terrain addon API contract quality`: lock the minimal stable
   game-facing API for generation, streaming, editing, materials, storage, and
   telemetry.
4. `G44 - Material texture pipeline quality`: prove stable texture/material
   assignment and edit feedback without flicker or excessive churn.
5. `G45 - Storage recovery schema quality`: prove compact binary/storage policy,
   deterministic recovery, journal compaction, and versioned migration behavior.

This order keeps the project focused on production terrain reliability before
adding water, vegetation, buildings, planets, multiplayer, or compute-shader
acceleration.

## Current decision

The project should not claim production-ready large-world terrain yet. It should
claim the narrower current state: automated validation-grade compact 2K terrain
runtime after G40.

G41 closed the runtime frame budget telemetry quality gap for the current
compact 2K validation path. G42 closed the collision traversal stability quality
gap for current validation profiles. G43 closed the view distance presentation
quality gap for current compact 2K first-person views. The immediate direction
after G43 is to close the production-readiness gap through G44 edit policy and
shape quality, then continue through the finite G41-G60 Terrain 1.0 roadmap.
