# G9 Sparse 2K Playable Profile

Status: complete by `WT_VALIDATION_G9_CONTRACT_PASS` and
`WT_VALIDATION_G9_SPARSE_2K_PLAYABLE_SMOKE_PASS`.

## Goal

G9 connects the G8 bounded 2000×2000 sparse runtime fixture to the normal
playable validation scene. This proves that the same scene path used for human
playtesting can load the sparse 2K fixture through `world-transvoxel-terrain`,
not only through a low-level `WorldTransvoxelTerrain` smoke.

## Scope

The `g8_sparse_2k` playable profile:

- uses `res://build/production-lifecycle-fixture/g8_2000x2000_sparse.wtworld`;
- keeps the logical map vocabulary at 2000 blocks by 2000 blocks;
- submits five bounded radius-2 viewer windows along the G8 path;
- expects exactly 93 active sparse path resources, not a full 125 by 125 chunk
  map load;
- keeps first-person player, camera, crosshair, terrain collision, materialized
  terrain meshes, scripted player motion, and terrain edit submission working;
- requires `render_fading_resources == 0` after edits so the white blink effect
  stays rejected.

Expected markers:

```text
WT_VALIDATION_G9_CONTRACT_PASS implementation=sparse_2k_playable_profile
WT_VALIDATION_G9_SPARSE_2K_PLAYABLE_PASS profile=g8_sparse_2k resources=93 viewers=5 triangles=... materialized=93 edit_replacements=1
WT_VALIDATION_G9_SPARSE_2K_PLAYABLE_SMOKE_PASS engines=2 report=artifacts/g9_sparse_2k_playable_profile/g9_sparse_2k_playable_profile_report.json
```

## Not claimed yet

G9 still does not claim a fully generated visible 2000×2000 terrain surface,
continuous player-driven streaming across every map coordinate, water/lava,
vegetation, buildings, compute shaders, multiplayer, or final performance. It
does prove that the playable scene can consume the sparse 2K path fixture with
bounded resources and standard player/material/edit systems intact.
