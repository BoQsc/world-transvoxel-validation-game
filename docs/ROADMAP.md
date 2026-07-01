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

## G24 - Autonomous large-terrain acceptance

Status: complete as capped active-window regression evidence when
`WT_VALIDATION_G24_CONTRACT_PASS` and
`WT_VALIDATION_G24_AUTONOMOUS_LARGE_TERRAIN_ACCEPTANCE_SMOKE_PASS` both pass.
G24 is superseded by G25 for large-terrain visibility.

Exit:

- No further human validation is requested from G24 alone;
- the compact `g19_compact_2k_on_demand` profile proves a 2048 by 2048 block
  terrain descriptor with 16,384 indexed pages;
- autonomous checks cover origin edge, interior quadrants, center, and far
  corner map-scale positions;
- every sampled position settles to the expected bounded active terrain window;
- player movement at every sampled position drives terrain viewer updates;
- first-person camera input changes camera rotation;
- left click carves and right click constructs/places through normal input;
- materialized colored captures are written for every sampled region;
- active render and collision resources never exceed 25 because this is a capped
  local active-window regression;
- settled runtime reports `render_fading_resources = 0`;
- settled runtime reports `pending_chunk_retirements = 0`;
- no dense near-2K source/world files are reintroduced.

Boundary:

- this is not the autonomous prerequisite before human review anymore;
- this does not prove full-map terrain visibility; G25 is required for that;
- this still does not claim final terrain art, seamless dynamic LOD, GPU/compute
  generation, fluids, biomes, vegetation, buildings, multiplayer, or a separate
  game repository.

## G25 - Full terrain visual baseline

Status: complete when `WT_VALIDATION_G25_CONTRACT_PASS` and
`WT_VALIDATION_G25_FULL_TERRAIN_VISUAL_BASELINE_SMOKE_PASS` both pass.

Exit:

- No human validation is requested until this gate passes;
- `g19_compact_2k_on_demand` has full 2048 by 2048 terrain visual coverage in
  the generated playtest scene;
- the full-map visual layer is provided by `world-transvoxel-terrain`;
- the active window is only the local Transvoxel detail layer for editable
  terrain and collision;
- native authoritative sample queries confirm sampled full-map visual heights
  match the backend procedural source;
- an automated full-map overview capture is written;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this restores the large-terrain visibility requirement, but it does not claim
  final terrain art, seamless dynamic LOD, GPU/compute generation, fluids,
  biomes, vegetation, buildings, multiplayer, or a separate game repository.

## G26 - Full terrain playable experience

Status: complete when `WT_VALIDATION_G26_CONTRACT_PASS` and
`WT_VALIDATION_G26_FULL_TERRAIN_PLAYABLE_EXPERIENCE_SMOKE_PASS` both pass.

Exit:

- No human validation is requested until this gate passes;
- this is the first-person full-terrain playable experience gate;
- human input is disabled for automation;
- player-driven viewer updates remain active when player movement is scripted;
- first-person player-eye captures are written at origin/center/far-map
  positions;
- every sampled position settles to the expected local native Transvoxel detail
  window;
- local active render/collision resources remain inside budget;
- terrain editing still commits through the normal interactor;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this proves first-person full-terrain validation-game behavior, but it does not
  claim final terrain art, seamless dynamic LOD, GPU/compute generation, fluids,
  biomes, vegetation, buildings, multiplayer, or a separate game repository.

## G27 - Full terrain handoff preflight

Status: complete when `WT_VALIDATION_G27_CONTRACT_PASS` and
`WT_VALIDATION_G27_FULL_TERRAIN_HANDOFF_PREFLIGHT_SMOKE_PASS` both pass.

Exit:

- No human validation is requested until this gate passes;
- this is the full-terrain human handoff preflight gate;
- the normal generated playtest scene is checked directly, not a test-only
  substitute;
- human input is disabled for automation from startup;
- player, camera, crosshair, interactor, full-map visual coverage, and local
  native Transvoxel detail are all present;
- event-driven material application happens automatically, includes a bounded
  material-repair audit for missing overrides, and then remains stable instead
  of reapplying every frame;
