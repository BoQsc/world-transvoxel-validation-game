# G49 - Debug telemetry UI quality

Status: complete when `WT_VALIDATION_G49_CONTRACT_PASS` and
`WT_VALIDATION_G49_DEBUG_TELEMETRY_UI_SMOKE_PASS` both pass.

G49 makes the normal validation playtest expose runtime state directly. The
goal is early problem detection: active chunks, queues, frame/update cost,
edit state, material state, and storage state must be visible without requiring
manual code tracing.

## Required evidence

- the normal validation playtest scene owns a debug telemetry overlay;
- the overlay reports `active_chunks`, `queues`, `frame_update`, `edit_state`,
  `material_state`, and `storage_state`;
- the overlay is mouse-transparent and does not take player input;
- telemetry can be exported as JSON for automated inspection;
- the compact 2K runtime scene starts, streams, commits one public edit, updates
  the overlay, exports telemetry, and stays inside the 25-resource detail window.

## Commands

```console
python tools/validate_g49_contract.py
python tools/g49_debug_telemetry_ui_quality.py
```

## Expected markers

```text
WT_VALIDATION_G49_CONTRACT_PASS implementation=debug_telemetry_ui_quality
WT_VALIDATION_G49_DEBUG_TELEMETRY_UI_PASS profile=g19_compact_2k_on_demand categories=6 overlay=1 exported=1 active_chunks=25 queued_render=0 queued_collision=0 frame_samples=... edit_committed=1 materialized=... storage_visible=1 dense_world_files=0
WT_VALIDATION_G49_DEBUG_TELEMETRY_UI_SMOKE_PASS profile=g19_compact_2k_on_demand engines=... categories=6 overlay=1 exported=1 quality_track=runtime_terrain dense_world_files=0 report=artifacts/g49_debug_telemetry_ui_quality/g49_debug_telemetry_ui_quality_report.json
```

## Boundary

G49 proves the current compact 2K validation scene has useful debug telemetry
visibility and export. It does not finish terrain profile standards, material
textures, underground variation, large-world streaming radius, LOD seam quality,
map-generator budgets, water, vegetation, buildings, multiplayer, compute
acceleration, or separate game integration.
