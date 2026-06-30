# G27 - Full terrain handoff preflight

Status: complete when `WT_VALIDATION_G27_CONTRACT_PASS` and
`WT_VALIDATION_G27_FULL_TERRAIN_HANDOFF_PREFLIGHT_SMOKE_PASS` both pass.

G27 is the full-terrain human handoff preflight gate. It checks the normal
generated playtest scene that a human would open after G26, rather than relying
on a test-only workaround. The gate verifies that the composed project can reach
a playable, full-terrain state with automation input disabled.

Exit:

- No human validation is requested until this gate passes;
- the normal generated playtest scene is pinned to `g19_compact_2k_on_demand`;
- human input is disabled for automation from startup;
- the player, first-person camera, crosshair, terrain interactor, local native
  Transvoxel detail window, and full-map visual layer are all present;
- full 2048 by 2048 terrain visual coverage is visible;
- event-driven material application happens automatically, includes a bounded
  material-repair audit for missing overrides, and then remains stable instead
  of reapplying every frame;
- scripted player movement updates the local native detail window;
- first-person captures are written before human review;
- terrain editing still commits through the normal interactor;
- dense near-2K source/world files are not reintroduced.

Run:

```console
python tools/validate_g27_contract.py
python tools/g27_full_terrain_handoff_preflight.py --skip-build
```

Expected markers:

```text
WT_VALIDATION_G27_CONTRACT_PASS implementation=full_terrain_handoff_preflight
WT_VALIDATION_G27_FULL_TERRAIN_HANDOFF_PREFLIGHT_PASS profile=g19_compact_2k_on_demand pages=16384 map_blocks=2048 captures=2 material_auto_applies=... player_stream_updates=... max_render_resources=25 max_collision_resources=25 human_input=false full_visual_visible=true dense_world_files=0
WT_VALIDATION_G27_FULL_TERRAIN_HANDOFF_PREFLIGHT_SMOKE_PASS engines=2 max_engine_seconds=... project=... scene=res://scenes/validation_playtest.tscn report=artifacts/g27_full_terrain_handoff_preflight/g27_full_terrain_handoff_preflight_report.json
```

Boundary:

- this is the automated preflight before renewed human review; it does not claim
  final terrain art, seamless dynamic LOD, GPU/compute generation, fluids,
  biomes, vegetation, buildings, multiplayer, or a separate game repository.