- scripted player movement updates the local native detail window;
- first-person captures are written before human review;
- terrain editing still commits through the normal interactor;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this proves automated handoff readiness for the current generated playtest
  project, but it does not claim final terrain art, seamless dynamic LOD,
  GPU/compute generation, fluids, biomes, vegetation, buildings, multiplayer, or
  a separate game repository.

## G28 - Normal project launch preflight

Status: complete when `WT_VALIDATION_G28_CONTRACT_PASS` and
`WT_VALIDATION_G28_NORMAL_PROJECT_LAUNCH_SMOKE_PASS` both pass.

Exit:

- No human validation is requested until this gate passes;
- this is the normal project launch preflight gate;
- the generated project's `run/main_scene` is `validation_playtest.tscn`;
- the scene is pinned to `g19_compact_2k_on_demand`;
- automation disables human input from startup in the generated scene file;
- Godot is launched with `--path`, not `--script`;
- the normal launch reaches `WT_VALIDATION_PLAYTEST_READY` within the 30 second
  load-to-ready ceiling;
- after automation, the generated handoff scene is restored to human input
  enabled;
- the normal launch logs no Godot errors;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this proves the generated handoff project starts through the path a human will
  use; it does not replace G27's capture/edit checks and does not claim final
  terrain art, seamless dynamic LOD, GPU/compute generation, fluids, biomes,
  vegetation, buildings, multiplayer, or a separate game repository.

## G29 - Compact 2K human-ready handoff

Status: complete when `WT_VALIDATION_G29_CONTRACT_PASS` and
`WT_VALIDATION_G29_COMPACT_2K_HUMAN_READY_HANDOFF_PASS` both pass.

Exit:

- No human validation is requested until this gate passes;
- this is the human-ready compact 2K handoff project gate;
- the generated handoff project is separate from automation-preflight projects;
- the scene is pinned to `g19_compact_2k_on_demand`;
- human input is enabled in the generated handoff scene;
- `project.godot` launches `res://scenes/validation_playtest.tscn`;
- current G27 and G28 prerequisite reports are present and match the current
  addon source commits;
- Godot import passes for the generated handoff project;
- `HUMAN_REVIEW.md` is written inside the generated project with controls,
  expected baseline, source commits, and known boundaries;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this prepares the current human review artifact; it does not claim human
  approval, final terrain art, seamless dynamic LOD, GPU/compute generation,
  fluids, biomes, vegetation, buildings, multiplayer, or a separate game
  repository.

## G30 - Compact 2K review bundle

Status: complete when `WT_VALIDATION_G30_CONTRACT_PASS` and
`WT_VALIDATION_G30_COMPACT_2K_REVIEW_BUNDLE_PASS` both pass.

Exit:

- No human validation is requested until this gate passes;
- this is the compact 2K review bundle gate;
- the human-ready G29 project is copied into `project/`;
- the bundled project keeps `human_input_enabled = true`;
- `project/HUMAN_REVIEW.md` remains present;
- `REVIEW_INDEX.md` explains what to open and what evidence is included;
- `HANDOFF_MANIFEST.json` records source commits, SHA-256 hashes, project
  budget, evidence budget, and prerequisite evidence files;
- G27, G28, and G29 reports/logs are copied into `evidence/`;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this prepares an auditable review bundle; it does not claim human approval,
  final terrain art, seamless dynamic LOD, GPU/compute generation, fluids,
  biomes, vegetation, buildings, multiplayer, or a separate game repository.

## G31 - Review bundle launch preflight

Status: complete when `WT_VALIDATION_G31_CONTRACT_PASS` and
`WT_VALIDATION_G31_REVIEW_BUNDLE_LAUNCH_SMOKE_PASS` both pass.

Exit:

- No human validation is requested until this gate passes;
- this is the review bundle launch preflight gate;
- the source G30 bundle remains human-input ready;
- `bundle_launch_copy` is created as a separate automation launch copy;
- stale `.godot` import cache is removed from the launch copy before import;
- automation disables human input only in the launch copy;
- Godot import passes for the launch copy;
- Godot launches the copied bundle project with `--path`, not `--script`;
- the copied bundle reaches `WT_VALIDATION_PLAYTEST_READY` within the 30 second
  ready ceiling;
