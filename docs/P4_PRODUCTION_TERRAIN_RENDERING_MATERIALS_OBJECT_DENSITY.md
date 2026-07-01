# P4 - Production terrain rendering, materials, and object-density foundation

Status: complete when `WT_VALIDATION_P4_CONTRACT_PASS` and
`WT_VALIDATION_P4_PRODUCTION_RENDERING_MATERIALS_OBJECT_DENSITY_PASS` both pass.

P4 closes these register gaps:

- `P4-TERRAIN-TEXTURES`
- `P4-RENDER-DENSITY`
- `P4-VISUAL-VALIDATION`

P4 decides `P4-EDITOR-UX` is not blocking P4. It moves editor UX hardening to
P5/P5A because production materials and rendering density can be proven without
claiming final editor authoring tools.

## Production material/texture foundation

The terrain addon now exposes a production material texture foundation beyond
the G51 checker baseline:

- real texture-slot contract: albedo, normal, roughness/ORM;
- sample material set: grass/ground, rock, sand/dirt, underground/stone;
- generated performance-conscious terrain atlases for the standard sample set;
- shader atlas sampling with material-id selection;
- explicit mapping, blending, and texture import policy fields;
- material quality summary fields for production texture slots and budgets.

## Rendering/object-density foundation

P4 does not implement vegetation, props, or buildings. It defines their
foundation:

- terrain visible work remains bounded by streaming active-resource capacity;
- future objects must be chunk/cell partitioned;
- one huge unculled object or vegetation resource is a failure;
- HLOD/visibility range/mesh LOD are presentation tools, not terrain
  correctness mechanisms;
- visible terrain chunks, entity cells, draw calls, instance counts, and frame
  cost are required telemetry for future object systems.

## Visual validation foundation

P4 keeps the existing technical gates as production guardrails:

- G43 covers compact 2K view-distance presentation;
- G51 covers material assignment stability through edits and streaming;
- G54 covers mixed LOD seam/artifact behavior;
- P4 adds static proof that the production texture pipeline is no longer only
  the 16 by 16 G51 checker/palette.

Expected marker:

```text
WT_VALIDATION_P4_PRODUCTION_RENDERING_MATERIALS_OBJECT_DENSITY_PASS texture_slots=3 sample_materials=4 material_pipeline=terrain_production_material_texture_pipeline_v1 render_density=1 visual_validation=1 editor_ux_moved_to_p5=1 next=P5_gpu_acceleration
```

Validator marker:

```text
WT_VALIDATION_P4_CONTRACT_PASS implementation=production_rendering_materials_object_density
```
