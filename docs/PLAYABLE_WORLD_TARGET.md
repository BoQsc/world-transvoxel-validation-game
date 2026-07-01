# Playable World Target

Status: active target contract.

This repository must eventually validate a real game-facing world built from
`world-transvoxel`, `world-transvoxel-terrain`, and a future game-world addon.
Tiny one-chunk rendering is only an early gate, not the finish line.

## Map scale vocabulary

When this project says `2000×2000`, `2000x2000`, `2K map`, or
`2K-world exploration`, it means horizontal block/grid dimensions:

- `2000×2000` means 2000 blocks by 2000 blocks;
- with the standard baseline of 1 block = 1 meter, this is about 2 km by 2 km;
- the horizontal area is 2000 * 2000 = 4,000,000 m², or 4 km².

This is not chunk count. Current 8 by 8 fixtures are validation fixtures, not
the final 2000 by 2000 block exploration target.

G8/G9/G10 add a bounded sparse 2K path fixture. That fixture proves 2000×2000
coordinate handling, playable-scene integration over 93 active sparse path
resources, and single-viewer playable streaming with a 25-resource active
window. It is still not the same as rendering or generating the full 2000 by
2000 surface.

G11 adds a dense generated 16 by 16 fixture with 256 generated pages. It proves
that generated terrain can use the same playable single-viewer 25-resource
active window without loading every generated page at once. It is a scale-up
step from 8 by 8 fixtures, not the final 2000 by 2000 world.

G12 scales that generated path to a 32 by 32 fixture with 1024 generated pages,
roughly a 512 by 512 block generated terrain step. It preserves the same
single-viewer 25-resource active window and still avoids claiming final 2000 by
2000 generated terrain.

G13 locks a generated fixture vertical coverage guard. Future generated fixtures
must prove their surface min/max height stays inside the active vertical chunk
with explicit margins, and reused generated fixtures must match the expected
source revision before Godot runtime tests run.

G14 scales the generated path to a 64 by 64 fixture with 4096 generated pages,
roughly a 1024 by 1024 block terrain step. It adds a streamed source writer so
larger bake inputs are written predictably without a large in-memory source
buffer, while keeping the same single-viewer 25-resource active window.

G15 locks G14 scale telemetry by checking source sizes, source revision,
vertical margins, engine markers, and active-resource budget before another
generated-terrain scale jump.

G16 is the 128 by 128 dense generated near-2K playable streaming gate. It is
roughly a 2048 by 2048 block generated terrain step, with 16384 generated pages
and the same 25-resource active streaming budget.

G17 prepares the G16 near-2K generated project for human visual playtesting. It
pins the generated scene to `g16_generated_128x128`, imports the project, and
records `human_confirmation` as pending.

G18 is the production budget pivot. G16 and G17 are stress-only evidence, not
production terrain architecture. The normal terrain path must not use the G16
dense source/world-file shape: no normal game path may require raw dense source
files, terrain/world files have a 100 MiB hard per-file ceiling and a 50 MiB
target per-file ceiling, and the 30 seconds load-to-play ceiling is mandatory. The next
architecture must be deterministic-on-demand generation or compact seed/config
plus edit journals.

G19 implements the first compact near-2K on-demand path. It keeps the 128 by
128 chunk footprint and 16384 indexed pages, but starts from a deterministic
procedural descriptor in the addons instead of dense source files or a baked
world manifest. Its validation requires no dense G19 source/world directories,
no `world.wtworld`, no `streaming.wtworld`, no `procedural.wtseed`, bounded
25-resource active streaming, edit replacement, and generated object-root files
under the 50 MiB target per-file and 100 MiB total budget. The same G19 gate
records each engine smoke duration and enforces the 30 second load-to-play
ceiling.

G20 closes the compact terrain storage/load-shape issue. The dense near-2K
source/world-file problem is resolved for the current validation boundary by
G19's addon-level on-demand path, including explicit 30 second timing evidence.
This is not final terrain art, not dynamic LOD seam approval, not GPU
generation, and not game-repository readiness.

