# G3 Terrain Generation Modes

Status: complete by automated contract and runtime smoke when
`WT_VALIDATION_G3_CONTRACT_PASS` and `WT_VALIDATION_G3_SMOKE_PASS` both pass.

G3 proves that the validation game can generate and load more than the tiny
single-reference terrain slice without moving into final 2000×2000-block
performance claims.

## Exit evidence

- flat 8 by 8 fixture remains selectable as `flat_8x8`;
- deterministic mountain 8 by 8 fixture exists as `mountain_8x8`;
- both profiles bake through the standard `world-transvoxel` dense bake path;
- each baked profile contains an 8 by 8 LOD0 page set;
- Godot loads both profiles from generated artifacts;
- cold-idle, render resources, collision resources, and nonzero triangle counts
  are checked for both profiles;
- captures are saved for both flat and mountain modes;
- mountain geometry has a larger vertical span than the flat baseline.

## Not claimed

- 2K map scale, meaning 2000 by 2000 horizontal blocks at the standard
  baseline of 1 block = 1 meter;
- streaming while the player moves across the full map;
- terrain edit/dig/place;
- material/textured terrain;
- final performance or watt budget.
