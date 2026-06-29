# G2 First-Person Playable Baseline

Status: complete by automated contract and runtime smoke when
`WT_VALIDATION_G2_CONTRACT_PASS` and `WT_VALIDATION_G2_SMOKE_PASS` both pass.

G2 exists to prove the validation game has a real first-person baseline before
larger generation modes, edits, materials, fluids, GPU work, or game-world
systems are added.

## Exit evidence

- first-person camera is the default human play view;
- crosshair is present;
- flat generation profile is explicitly selected as the default reproducible
  baseline;
- generated project supports player walking against terrain collision;
- generated project supports scripted jump response with human input disabled;
- terrain mesh triangles and collision resources are nonzero;
- automated visual capture remains available through the G1 overview capture.

## Not claimed

- 2000×2000-block terrain;
- mountain generation;
- terrain dig/place;
- material/textured terrain;
- production performance.
