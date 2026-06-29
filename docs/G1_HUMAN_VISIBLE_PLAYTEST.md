# G1 Human-Visible Playtest

Status: active.

Markers:

```text
WT_VALIDATION_G1_CONTRACT_PASS implementation=human_visible_playtest_guard next=human_rerun_confirmation
WT_VALIDATION_G1_GODOT_PASS state=ready terrain_meshes=1 implementation=human_visible_playtest_guard
WT_VALIDATION_G1_SMOKE_PASS engines=2 report=artifacts/g1_visible_playtest/g1_visible_playtest_report.json
WT_VALIDATION_G1_VISUAL_CAPTURE_RUN_PASS engines=2 report=artifacts/g1_visual_capture/g1_visual_capture_report.json
```

## Problem observed

The first human run only showed a gray rectangle. That was not enough for visual
validation. The playtest scene must clearly show whether terrain rendering is
present and must not ask a human to infer status from a blank panel.

## G1 changes

G1 makes the scene human-usable:

- targets the camera at the validation viewer position;
- composes into `artifacts/g1_visible_playtest/project` so the smoke does not
  need to delete a human-open `artifacts/validation_project`;
- adds unshaded orientation markers for X, Y, Z, and the viewer position;
- adds a small playable `CharacterBody3D` with visible body, collision shape,
  WASD movement, jump, first-person camera, and crosshair;
- adds a dedicated validation status overlay below the addon debug overlay;
- records a failed state if no terrain MeshInstance3D exists under the backend
  terrain node;
- adds an automated guard that instantiates the visible playtest scene and
  checks the ready status plus terrain mesh, triangle, collision, player, and
  scripted-motion counts;
- adds a windowed visual capture check that saves the rendered viewport and
  rejects a blank, gray-only, terrain-off-center, or player-not-visible capture.

## Automated evidence

The G1 automated guard passes on Godot 4.6.3 and Godot 4.7:

```text
WT_VALIDATION_G1_SMOKE_PASS engines=2 report=artifacts/g1_visible_playtest/g1_visible_playtest_report.json
WT_VALIDATION_G1_VISUAL_CAPTURE_RUN_PASS engines=2 report=artifacts/g1_visual_capture/g1_visual_capture_report.json
```

The guard confirms the scene reaches ready state and reports nonzero terrain
mesh and triangle counts. The capture confirms that the rendered viewport
contains non-gray marker/status pixels, centered terrain-bright pixels, and
visible player pixels, then writes
`artifacts/g1_visual_capture/godot-4.7-capture.png` for inspection. Human rerun
confirmation is still useful because G1 is about the actual visible experience,
not only the programmatic mesh count.

## Boundary

G1 still does not claim terrain quality, final camera controls, production
performance, or correct 2000×2000-block world visuals. It only makes the human-visible
validation scene informative enough to continue review.