G21 prepares the compact G19 project for human visual playtesting. It composes
the validation project from current local addon sources, pins the playable scene
to `g19_compact_2k_on_demand`, imports the project before handoff, and records
human_confirmation as pending. It is a handoff gate only; it must not reintroduce
dense near-2K source/world files as the normal path.

G22 runs the exact compact G21 handoff project before human review. It disables
human input during automation, captures automated PNG evidence, exercises
origin, center, and far-corner compact 2K positions, verifies scripted movement,
carve and construct/place, and requires settled runtime metrics with no render
fading resources and no pending chunk retirements. It does not claim final
terrain art, GPU generation, water, biomes, vegetation, buildings, multiplayer,
or game-repository readiness.

G23 fixes the failed human handoff by requiring real compact player-driven
streaming. The compact profile starts inside the 2K map, player movement drives
the active terrain viewer, and mouse look plus left/right click terrain edits
are checked through the real input path before human review can resume.

G24 is reclassified as capped active-window regression evidence. It still checks
map-scale positions, player-driven streaming, movement, edits, captures, and
compact storage, but it does not prove the player can see a full 2048 by 2048
terrain. The active window is only the local native Transvoxel detail layer.

G25 replaces G24 as the active large-terrain visibility gate. It requires full
2048 by 2048 terrain visual coverage, confirms sampled visual heights against
native authoritative backend samples, and confirms the active window is only the
local Transvoxel detail layer for editing and collision.

G26 is the active first-person full-terrain playable-experience gate. It keeps
human input disabled for automation while player-driven viewer updates remain
active, captures player-eye views at map-scale positions, verifies the local
detail window follows scripted player movement, and confirms terrain editing
still commits.

G27 is the active full-terrain human handoff preflight gate. It checks the
normal generated playtest scene directly before renewed human review, verifies
player/camera/crosshair/interactor/full-visual/local-detail readiness, and
requires event-driven material application so material work happens on runtime
state changes instead of every frame, plus a bounded material-repair audit for
missing overrides.

G28 is the active normal project launch preflight gate. It checks the normal
generated project launch that a human would use, keeps automation safe by
disabling human input in the generated scene file, and proves the project
reaches the playable `validation_playtest.tscn` scene through `project.godot`
without using a test script. For this gate, automation disables human input from
startup; after automation, the generated handoff scene is restored to human
input enabled for human playtest.

G29 is the active compact 2K human-ready handoff gate. It creates a separate
human-ready compact 2K handoff project, verifies current G27/G28 prerequisite
reports against current addon source commits, imports the project, leaves human
input enabled, and writes `HUMAN_REVIEW.md` into the generated project.

G30 is the active compact 2K review bundle gate. It packages the human-ready
project, G27/G28/G29 evidence, `REVIEW_INDEX.md`, and `HANDOFF_MANIFEST.json`
with SHA-256 hashes so the review artifact is auditable from one directory.

G31 is the active review bundle launch preflight gate. It proves copied-bundle
launch readiness by creating `bundle_launch_copy`, removing stale Godot import
cache, disabling human input only in the automation copy, and launching the
copied bundle project through `project.godot`.

G32 is the active exact review-bundle autonomous runtime proof gate. It proves
copied review-bundle runtime proof by running G25 full-terrain visual baseline,
G26 full-terrain playable experience, and G27 full-terrain handoff preflight
from a separate automation copy of the G30 bundle.

G33 is the active runtime terrain quality gate. It audits the exact runtime
evidence from G32 and enforces full visual coverage, first-person route evidence,
bounded active resources, edit/material behavior, copied PNG evidence, and a
30 second per-script quality ceiling. From G33 onward, runtime terrain quality
gates are the active direction; human-visible review remains a final sanity
check, not the active project direction.

Active track guardrails keep this from drifting again. Post-G33 milestones must
not be review, handoff, package, bundle, launch, or human-review milestones; the
allowed direction is measured runtime terrain quality and addon usability.

