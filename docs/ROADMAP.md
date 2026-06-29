# Roadmap

## G0 - Install/run validation scaffold

Status: complete by `WT_VALIDATION_G0_SMOKE_PASS`.

Exit:

- compose a fresh ignored Godot project from sibling `world-transvoxel` and
  `world-transvoxel-terrain` repos;
- run one headless install/run smoke;
- provide one human-visible playtest scene;
- keep all discovered addon failures visible and attributable.

Not in scope:

- production gameplay systems;
- broad open-world exploration;
- GPU compute;
- water/lava, planets, vegetation, building blocks, or structural stability;
- 0BSD backend replacement.

## G1 - Human-visible playtest confirmation

Status: active. Automated guard passes by `WT_VALIDATION_G1_SMOKE_PASS`; visual
capture passes by `WT_VALIDATION_G1_VISUAL_CAPTURE_RUN_PASS`; human rerun
confirmation remains pending. G1 is not the final playable-world gate.

Exit:

- open the generated validation project;
- run `res://scenes/validation_playtest.tscn`;
- confirm that the scene shows more than a gray rectangle: terrain or an
  explicit failure status, orientation markers, and validation status text;
- confirm that a playable character and follow camera are present;
- confirm programmatically that the visible terrain mesh has nonzero triangle
  geometry, terrain collision resources, and scripted player movement;
- keep a captured viewport image as automated evidence before asking for human
  confirmation;
- confirm whether there are obvious orientation, artifact, popping,
  missing-backside, or performance issues;
- record failures as addon work, not as hidden validation-game workarounds.

## G2 - First-person playable baseline

Status: complete by `WT_VALIDATION_G2_CONTRACT_PASS` and
`WT_VALIDATION_G2_SMOKE_PASS`. G1 human-visible rerun confirmation remains
pending, but the automated G2 gate is not blocked by that human confirmation.

Exit:

- first-person camera and crosshair are present for human play;
- flat terrain remains the default reproducible baseline;
- generated project supports player walk/jump against terrain collision;
- automated tests disable human input and prove scripted movement;
- visual capture shows terrain and player/play HUD evidence.

## G3 - Terrain generation modes

Status: complete by `WT_VALIDATION_G3_CONTRACT_PASS` and
`WT_VALIDATION_G3_SMOKE_PASS`.

Exit:

- flat baseline remains selectable;
- mountain/8 by 8 multi-chunk profile exists with deterministic seed;
- chunking/streaming counters prove bounded work and cold idle;
- captures cover flat and mountain modes.

## G4 - Terrain edit interaction

Status: complete by `WT_VALIDATION_G4_CONTRACT_PASS` and
`WT_VALIDATION_G4_SMOKE_PASS`.

Exit:

- first-person dig/place affordance exists;
- edit shape policy is explicit, with standard sphere/box and optional alternate
  shapes only when justified;
- edit latency and restore/recovery behavior are measured;
- automated tests prove terrain and collision update after edits.

## G5 - Material and performance baseline

Status: complete by `WT_VALIDATION_G5_CONTRACT_PASS` and
`WT_VALIDATION_G5_SMOKE_PASS`.

Exit:

- small texture/material path exists without hiding performance cost;
- baseline watt/performance behavior is measured;
- optional GPU burst/full-GPU paths remain decisions, not assumptions.

## G6 - Profile-selectable playable world

Status: complete by `WT_VALIDATION_G6_CONTRACT_PASS` and
`WT_VALIDATION_G6_SMOKE_PASS`.

Exit:

- generated playtest exposes flat and mountain playable profiles;
- both profiles keep first-person player, crosshair, materialized terrain,
  dig/place interaction, collision, and telemetry;
- automated captures cover both profiles before human handoff;
- `tools/prepare_human_playtest.py` prepares the reproducible human-test project
  and pins the generated scene to the 8 by 8 `flat_8x8` profile;
- handoff document gives the exact generated project path and accepted
  limitations.

## G7 - Human visual verification

Status: active. Automated handoff prep passes by
`WT_VALIDATION_G7_CONTRACT_PASS` and `WT_VALIDATION_G7_HANDOFF_READY`; final
human profile review remains pending.

Exit:

- reproducible handoff projects exist for `flat_8x8` and `mountain_8x8`;
- each generated scene is pinned to the intended profile before review;
- Godot import passes for both generated handoff projects;
- human opens the generated validation projects and confirms whether flat and
  mountain playable profiles look and feel acceptable;
- any terrain orientation, artifact, popping, performance, collision, or edit
  issue is recorded as addon follow-up work instead of hidden in the validation
  game.

## G8 - 2000×2000 bounded streaming

Status: complete by `WT_VALIDATION_G8_CONTRACT_PASS`,
`WT_VALIDATION_G8_WINDOW_PLAN_PASS`, and
`WT_VALIDATION_G8_RUNTIME_ACTIVE_WINDOW_PASS`.