- the copied bundle launch logs no Godot errors;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this proves copied-bundle launch readiness for review; it does not claim human
  approval, final terrain art, seamless dynamic LOD, GPU/compute generation,
  fluids, biomes, vegetation, buildings, multiplayer, or a separate game
  repository.

## G32 - Review bundle runtime proof

Status: complete when `WT_VALIDATION_G32_CONTRACT_PASS` and
`WT_VALIDATION_G32_REVIEW_BUNDLE_RUNTIME_SMOKE_PASS` both pass.

Exit:

- No human validation is requested until this gate passes;
- this is the exact review-bundle autonomous runtime proof gate;
- the source G30 bundle remains human-input ready;
- `bundle_runtime_copy` is created as a separate automation runtime copy;
- stale `.godot` import cache is removed from the runtime copy before import;
- automation disables human input only in the runtime copy;
- Godot import passes for the runtime copy;
- G25 full-terrain visual baseline passes from the runtime copy;
- G26 full-terrain playable experience passes from the runtime copy;
- G27 full-terrain handoff preflight passes from the runtime copy;
- runtime proof captures and logs are copied into G32 evidence;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this proves copied review-bundle runtime behavior for the current compact 2K
  handoff artifact; it does not claim human approval, final terrain art,
  seamless dynamic LOD, GPU/compute generation, fluids, biomes, vegetation,
  buildings, multiplayer, or a separate game repository.

## G33 - Runtime terrain quality gate

Status: complete when `WT_VALIDATION_G33_CONTRACT_PASS` and
`WT_VALIDATION_G33_RUNTIME_TERRAIN_QUALITY_PASS` both pass.

Exit:

- this is the active runtime terrain quality gate;
- this is not another human review package;
- G32 exact-bundle runtime evidence exists for at least two Godot engines;
- G25 full-terrain visual baseline evidence proves full 2048 by 2048 terrain
  visual coverage;
- G26 first-person playable experience evidence proves player-driven streaming,
  first-person captures, and bounded active resources;
- G27 full-terrain handoff preflight evidence proves material application,
  local edit commit behavior, first-person captures, and automation-safe input;
- each runtime script remains below the 30 second quality ceiling;
- every runtime check keeps the bounded 25-resource native detail window;
- copied PNG evidence exists on disk and is non-empty;
- generated compact terrain storage remains inside the 50 MB file and 100 MB
  total budget;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this turns the active track toward terrain quality instead of review packaging.
  It does not claim final terrain art, seamless dynamic LOD, GPU/compute
  generation, fluids, biomes, vegetation, buildings, multiplayer, or a separate
  game repository.

## G34 - Edit latency persistence quality

Status: complete when `WT_VALIDATION_G34_CONTRACT_PASS` and
`WT_VALIDATION_G34_EDIT_LATENCY_PERSISTENCE_SMOKE_PASS` both pass.

Exit:

- this is a runtime terrain quality gate;
- the compact 2K runtime state starts clean for each engine;
- carve and construct edits commit inside the frame and millisecond budgets;
- authoritative samples match edited density/material values before reload;
- the edit journal is created and remains inside compact storage budgets;
- a fresh scene reload replays both edits from persistent storage;
- terrain settles without pending retirements or render fade/blink resources;
- active render and collision resources remain bounded to 25;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this proves edit latency and persistence for the current compact CPU/native
  terrain path. It does not claim final terrain art, seamless dynamic LOD,
  GPU/compute generation, fluids, biomes, vegetation, buildings, multiplayer,
  or a separate game repository.

## G35 - Terrain correctness artifact quality

Status: complete when `WT_VALIDATION_G35_CONTRACT_PASS` and
`WT_VALIDATION_G35_TERRAIN_CORRECTNESS_ARTIFACT_SMOKE_PASS` both pass.

Exit:

- this is an active runtime terrain quality gate;
- full-map terrain visual mesh shape is exactly the expected compact 2K shape;
- surface samples are finite and inside the expected vertical range;
- neighbor and diagonal-pair samples stay below artifact thresholds;
- material samples stay inside the current terrain palette;
- backend authoritative samples match the full-map visual surface;
- full-map capture contains enough colored terrain samples;
- active render and collision resources remain bounded to 25;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this proves terrain correctness and artifact detection for the current compact
  CPU/native terrain path. It does not claim final terrain art, seamless dynamic
  LOD, GPU/compute generation, fluids, biomes, vegetation, buildings,
  multiplayer, or a separate game repository.