G34 is the active edit latency and persistence quality gate. It starts the
compact 2K runtime path from a clean state, performs timed carve and construct
edits, verifies authoritative samples, verifies edit journal creation, reloads
the scene, and verifies both edits replay from persistent storage.

G35 is the active terrain correctness and artifact detection quality gate. It
checks full-map mesh shape, finite surface heights, neighbor and diagonal-pair
continuity thresholds, material palette bounds, backend/visual height agreement,
capture evidence, and bounded active resources.

G36 is the active cold-idle performance quality gate. It holds the compact 2K
runtime scene idle for 300 frames after settling and proves no viewer-update
churn, edit-replacement churn, material auto-apply churn, queued work, pending
retirements, or render fade/blink resources occur.

G37 is the active streaming movement performance quality gate. It drives the
real validation player across five interior compact 2K route samples, performs
scripted local movement at each sample, and measures settle frames,
settled active-resource bounds, transient overlap bounds, fade/blink resources,
and material-apply churn.

G38 is the active streaming endurance stability quality gate. It repeats the
compact 2K streaming route for two cycles, verifies ten route samples with real
local player movement, and requires final cold idle with the standard
25-resource active window.

G39 is the active distributed edit streaming quality gate. It streams to four
distant compact 2K regions, applies carve/construct edits, verifies
authoritative samples, reloads the scene, and verifies all four edits replay
from the edit journal.

G40 is the active edit visual material feedback quality gate. It captures a
focused terrain patch before and after real edits, requires visible image delta,
verifies material stability, and checks authoritative edited samples.

G41 is the latest completed runtime frame budget telemetry quality gate. It
measures idle, movement/streaming, edit, and reload phase frame/update costs in
the normal compact 2K runtime scene and writes machine-readable telemetry for
later production comparison.

G42 is the latest completed collision traversal stability quality gate. It
drives the real validation player over flat baseline terrain, mountain/sloped
terrain, and edited compact 2K terrain while checking floor contact, control
state, vertical stability, and active-resource bounds.

G43 is the latest completed view distance presentation quality gate. It captures
multiple first-person compact 2K views and rejects tiny one-chunk-only
presentation by checking full visual coverage plus horizontal, vertical, and
mid-band terrain image coverage.

G44 is the latest completed edit policy and shape quality gate. It locks the default
sphere carve/place policy for the validation layer and verifies repeated edit
shape behavior with authoritative samples.

G45 is the latest completed storage recovery schema quality gate. It verifies compact
storage policy, journal versioning, reload, truncated-tail recovery, and
compaction/reopen behavior.

G46 is the latest completed terrain addon API contract quality gate. It locks
the minimal public `WtTerrainWorld` API for profile summaries, lifecycle,
streaming, edits, authoritative samples, storage snapshot requests, telemetry,
and debug snapshots.

G47 is the latest completed validation workaround removal quality gate. It moves
required material and mesh-inspection helpers into `world-transvoxel-terrain`,
removes their validation-game copies, and quarantines historical backend-facing
tests as audit evidence.

G48 is the latest completed native hot-path boundary quality gate. It exposes
the addon hot-path boundary through `WtTerrainWorld`, proves generation,
meshing, streaming, edit application, storage, and normal validation runtime
paths stay out of GDScript terrain hot loops, and keeps bounded debug/material
helpers separate from production hot paths.

G49 is the latest completed debug telemetry UI quality gate. It adds a
mouse-transparent telemetry overlay and JSON export to the normal validation
playtest scene for active chunks, queues, frame/update cost, edit state,
material state, and storage state.

G50 is the latest completed terrain profile standard quality gate. It locks the
standard `flat_baseline`, `mountain_8x8`, `g19_compact_2k_on_demand`, and
`g50_seeded_procedural_2k` profiles with deterministic seeds/source revisions,
active-resource expectations, and storage/load budgets.

