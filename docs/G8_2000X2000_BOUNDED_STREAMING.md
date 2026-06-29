# G8 2000×2000 Bounded Streaming

Status: active. The first G8 subgate is complete when
`WT_VALIDATION_G8_CONTRACT_PASS` and `WT_VALIDATION_G8_WINDOW_PLAN_PASS` pass.

## Goal

G8 begins the real scale path without pretending that the current 8 by 8
fixtures are large terrain. The target map is a logical 2000×2000 block area:

- 2000 blocks by 2000 blocks;
- baseline scale is 1 block = 1 meter;
- real horizontal size is about 2 km by 2 km;
- area is 4,000,000 m², or 4 km².

The standard implementation must stream a bounded active window around viewers.
It must not load, mesh, render, or collide the whole 2000×2000 area at once.

## First subgate

The first G8 subgate proves the coordinate and active-window contract:

- chunk size is 16 blocks;
- 2000 blocks require 125 chunks along X and 125 chunks along Z;
- logical map bounds are inclusive block coordinates 0..1999 on X and Z;
- active chunk windows clamp to the map bounds;
- a radius-2 single-viewer surface window contains at most 25 horizontal chunk
  columns;
- the default active chunk budget is 256 records, leaving room for vertical
  bands, transition support, and future multi-viewer expansion;
- the test path touches near-origin, center, edge, and far-corner coordinates.

Expected markers:

```text
WT_VALIDATION_G8_CONTRACT_PASS implementation=bounded_2000x2000_streaming next=g8_runtime_active_window
WT_VALIDATION_G8_WINDOW_PLAN_PASS map_blocks=2000 chunk_grid=125x125 max_window_columns=25 active_budget=256
```

## Not claimed yet

This subgate does not claim rendered 2000×2000 terrain, full map baking,
water/lava, vegetation, buildings, compute shaders, multiplayer, or final
performance. The next G8 subgate must attach this bounded-window policy to real
runtime viewer movement and active resource telemetry.