Exit:

- `2000×2000` means 2000 horizontal blocks by 2000 horizontal blocks, not chunk
  count;
- the map is represented as a 125 by 125 chunk grid with 16-block chunks;
- viewer movement uses a bounded active window instead of loading the full map;
- the first active-window planner proves near-origin, center, edge, and
  far-corner logical coordinates;
- the runtime subgate uses the native `g8_2000x2000_sparse.wtworld` fixture with
  93 sparse chunk pages;
- Godot viewer movement across the logical 2000×2000 path must settle to
  9/25/25/25/9 active render/collision resources, no render fade blink
  resources, and no active-resource budget overflow.

## G9 - Sparse 2K playable profile

Status: complete by `WT_VALIDATION_G9_CONTRACT_PASS` and
`WT_VALIDATION_G9_SPARSE_2K_PLAYABLE_SMOKE_PASS`.

Exit:

- `g8_sparse_2k` is a selectable playable profile in the validation scene;
- the profile uses the native G8 `g8_2000x2000_sparse.wtworld` fixture;
- the normal first-person playtest path keeps player, camera, crosshair,
  collision, materialized terrain, scripted motion, and edit submission working;
- the profile submits five bounded G8 path viewers and settles to 93 active
  sparse path resources, not a full 125 by 125 map load;
- edit replacement keeps `render_fading_resources == 0`, preserving the no-blink
  policy from G8.

## G10 - Single-viewer 2K playable streaming

Status: complete by `WT_VALIDATION_G10_CONTRACT_PASS` and
`WT_VALIDATION_G10_SINGLE_VIEWER_2K_PLAYABLE_STREAMING_SMOKE_PASS`.

Exit:

- `g10_single_viewer_2k` is a selectable playable profile that uses the native
  G8 `g8_2000x2000_sparse.wtworld` fixture;
- the normal first-person playtest path starts with one active viewer, player,
  camera, crosshair, collision, materialized terrain, and human input disabled
  for autonomous validation;
- the smoke moves the same viewer ID through the G8 path and requires
  9/25/25/25/9 active render/collision resources;
- the playable-scene active budget is 25 resources for this sparse path and it
  does not keep all 93 sparse path resources active;
- scripted player motion and an active-center edit remain valid after streaming,
  with `render_fading_resources == 0`.

## G11 - Generated 16x16 playable streaming

Status: complete by `WT_VALIDATION_G11_CONTRACT_PASS` and
`WT_VALIDATION_G11_GENERATED_16X16_PLAYABLE_STREAMING_SMOKE_PASS`.

Exit:

- `g11_generated_16x16` is a selectable playable profile backed by a dense
  deterministic generated terrain fixture;
- the fixture is baked through `world-transvoxel/tools/wt_bake.py` and contains
  256 generated pages;
- the normal first-person playtest path starts with one active viewer, player,
  camera, crosshair, collision, materialized terrain, and human input disabled
  for autonomous validation;
- the smoke moves the same viewer ID through the 16 by 16 terrain and requires
  9/25/25/25/9 active render/collision resources;
- the playable-scene active budget remains 25 resources and does not load all
  256 generated pages as active resources;
- scripted player motion and an active-center edit remain valid after streaming,
  with `render_fading_resources == 0`.

## G12 - Generated 32x32 playable streaming

Status: complete by `WT_VALIDATION_G12_CONTRACT_PASS` and
`WT_VALIDATION_G12_GENERATED_32X32_PLAYABLE_STREAMING_SMOKE_PASS`.

Exit:

- `g12_generated_32x32` is a selectable playable profile backed by a dense
  deterministic generated terrain fixture;
- the fixture is baked through `world-transvoxel/tools/wt_bake.py` and contains
  1024 generated pages;
- the normal first-person playtest path starts with one active viewer, player,
  camera, crosshair, collision, materialized terrain, and human input disabled
  for autonomous validation;
- the smoke moves the same viewer ID through the 32 by 32 terrain and requires
  9/25/25/25/9 active render/collision resources;
- the playable-scene active budget remains 25 resources and does not load all
  1024 generated pages as active resources;
- scripted player motion and an active-center edit remain valid after streaming,
  with `render_fading_resources == 0`.

## G13 - Generated fixture vertical coverage guard

Status: complete by `WT_VALIDATION_G13_CONTRACT_PASS` and
`WT_VALIDATION_G13_GENERATED_FIXTURE_VERTICAL_COVERAGE_PASS`.

Exit:

- G11, G12, G14, and G16 generated fixture runners compute surface min/max height
  before bake;
- generated surfaces must remain inside the active vertical chunk with explicit
  lower and upper margins;