G51 is the latest completed material texture pipeline quality gate. It locks the
current small deterministic UV2 material-id pipeline, including a 16 by 16
generated `RGBA8` texture, standard material IDs, shared material-instance
stability through edits and streaming, and authoritative material sampling.

G52 is the latest completed underground terrain variation quality gate. It locks
the native procedural vertical-strata model, public generation-profile
underground contract, flat-baseline volumetric density proof, and localized
underground carve behavior.

G53 is a completed large-world streaming radius quality gate. It proves
configurable compact 2K streaming radii 1, 2, 4, and 6 through the public viewer
path, exact active/render resources 9, 25, 81, and 169, radius-edge readiness,
outside-radius absence, growing visible mesh spread, and active-resource capacity
256.

G54 is a completed LOD seam and artifact quality gate. It proves the
current mixed LOD transition fixture through native production LOD streaming
evidence and a Godot runtime seam audit with LOD0/LOD1 render meshes, horizontal
seam-pair checks, diagonal edge bounds, edited seam stability, and post-edit
transition remeshing.

G55 is a completed map generator budget quality gate. It proves the
current deterministic compact 2K generator profiles load under the 30 seconds
load-to-play ceiling, expose 2048 by 2048 block maps through 16384 pages, avoid
dense normal terrain files, and stay inside the 50 MiB target and 100 MiB hard
file budgets.

G56 is a completed game-world addon prototype quality gate. It proves a
validation-owned `world_transvoxel_game_world` addon boundary can create the
standard world node, configure terrain profiles, attach an optional player,
drive player-based viewer updates, and submit terrain edits without dense normal
terrain files.

G57 is a completed separate game repository integration quality gate.
It proves the sibling `world-transvoxel-integration-game` repository imports the
three addon stack without validation-game scripts/tests/scenes, then runs the
compact 2K player-viewer and edit path on both supported Godot engines.

G58 is a completed documentation examples quality gate. It provides
installation, profile setup, terrain editing, storage, telemetry, and
troubleshooting examples, and keeps the separate integration repo README aligned.

G59 is a completed versioning release contract quality gate. It locks
versioning, compatibility, migration policy, license boundary,
source/reference policy, supported Godot versions, and the release checklist.

G60 is the latest completed Terrain 1.0 release-candidate quality gate. It runs
the bounded G41-G59 validation suite and requires zero known critical blockers.

The production world/terrain gap audit is
[`docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md`](PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md).
Current state after G60 is Terrain 1.0 release-candidate quality for the
validated compact 2K stack: automated validation-grade compact 2K terrain
runtime with measured frame/update telemetry, collision traversal stability, and
view-distance presentation coverage plus default sphere edit policy/repeated edit
shape validation plus compact storage recovery schema evidence and a minimal
game-facing terrain addon API contract plus validation-workaround removal
evidence plus native hot-path boundary evidence, debug telemetry UI evidence, and
terrain profile standard evidence plus material texture pipeline evidence and
underground density/material variation evidence plus configurable streaming
radius evidence plus mixed LOD seam/artifact evidence and map-generator budget
evidence plus game-world addon prototype evidence and separate game repository
integration evidence plus documentation examples evidence, versioning release
contract evidence, and the full G60 release-candidate suite.

The finite production roadmap is
[`docs/FINITE_PRODUCTION_ROADMAP.md`](FINITE_PRODUCTION_ROADMAP.md). Terrain 1.0
is bounded to G41 through G60, with G60 as the release-candidate finish line.
Future work after G60 belongs to explicit post-1.0 roadmaps.
The post-1.0 production gap register is
[`docs/POST_1_0_PRODUCTION_GAP_REGISTER.md`](POST_1_0_PRODUCTION_GAP_REGISTER.md).
The post-1.0 roadmap has completed P1 game-world addon extraction, P2 production
integration game proof, P3 scale and coordinate policy, and P4 production
terrain rendering/materials/object density. G51 is baseline material/texture
proof, not final production terrain texturing; P4 adds the production material
texture foundation. P5 optional GPU/compute acceleration proof is next.

