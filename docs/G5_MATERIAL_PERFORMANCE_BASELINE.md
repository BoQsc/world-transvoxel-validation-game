# G5 Material and Performance Baseline

Status: complete by automated contract and runtime smoke when
`WT_VALIDATION_G5_CONTRACT_PASS` and `WT_VALIDATION_G5_SMOKE_PASS` both pass.

G5 proves that the validation game has a small material/texture path and records
baseline runtime behavior without assuming GPU compute is required.

## Exit evidence

- terrain materialization uses the backend mesh material IDs exposed in `UV2.x`;
- a small generated checker texture is used through a shader material;
- terrain material profile remains visible through the terrain addon debug
  snapshot and overlay;
- automated test disables human input;
- materialized terrain capture is saved;
- average and maximum frame times are measured after cold idle;
- the Python runner samples GPU watts with `nvidia-smi` when available;
- GPU burst/full-GPU paths remain future decisions, not assumptions.

## Not claimed

- final art direction;
- Poly Haven or other external production textures;
- biome material blending;
- compute shader acceleration;
- final watt or performance budget.