- G11, G12, G14, and G16 fixture reports include `vertical_coverage` metadata;
- reused generated fixtures must match the runner's expected `source_revision`;
- stale or vertically unsafe generated fixtures fail before Godot runtime smoke;
- this is a safety gate before larger generated terrain scale-up milestones.

## G14 - Generated 64x64 playable streaming

Status: complete by `WT_VALIDATION_G14_CONTRACT_PASS` and
`WT_VALIDATION_G14_GENERATED_64X64_PLAYABLE_STREAMING_SMOKE_PASS`.

Exit:

- `g14_generated_64x64` is a selectable playable profile backed by a dense
  deterministic generated terrain fixture;
- the fixture is baked through `world-transvoxel/tools/wt_bake.py` and contains
  4096 generated pages;
- generated source writing uses the streamed source writer instead of building
  one large in-memory bytearray;
- the normal first-person playtest path starts with one active viewer, player,
  camera, crosshair, collision, materialized terrain, and human input disabled
  for autonomous validation;
- the smoke moves the same viewer ID through the 64 by 64 terrain and requires
  9/25/25/25/9 active render/collision resources;
- the playable-scene active budget remains 25 resources and does not load all
  4096 generated pages as active resources;
- scripted player motion and an active-center edit remain valid after streaming,
  with `render_fading_resources == 0`.

## G15 - G14 scale telemetry guard

Status: complete when `WT_VALIDATION_G15_CONTRACT_PASS` and
`WT_VALIDATION_G15_G14_SCALE_TELEMETRY_PASS` both pass.

Exit:

- the G14 saved report is present and still describes `g14_generated_64x64`;
- the fixture is still 4096 generated pages at source revision `146400`;
- streamed source files have the expected byte sizes:
  `density.f32 = 275298660` and `materials.u16 = 137649330`;
- `keys.txt` contains exactly the 64 by 64 chunk-key set;
- vertical coverage margins remain inside the G13 safety policy;
- two engine runtime markers are present from the G14 smoke;
- runtime telemetry proves render and collision resources remain at or below the
  25 active-resource playable budget;
- edit replacement remains proven by the G14 runtime markers.

## G16 - Generated 128x128 playable streaming

Status: complete when `WT_VALIDATION_G16_CONTRACT_PASS` and
`WT_VALIDATION_G16_GENERATED_128X128_PLAYABLE_STREAMING_SMOKE_PASS` both pass.

Exit:

- `g16_generated_128x128` is a selectable playable profile backed by a dense
  deterministic near-2K generated terrain fixture;
- the fixture is baked through `world-transvoxel/tools/wt_bake.py` and contains
  16384 generated pages;
- generated source writing uses the streamed source writer;
- generated source sizes are checked before runtime:
  `density.f32 = 1095850340` and `materials.u16 = 547925170`;
- the G13 vertical coverage guard includes the G16 height field;
- the normal first-person playtest path starts with one active viewer, player,
  camera, crosshair, collision, materialized terrain, and human input disabled
  for autonomous validation;
- the smoke moves the same viewer ID through the 128 by 128 terrain and requires
  9/25/25/25/9 active render/collision resources;
- the playable-scene active budget remains 25 resources and does not load all
  16384 generated pages as active resources;
- scripted player motion and an active-center edit remain valid after streaming,
  with `render_fading_resources == 0`.

## G17 - Generated 128x128 human visual handoff

Status: complete when `WT_VALIDATION_G17_CONTRACT_PASS` and
`WT_VALIDATION_G17_GENERATED_128X128_HUMAN_HANDOFF_READY` both pass.

Exit:

- the saved G16 runtime report is present and still proves two engine runs;
- the handoff project is composed from current local addon sources;
- the G16 baked world is copied into the generated project;
- `validation_playtest.tscn` is pinned to `g16_generated_128x128`;
- Godot import passes before human review;
- the stress-fixture visual confirmation is human visual playtesting, recorded as
  `human_confirmation = pending`.

Boundary:

- G17 is a stress-fixture handoff only;
- G16 and G17 are stress-only evidence, not production terrain architecture;
- this does not make dense pre-baked near-2K terrain acceptable for normal game
  startup, storage, or distribution.

## G18 - Production terrain budget pivot

Status: complete when `WT_VALIDATION_G18_CONTRACT_PASS` and
`WT_VALIDATION_G18_WORLD_BUDGET_GUARD_PASS` both pass.

Exit:

- G16/G17 dense near-2K artifacts are classified as stress-only evidence;
- normal terrain/world files have a 100 MiB hard per-file ceiling and 50 MiB
  target per-file ceiling;
- normal load-to-play has a 30 second ceiling;
- raw dense source files are transient stress artifacts only;
- large terrain must move to deterministic-on-demand generation or compact
  seed/config plus edit journals;
- ignored oversized stress artifacts can be cleaned while committed reports and
  contracts remain.