## G36 - Cold idle performance quality

Status: complete when `WT_VALIDATION_G36_CONTRACT_PASS` and
`WT_VALIDATION_G36_COLD_IDLE_PERFORMANCE_SMOKE_PASS` both pass.

Exit:

- this is an active runtime terrain quality gate;
- cold-idle performance stability is measured in the normal compact 2K runtime
  scene after the active detail window settles;
- viewer update count remains unchanged over 300 idle frames;
- edit replacement count remains unchanged without edits;
- material auto-apply count remains unchanged after material stability;
- render and collision resources remain bounded to 25;
- render queues, collision queues, pending retirements, and render fade/blink
  resources remain zero;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this proves cold-idle performance stability for the current compact CPU/native
  terrain path. It does not claim final terrain art, seamless dynamic LOD,
  GPU/compute generation, fluids, biomes, vegetation, buildings, multiplayer,
  or a separate game repository.

## G37 - Streaming movement performance quality

Status: complete when `WT_VALIDATION_G37_CONTRACT_PASS` and
`WT_VALIDATION_G37_STREAMING_MOVEMENT_PERFORMANCE_SMOKE_PASS` both pass.

Exit:

- this is an active runtime terrain quality gate;
- streaming movement performance quality is measured in the normal compact 2K
  runtime scene;
- five interior route samples across the compact 2K map are exercised;
- each route sample performs scripted player movement through the real player
  controller;
- each streaming transition settles within the frame budget;
- each settled active window returns to 25 render, collision, and chunk records;
- transient streaming overlap remains bounded to 50 records/resources;
- render fade/blink resources remain zero;
- material auto-apply churn remains bounded per route sample;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this proves movement-streaming behavior for the current compact CPU/native
  terrain path. It does not claim final terrain art, seamless dynamic LOD,
  GPU/compute generation, fluids, biomes, vegetation, buildings, multiplayer,
  or a separate game repository.

## G38 - Streaming endurance stability quality

Status: complete when `WT_VALIDATION_G38_CONTRACT_PASS` and
`WT_VALIDATION_G38_STREAMING_ENDURANCE_STABILITY_SMOKE_PASS` both pass.

Exit:

- this is an active runtime terrain quality gate;
- streaming endurance stability quality is measured in the normal compact 2K
  runtime scene;
- two route cycles exercise ten compact 2K route samples;
- each route sample performs scripted player movement through the real player;
- each settled active window returns to 25 render, collision, and chunk records;
- transient streaming overlap remains bounded to 50 records/resources;
- render fade/blink resources remain zero;
- final cold idle is true after the repeated route;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this proves repeated movement-streaming stability for the current compact
  CPU/native terrain path. It does not claim final terrain art, seamless dynamic
  LOD, GPU/compute generation, fluids, biomes, vegetation, buildings,
  multiplayer, or a separate game repository.

## G39 - Distributed edit streaming quality

Status: complete when `WT_VALIDATION_G39_CONTRACT_PASS` and
`WT_VALIDATION_G39_DISTRIBUTED_EDIT_STREAMING_SMOKE_PASS` both pass.

Exit:

- this is an active runtime terrain quality gate;
- distributed edit streaming quality is measured in the normal compact 2K
  runtime scene;
- four distant compact 2K edit sites are streamed to before editing;
- carve and construct edits both commit in distant regions;
- authoritative backend samples match the edited density/material at each site;
- a fresh scene reload replays all four distributed edits from the edit journal;
- the replay scene returns to cold idle with 25 render/collision resources;
- render fade/blink resources remain zero;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this proves distributed edit and replay behavior for the current compact
  CPU/native terrain path. It does not claim final terrain art, seamless dynamic
  LOD, GPU/compute generation, fluids, biomes, vegetation, buildings,
  multiplayer, or a separate game repository.

## G40 - Edit visual material feedback quality

Status: complete when `WT_VALIDATION_G40_CONTRACT_PASS` and
`WT_VALIDATION_G40_EDIT_VISUAL_MATERIAL_FEEDBACK_SMOKE_PASS` both pass.

Exit:

- this is an active runtime terrain quality gate;
- edit visual material feedback quality is measured in the normal compact 2K
  runtime scene;
- a focused terrain patch is captured before and after real edits;
- carve and construct edits commit through the terrain interactor;
- authoritative backend samples match the edited density/material values;
- the after-edit capture differs from the before-edit capture above threshold;
- material auto-application stabilizes after edit replacement;
- active render and collision resources remain bounded to 25;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this proves player-facing edit visual and material feedback for the current
  compact CPU/native terrain path. It does not claim final terrain art, seamless
  dynamic LOD, GPU/compute generation, fluids, biomes, vegetation, buildings,
  multiplayer, or a separate game repository.

## G41 - Runtime frame budget telemetry quality

Status: complete when `WT_VALIDATION_G41_CONTRACT_PASS` and
`WT_VALIDATION_G41_RUNTIME_FRAME_BUDGET_TELEMETRY_SMOKE_PASS` both pass.

Exit:

- this is an active runtime terrain quality gate;
- runtime frame budget telemetry quality is measured in the normal compact 2K
  runtime scene;
- telemetry covers settled idle, movement/streaming, real carve/construct edits,
  and reload after edits;
- at least five telemetry phases and at least 240 measured frames are recorded;
- every phase records average frame milliseconds and max frame milliseconds;
- maximum phase average frame time remains below the telemetry budget;
- maximum single-frame spike remains below the spike budget;
- transient active render, collision, and chunk records remain bounded to 50;
- render fade/blink resources remain zero;
- dense near-2K source/world files are not reintroduced;
- machine-readable telemetry JSON is written for later trend comparison.

Boundary:

- this creates the first runtime frame/update budget contract for the current
  compact CPU/native terrain path. It does not claim final optimization,
  seamless dynamic LOD, GPU/compute generation, fluids, biomes, vegetation,
  buildings, multiplayer, or a separate game repository.

## G42 - Collision traversal stability quality

Status: complete when `WT_VALIDATION_G42_CONTRACT_PASS` and
`WT_VALIDATION_G42_COLLISION_TRAVERSAL_STABILITY_SMOKE_PASS` both pass.

Exit:

- this is an active runtime terrain quality gate;
- collision traversal stability quality is measured through the real validation
  player controller;
- flat baseline, mountain/sloped, and edited compact 2K terrain cases are
  exercised;
- every case reaches the normal playable scene with human input disabled;
- scripted traversal keeps valid control state and camera state;
- total motion, floor contact ratio, off-floor streak, minimum player height,
  and vertical velocity remain within stability thresholds;
- the edited compact 2K case performs a real terrain edit before traversal;
- transient active resources stay bounded;
- render fade/blink resources remain zero;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this proves collision traversal stability for current validation profiles. It
  does not claim final character controller design, final terrain art, seamless
  dynamic LOD, GPU/compute generation, fluids, biomes, vegetation, buildings,
  multiplayer, or a separate game repository.

## G43 - View distance presentation quality

Status: complete when `WT_VALIDATION_G43_CONTRACT_PASS` and
`WT_VALIDATION_G43_VIEW_DISTANCE_PRESENTATION_SMOKE_PASS` both pass.

Exit:

- this is an active runtime terrain quality gate;
- view distance presentation quality is measured through first-person captures
  in the normal compact 2K runtime scene;
- the full terrain visual reports 2048 by 2048 block coverage;
- at least three map-scale first-person captures are written;
- every capture contains enough colored terrain samples;
- every capture spans enough horizontal and vertical image bins;
- every capture contains enough mid-band terrain samples for horizon/presentation
  coverage;
- local active render and collision resources remain bounded to 25;
- render fade/blink resources remain zero;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this detects tiny-patch or one-chunk-only first-person presentation regressions
  in the current compact CPU/native terrain path. It does not claim final art
  direction, final draw-distance policy, seamless dynamic LOD, GPU/compute
  generation, fluids, biomes, vegetation, buildings, multiplayer, or a separate
  game repository.

## G44 - Edit policy and shape quality

Status: complete when `WT_VALIDATION_G44_CONTRACT_PASS` and
`WT_VALIDATION_G44_EDIT_POLICY_SHAPE_SMOKE_PASS` both pass.

Exit:

- this is an active runtime terrain quality gate;
- edit policy and shape quality is measured in the normal compact 2K runtime
  scene;
- the validation edit policy exposes default shape, dig radius, place radius,
  place material, and alternate-shape-toggle status;
- default carve/place shape is sphere;
- dig and place radii are both 1.8;
- place material id is 4;
- alternate shape toggles are explicitly disabled for this validation gate;
- at least six repeated carve/construct edits commit through the terrain
  interactor;
- center and inside-radius authoritative samples match expected density/material
  behavior;
- outside-radius authoritative samples remain unchanged immediately after each
  edit;
- edits settle within commit and active-window budgets;
- render fade/blink resources and pending retirements remain zero;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this proves the current default sphere edit policy and repeated edit shape
  behavior. It does not claim full public terrain editing API stability, final
  mining design, non-sphere production brushes, fluids, biomes, vegetation,
  buildings, multiplayer, or a separate game repository.

## G45 - Storage recovery schema quality

Status: complete when `WT_VALIDATION_G45_CONTRACT_PASS` and
`WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_SMOKE_PASS` both pass.

Exit:

- this is a runtime terrain quality gate;
- compact 2K storage uses a compact deterministic descriptor plus versioned
  `world.wtedit` journal, not dense near-2K world files;
- journal format version is locked to schema `1`;
- physical journal bytes expose the schema-1 `WTEDIT` container header and
  expected source revision;
- compact 2K edits reload and replay from the journal;
- a simulated interrupted write with a truncated `WTEDIT` tail is recovered by
  reopening and truncating to the last complete transaction prefix;
- `WtTerrainWorld` exposes game-facing snapshot request wrappers;
- existing sparse 2K baked-fixture compaction writes a side-by-side snapshot, reopens it, and
  verifies the edited authoritative sample;
- compacted output starts without a carried edit journal;
- active resources return to the 25-resource compact detail window;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this proves compact 2K journal/reload/truncated-tail recovery and
  compaction/reopen through the existing sparse 2K baked fixture. It does not
  claim final save UI, cloud sync, massive world compaction, procedural-world
  compaction, public terrain API stability, materials/textures, LOD seam quality,
  water, vegetation, buildings, multiplayer, or a separate game repository.

## G46 - Terrain addon API contract quality

Status: complete when `WT_VALIDATION_G46_CONTRACT_PASS` and
`WT_VALIDATION_G46_TERRAIN_ADDON_API_CONTRACT_SMOKE_PASS` both pass.

Exit:

- this is a runtime terrain quality gate;
- `WtTerrainWorld` exposes minimal stable public lifecycle, profile, streaming,
  editing, storage, telemetry, and debug API groups;
- authoritative sample queries are exposed through public terrain addon methods
  and signals;
- the compact 2K validation runtime starts, streams, edits, samples, and reads
  debug/telemetry state through the public API path;
- the validation gate reports `direct_backend_calls=0`;
- active resources return to the 25-resource compact detail window;
- dense near-2K source/world files are not reintroduced.

Boundary:

- this locks the minimal public terrain addon API required by normal Godot game
  integration. It does not remove every old validation helper, finish material
  art, complete underground terrain, solve LOD seams, add fluids, vegetation,
  buildings, multiplayer, or prove a separate game repository.

## G47 - Validation workaround removal quality

Status: complete when `WT_VALIDATION_G47_CONTRACT_PASS` and
`WT_VALIDATION_G47_VALIDATION_WORKAROUND_REMOVAL_SMOKE_PASS` both pass.

Exit:

- this is a runtime terrain quality gate;
- validation-game material application and mesh-stat helpers that inspect
  terrain internals are moved into `world-transvoxel-terrain`;
- the validation scene uses addon-owned `WtTerrainMaterialApplicator`;
- the validation playtest uses addon-owned `WtTerrainMeshStats`;
- local validation-game copies of those terrain helpers are absent;
- normal validation runtime scripts do not call backend internals directly;
- remaining direct backend calls in historical tests are reported as
  quarantined audit evidence;
- the compact 2K validation scene still reaches ready state, applies terrain
  materials, reports mesh stats, and stays inside the 25-resource detail window.

Boundary:

- this removes required reusable material and mesh-inspection workarounds from
  the validation game. It does not rewrite every historical test, lock native
  hot-path boundaries, finish material art, solve underground terrain, LOD seams,
  fluids, vegetation, buildings, multiplayer, or a separate game repository.

## G48 - Native hot-path boundary quality

Status: complete when `WT_VALIDATION_G48_CONTRACT_PASS` and
`WT_VALIDATION_G48_NATIVE_HOT_PATH_BOUNDARY_SMOKE_PASS` both pass.

Exit:

- this is a runtime terrain quality gate;
- `WtTerrainWorld` exposes `get_hot_path_boundary_summary`;
- the boundary summary marks generation, meshing, streaming, edit application,
  and storage as native/backend-owned runtime hot paths;
- normal validation-game runtime scripts avoid direct backend calls and avoid
  GDScript density-volume, mesh-building, page-generation, source-file
  streaming, and image/pixel terrain loops;
- bounded GDScript helpers remain limited to public API wrappers, profile
  descriptors, edit-command validation, material/debug helpers, and telemetry
  summaries;
- the compact 2K validation scene starts, streams, commits one public edit,
  remains inside the 25-resource detail window, and reports
  `gdscript_hot_loops=0`.

Boundary:

- this locks the native hot-path ownership boundary for the current compact 2K
  CPU/native validation path. It does not finish debug telemetry UI, final
  terrain profiles, material textures, underground variation, large-world
  streaming radius, LOD seam quality, generator budgets, water, vegetation,
  buildings, multiplayer, compute acceleration, or separate game integration.

## G49 - Debug telemetry UI quality

Status: complete when `WT_VALIDATION_G49_CONTRACT_PASS` and
`WT_VALIDATION_G49_DEBUG_TELEMETRY_UI_SMOKE_PASS` both pass.

Exit:

- this is a runtime terrain quality gate;
- the normal validation playtest scene owns a lightweight debug telemetry
  overlay;
- the overlay exposes active chunks, queues, frame/update cost, edit state,
  material state, and storage state;
- the overlay is mouse-transparent and does not interfere with player input;
- telemetry can be exported as JSON for automated inspection;
- the compact 2K validation scene starts, streams, commits one public edit,
  updates the telemetry overlay, exports telemetry, and remains inside the
  25-resource detail window.

Boundary:

- this makes runtime problems observable in the current validation scene. It
  does not finish terrain profile standards, material textures, underground
  variation, large-world streaming radius, LOD seam quality, generator budgets,
  water, vegetation, buildings, multiplayer, compute acceleration, or separate
  game integration.

## G50 - Terrain profile standard quality

Status: complete when `WT_VALIDATION_G50_CONTRACT_PASS` and
`WT_VALIDATION_G50_TERRAIN_PROFILE_STANDARD_SMOKE_PASS` both pass.

Exit:

- this is a runtime terrain quality gate;
- the standard profile set is `flat_baseline`, `mountain_8x8`,
  `g19_compact_2k_on_demand`, and `g50_seeded_procedural_2k`;
- the standard profile contract exposes deterministic source mode, seed, source
  revision, chunk dimensions, storage paths, active-resource expectations, and
  load/storage budgets;
- the normal validation playtest scene runs all four profiles with human input
  and player-driven viewer updates disabled, so the gate measures the
  profile-defined viewer windows;
- all four profiles reach ready state, floor contact, cold idle, and their
  expected active-resource count;
- compact and seeded procedural 2K profiles use deterministic procedural
  descriptors and do not create dense `world.wtworld`, `streaming.wtworld`, or
  `procedural.wtseed` files;
- the G50 runner enforces the 30 second load-to-play ceiling, 50 MiB per-file
  target, and 100 MiB per-profile-directory ceiling.

Boundary:

- this locks terrain profile standards. It does not finish material textures,
  underground variation, large-world streaming radius, LOD seam quality,
  generator budgets, water, vegetation, buildings, multiplayer, compute
  acceleration, or separate game integration.

## G51 - Material texture pipeline quality

Status: complete when `WT_VALIDATION_G51_CONTRACT_PASS` and
`WT_VALIDATION_G51_MATERIAL_TEXTURE_PIPELINE_SMOKE_PASS` both pass.

Exit:

- this is a runtime terrain quality gate;
- `WtTerrainMaterialProfile` exposes `terrain_material_profile_contract_v1`;
- `WtTerrainMaterialApplicator` exposes `terrain_material_texture_pipeline_v1`;
- the normal compact 2K validation path uses the UV2 material-id shader path;
- the standard generated checker texture is deterministic, 16 by 16 `RGBA8`,
  and 1024 bytes under the 4 KiB G51 budget;
- the standard palette IDs are `1,2,3,4,7`;
- all active compact 2K terrain meshes receive the same shared material instance;
- the material instance remains stable after a real construct edit and after two
  explicit viewer-streaming windows;
- an authoritative sample after construct observes material ID `4`;
- automated capture evidence shows colored terrain material output.

Boundary:

- this locks the current deterministic small material/texture pipeline. It does
  not finish final terrain art, external texture packs, biome materials,
  underground material variation, large-world streaming radius, LOD seam quality,
  generator budgets, water, vegetation, buildings, multiplayer, compute
  acceleration, or separate game integration.

## G52 - Underground terrain variation quality

Status: complete when `WT_VALIDATION_G52_CONTRACT_PASS` and
`WT_VALIDATION_G52_UNDERGROUND_TERRAIN_VARIATION_SMOKE_PASS` both pass.

Exit:

- this is a runtime terrain quality gate;
- the native procedural compact terrain source exposes
  `density_volume_vertical_strata_v1`;
- underground material strata are deterministic: deep `1`, mid stone `7`, and
  shallow subsoil `4`;
- authoritative sample batches prove same-column density ordering from
  underground solid to above-surface air;
- a local underground carve changes the target voxel density without rewriting
  unaffected deeper strata;
- the flat baseline also exposes volumetric density samples through the public
  terrain-world authoritative sample API;
- no dense near-2K source/world files are required in the normal compact path.

Boundary:

- this locks the baseline underground density/material variation proof. It does
  not finish deep vertical worlds, caves, ore veins, mining progression, biome
  ecosystems, large-world streaming radius, LOD seam quality, generator budgets,
  water, vegetation, buildings, multiplayer, compute acceleration, or separate
  game integration.

## G53 - Large-world streaming radius quality

Status: complete when `WT_VALIDATION_G53_CONTRACT_PASS` and
`WT_VALIDATION_G53_LARGE_WORLD_STREAMING_RADIUS_SMOKE_PASS` both pass.

Exit:

- this is a runtime terrain quality gate;
- the compact 2K public viewer path accepts configurable radii 1, 2, 4, and 6;
- active/render resources settle exactly to 9, 25, 81, and 169;
- active resources remain inside capacity 256;
- radius-edge chunks are fully ready and chunks just outside the selected radius
  are absent;
- visible terrain mesh spread grows as radius grows;
- no dense near-2K source/world files are required in the normal compact path.

Boundary:

- this locks configurable streaming-radius behavior for the current compact 2K
  CPU/native path. It does not finish LOD seam quality, generator budgets,
  water, vegetation, buildings, multiplayer, compute acceleration, or separate
  game integration.

## G54 - LOD seam and artifact quality

Status: complete when `WT_VALIDATION_G54_CONTRACT_PASS` and
`WT_VALIDATION_G54_LOD_SEAM_ARTIFACT_SMOKE_PASS` both pass.

Exit:

- this is a runtime terrain quality gate;
- the native production LOD streaming proof reports
  `PRODUCTION_LOD_STREAMING_PASS`;
- the Godot runtime starts the 28-page mixed LOD transition fixture;
- `maximum_lod=1` produces both LOD0 and LOD1 render meshes;
- coarse bridge and fine seam-neighbor chunks become fully ready;
- horizontal LOD seam pairs are detected from actual render mesh names and
  chunk coordinates;
- boundary vertices exist on both sides of the LOD seam and stay under the seam
  gap tolerance;
- diagonal mesh edges are present and bounded before and after the LOD topology
  change;
- an edited seam remains stable and a post-edit topology change remeshes
  transition geometry;
- no dense near-2K source/world files are required in the normal compact path.

Boundary:

- this locks mixed LOD seam/artifact behavior for the current CPU/native
  transition fixture. It does not finish generator budgets, water, vegetation,
  buildings, multiplayer, compute acceleration, or separate game integration.
