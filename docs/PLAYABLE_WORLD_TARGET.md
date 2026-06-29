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

## Required before final human visual handoff

- first-person player with crosshair and terrain interaction affordances;
- flat terrain baseline as the default reproducible mode;
- mountain/8 by 8 multi-chunk generation mode for scale and visual validation;
- digging and placing with measured latency and deterministic recovery policy;
- textured terrain material path with small, performance-conscious test assets;
- terrain collision, chunking, cold-idle behavior, and visible-runtime telemetry;
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