## G19 - Compact 2K on-demand procedural streaming

Status: complete when `WT_VALIDATION_G19_CONTRACT_PASS` and
`WT_VALIDATION_G19_COMPACT_2K_ON_DEMAND_SMOKE_PASS` both pass.

Exit:

- `g19_compact_2k_on_demand` is a selectable playable profile using
  `DETERMINISTIC_REFERENCE` generation;
- the addons start a compact procedural world from chunk counts, seed, source
  revision, and object root, not a dense `.wtworld` manifest;
- the near-2K footprint remains 128 by 128 chunks, 16,384 indexed pages, or
  roughly 2048 by 2048 blocks;
- no dense source directory, baked world directory, `world.wtworld`,
  `streaming.wtworld`, or `procedural.wtseed` is produced for this path;
- the five-point playable streaming path remains bounded to 25 active render
  resources and 25 active collision resources;
- active-center carving commits and replaces render resources;
- generated runtime files stay inside the 50 MiB target per-file and 100 MiB
  total generated-object-root budget.

## G20 - Compact terrain resolution gate

Status: complete when `WT_VALIDATION_G20_CONTRACT_PASS` and
`WT_VALIDATION_G20_COMPACT_TERRAIN_RESOLUTION_PASS` both pass.

Exit:

- the G19 two-engine report exists and proves `g19_compact_2k_on_demand`;
- the compact near-2K terrain storage/load-shape problem is resolved within
  this validation boundary;
- the G18 budget guard still sees no oversized stress artifacts;
- G16/G17 remain stress-only historical evidence;
- the next terrain work must not reintroduce dense near-2K source/world files
  as the normal path.

Boundary:

- this does not claim final terrain art, dynamic LOD seam quality,
  GPU/compute generation, water, biomes, vegetation, buildings, multiplayer, or
  game repository readiness.

## G21 - Compact 2K human visual handoff

Status: complete when `WT_VALIDATION_G21_CONTRACT_PASS` and
`WT_VALIDATION_G21_COMPACT_2K_HUMAN_HANDOFF_READY` both pass.

Exit:

- the compact G19 near-2K project is composed from current local addon sources;
- `validation_playtest.tscn` is pinned to `g19_compact_2k_on_demand`;
- the project imports before human visual playtesting;
- the handoff report records `human_confirmation = pending`;
- G21 does not return to dense G16/G17 stress artifacts and does not claim a
  new terrain algorithm milestone.

Boundary:

- this is a human visual handoff gate only; it does not claim final terrain art,
  dynamic LOD seam quality, GPU/compute generation, water, biomes, vegetation,
  buildings, multiplayer, or game repository readiness.

## G22 - Exact compact handoff runtime proof

Status: complete when `WT_VALIDATION_G22_CONTRACT_PASS` and
`WT_VALIDATION_G22_EXACT_COMPACT_HANDOFF_RUNTIME_SMOKE_PASS` both pass.

Exit:

- the exact compact G21 handoff project is prepared from current local addon
  sources and imported before runtime proof;
- automated runtime disables human input from startup;
- runtime covers origin, center, and far-corner compact 2K positions;
- scripted movement, carve, and construct/place all commit;
- automated PNG captures are produced before human visual review;
- settled runtime reports `render_fading_resources = 0`;
- settled runtime reports `pending_chunk_retirements = 0`;
- active render and collision resources stay within the 25-resource budget;
- no dense source/world files are reintroduced.

Boundary:

- this proves the current compact handoff artifact runs and produces automated
  runtime/visual evidence; it does not claim final terrain art, dynamic LOD seam
  quality, GPU/compute generation, water, biomes, vegetation, buildings,
  multiplayer, or game repository readiness.

## G23 - Real compact human-playable streaming

Status: complete when `WT_VALIDATION_G23_CONTRACT_PASS` and
`WT_VALIDATION_G23_REAL_COMPACT_HUMAN_PLAYABLE_STREAMING_SMOKE_PASS` both pass.

Exit:

- `g19_compact_2k_on_demand` starts inside the map instead of on the clipped
  origin edge;
- startup settles to 25 active render and collision resources around the
  player;
- human input remains enabled in the compact playtest scene;
- mouse motion changes the first-person camera through the real scene input
  path;
- player movement drives terrain viewer updates and the active terrain window
  follows the moved player;
- left click carves and right click constructs/places through the terrain
  interactor input path;
- settled runtime reports `render_fading_resources = 0`;
- settled runtime reports `pending_chunk_retirements = 0`;
- no dense source/world files are reintroduced.

Boundary:

- this fixes the failed human handoff boundary and proves real compact
  player-driven streaming, but it does not claim final terrain art, dynamic LOD
  seam quality, GPU/compute generation, water, biomes, vegetation, buildings,
  multiplayer, or game repository readiness.