## Required before final human-visible sanity check

- first-person player with crosshair and terrain interaction affordances;
- flat terrain baseline as the default reproducible mode;
- mountain/8 by 8 multi-chunk generation mode for scale and visual validation;
- digging and placing with measured latency and deterministic recovery policy;
- textured terrain material path with small, performance-conscious test assets;
- terrain collision, chunking, cold-idle behavior, and visible-runtime telemetry;
- full 2048 by 2048 terrain visual coverage before renewed human visual review;
- first-person full-terrain playable-experience captures before renewed human
  visual review;
- normal generated playtest scene preflight before renewed human visual review;
- normal generated project launch preflight before renewed human visual review;
- human-ready compact 2K handoff project before renewed human visual review;
- Compact 2K review bundle before renewed human visual review;
- copied-bundle launch readiness before renewed human visual review;
- copied review-bundle runtime proof before renewed human visual review;
- runtime terrain quality gate before renewed human visual review;
- edit latency and persistence quality gate before renewed human visual review;
- terrain correctness and artifact detection quality gate before renewed human
  visual review;
- cold-idle performance quality gate before renewed human visual review;
- streaming movement performance quality gate before renewed human visual
  review;
- streaming endurance stability quality gate before renewed human visual review;
- distributed edit streaming quality gate before renewed human visual review;
- edit visual material feedback quality gate before renewed human visual review;
- runtime frame budget telemetry quality gate before claiming production-ready
  terrain performance;
- collision traversal stability quality gate before claiming production-ready
  player traversal;
- view distance presentation quality gate before claiming production-ready
  large-world presentation;
- edit policy and shape quality gate before claiming production-ready digging
  and placing;
- terrain profile standard quality gate before material, underground, streaming
  radius, seam/artifact, or generator-budget work;
- material texture pipeline quality gate before underground, streaming radius,
  seam/artifact, or generator-budget work;
- underground terrain variation quality gate before streaming radius,
  seam/artifact, or generator-budget work;
- LOD seam and artifact quality gate before generator-budget work;
- map-generator budget quality gate before game-world addon prototype work;
- game-world addon prototype quality gate before separate game repository
  integration work;
- separate game repository integration quality gate before documentation
  examples work;
- documentation examples quality gate before versioning release contract work;
- versioning release contract quality gate before Terrain 1.0 release candidate
  work;
- Terrain 1.0 release candidate quality gate before claiming Terrain 1.0 for the
  validated compact 2K stack;
- production world/terrain gap audit before claiming production-ready terrain;
- finite production roadmap before adding new production milestones;
- automated captures and runtime checks before asking for human playtest.

## Addon boundary

- `world-transvoxel`: low-level MIT-backed Transvoxel backend.
- `world-transvoxel-terrain`: terrain addon with generation, meshing,
  streaming, edit/storage/recovery, and terrain-facing public APIs.
- `world-transvoxel-gameworld`: game-world addon with standard world node,
  terrain node setup, player interaction integration, and game-world defaults
  without forcing a specific game.
- future optional addons can cover vegetation, block/voxel buildings, fluids,
  and entities after terrain is technically reliable.

## Standard-first terrain policy

Default mode should be boring and reliable:

- finite flat terrain baseline;
- deterministic generation seed/profile;
- cold when idle;
- no hidden background work after settling;
- native/backend hot paths for terrain, meshing, edits, and storage;
- GDScript limited to scene scaffolding, input glue, HUD, and tests.

Optional modes can add quantized generation, octahedral/alternate edit shapes,
mountain biomes, fluids, vegetation, GPU bursting, or compute paths only after
the default path remains measurable and stable.

## Not accepted as final

- a gray patch without terrain interaction;
- a player that cannot walk on terrain collision;
- a screenshot without automated runtime evidence;
- hidden workarounds inside the validation game instead of addon fixes;
- broad GPU/fluids/biomes work before terrain play/edit performance is measured.
