# G4 Terrain Edit Interaction

Status: complete by automated contract and runtime smoke when
`WT_VALIDATION_G4_CONTRACT_PASS` and `WT_VALIDATION_G4_SMOKE_PASS` both pass.

G4 proves that the validation game has a first-person terrain interaction
affordance and that automated edits go through the terrain addon/backend edit
path.

## Standard edit policy

- default dig shape: sphere;
- default place shape: sphere;
- standard backend-supported shapes for this milestone: sphere and box;
- capsule, plane, octahedron, or other shapes remain optional future policy
  decisions until they have backend support and measurements;
- left mouse button carves;
- right mouse button constructs/places material.

## Exit evidence

- validation playtest scene includes a `ValidationTerrainInteractor` node;
- human left/right mouse affordance exists for carve/place;
- automated test disables human input and submits carve/place through the same
  interactor node;
- edit commit, replacement, collision resource, and authoritative sample updates
  are verified;
- latency is measured as commit frames and cold-idle settle frames;
- place edit is persisted through backend revision state in the same run.

## Not claimed

- final digging feel;
- custom brush palette UI;
- restore-to-natural-terrain policy;
- structural stability, gravity, or debris;
- multiplayer edit replication.
