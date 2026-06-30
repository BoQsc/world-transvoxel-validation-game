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

## Required before final human visual handoff

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
- automated captures and runtime checks before asking for human playtest.

## Addon boundary

- `world-transvoxel`: low-level MIT-backed Transvoxel backend.
- `world-transvoxel-terrain`: terrain addon with generation, meshing,
  streaming, edit/storage/recovery, and terrain-facing public APIs.
- future game-world addon name is undecided; it should provide the standard
  world node, terrain node setup, player interaction integration, and game-world
  defaults without forcing a specific game.
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
