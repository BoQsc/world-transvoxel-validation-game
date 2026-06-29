# G25 - Full terrain visual baseline

Status: complete when `WT_VALIDATION_G25_CONTRACT_PASS` and
`WT_VALIDATION_G25_FULL_TERRAIN_VISUAL_BASELINE_SMOKE_PASS` both pass.

G25 corrects the G24 boundary mistake. G19 through G24 proved compact
generation, bounded local streaming, movement, edit submission, and budget
behavior. They did not prove full-map terrain visibility. G25 is now the active
large-terrain visibility gate.

Exit:

- No human validation is requested until this gate passes;
- the compact `g19_compact_2k_on_demand` profile has full 2048 by 2048 terrain
  visual coverage in the generated playtest scene;
- the active window is only the local Transvoxel detail layer, not the full
  terrain success boundary;
- the full-map visual layer is provided by `world-transvoxel-terrain`, not hidden
  as a validation-game workaround;
- native authoritative sample queries confirm sampled full-map visual heights
  match the backend procedural source;
- an automated overview capture is written for the full terrain footprint;
- local native Transvoxel render/collision resources remain present for
  interaction and detailed terrain;
- dense near-2K source/world files are not reintroduced.

Commands:

```console
python tools/validate_g25_contract.py
python tools/g25_full_terrain_visual_baseline.py --skip-build
```

Expected markers:

```text
WT_VALIDATION_G25_CONTRACT_PASS implementation=full_terrain_visual_baseline
WT_VALIDATION_G25_FULL_TERRAIN_VISUAL_BASELINE_PASS profile=g19_compact_2k_on_demand pages=16384 map_blocks=2048 full_visual_blocks=2048x2048 full_visual_vertices=... full_visual_triangles=... native_render_resources=... native_collision_resources=... capture_colored_samples=... dense_world_files=0
WT_VALIDATION_G25_FULL_TERRAIN_VISUAL_BASELINE_SMOKE_PASS engines=2 max_engine_seconds=... report=artifacts/g25_full_terrain_visual_baseline/g25_full_terrain_visual_baseline_report.json
```

Boundary:

- G25 is still not final terrain art, seamless dynamic LOD approval, water,
  biomes, vegetation, buildings, GPU/compute generation, multiplayer, or game
  repository readiness.
- G25 does make the previous “tiny active island is large terrain” result
  unacceptable as a release or human-review claim.
