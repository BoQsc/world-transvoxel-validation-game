# World Transvoxel Validation Game

Small Godot validation project for `world-transvoxel-terrain`.

Status: G0 install/run validation complete. G1 playable terrain/player guard
passes programmatically; G2 first-person flat baseline passes programmatically;
G3 flat/mountain generation modes pass programmatically; G4 terrain edit
interaction passes programmatically; G5 material/performance baseline passes
programmatically; G6 8 by 8 multi-chunk profile-selectable playable world passes
programmatically. G7 human visual verification handoff is reproducible;
final human profile review remains pending. G8 bounded 2000×2000 streaming has
an active-window planner and now requires a real Godot/native runtime active
window smoke. G9 sparse 2K playable profile and G10 single-viewer 2K playable
streaming pass programmatically through the normal validation playtest scene.
G11 generated 16 by 16 and G12 generated 32 by 32 playable streaming are tracked
as dense generated terrain scale-up gates. G13 locks generated fixture vertical
coverage and source-revision guards before larger generated scale-ups. G14 adds
the 64 by 64 dense generated terrain scale step with streamed source writing.
G15 locks G14 scale telemetry before another generated-terrain scale jump.
G16 is the 128 by 128 dense generated near-2K playable streaming gate.
G17 prepares that G16 profile for stress visual playtesting only.
G18 production budget pivot reclassifies G16/G17 as stress-only evidence and
requires compact deterministic/on-demand terrain before larger game claims.
G19 implements that compact near-2K on-demand path through the addons without
dense source/world files.
G20 closes the compact terrain storage/load-shape issue: within the near-2K
validation boundary, dense source/world files are no longer the normal path and
the compact path is timed against the 30 second load-to-play ceiling.
G21 prepares the compact G19 project for human visual playtesting without
returning to the dense G16 stress handoff.
G22 runs the exact compact G21 handoff project before human review, captures
automated PNG evidence, and proves movement plus carve/place runtime behavior.
G23 fixes the failed human handoff by requiring player-driven streaming and
real input-path camera/dig/place checks in the compact project.
G24 is now reclassified as a capped active-window regression, not the full
large-terrain proof. G25 replaces G24 as the active large-terrain visibility gate
and requires full 2048 by 2048 terrain visual coverage while the active native
Transvoxel window remains only the local editable/collision detail layer.
G26 is the active first-person full-terrain playable-experience gate: it checks
full terrain from player-eye captures while local Transvoxel detail follows
scripted player movement with human input disabled.
G27 is the active full-terrain human handoff preflight gate: it checks the
normal generated playtest scene directly, proves event-driven material
application plus bounded material-repair audit, captures first-person evidence,
and rejects dense near-2K files before human review.
G28 is the active normal project launch preflight gate: it launches the
generated handoff project through `project.godot`, disables human input for
automation, reaches the normal playtest scene without `--script`, restores human
input for handoff, and rejects dense near-2K files before human review.
G29 is the active compact 2K human-ready handoff gate: it creates a separate
human-ready generated project, verifies current G27/G28 prerequisite reports,
imports the project, writes `HUMAN_REVIEW.md`, and leaves human input enabled
for review.
G30 is the active compact 2K review bundle gate: it packages the human-ready
project, G27/G28/G29 evidence, `REVIEW_INDEX.md`, and `HANDOFF_MANIFEST.json`
with hashes into one auditable directory.
G31 is the active review bundle launch preflight gate: it copies the G30 bundle
to `bundle_launch_copy`, disables human input only in that automation copy,
reimports it from a clean Godot cache, and launches it through `project.godot`.
G32 is the active exact review-bundle autonomous runtime proof gate: it copies
the G30 bundle to `bundle_runtime_copy` and runs G25, G26, and G27 from that
copied review artifact before human review.
G33 is the active runtime terrain quality gate: it audits the G32 runtime
evidence for full 2048 by 2048 terrain coverage, first-person route evidence,
bounded active resources, edit/material behavior, copied PNG evidence, and
runtime ceilings. Human-visible review is not the active project direction.
G34 is the active edit latency and persistence quality gate: it times carve and
construct edits, verifies authoritative samples, writes the edit journal, reloads
the scene, and proves the edits replay from persistent storage.
G35 is the active terrain correctness and artifact detection quality gate: it
checks full-map surface continuity, material palette bounds, backend/visual
height agreement, capture evidence, and bounded active resources.
G36 is the active cold-idle performance quality gate: it holds the compact 2K
runtime scene idle for 300 frames and proves there is no viewer-update churn,
edit-replacement churn, material reapplication churn, queue work, retirements,
or render fade/blink resources after settling.
G37 is the active streaming movement performance quality gate: it drives the
real validation player across five interior compact 2K route samples, performs
scripted local movement at each sample, and measures streaming settle frames,
settled active-resource bounds, transient overlap bounds, fade/blink resources,
and material-apply churn.
G38 is the active streaming endurance stability quality gate: it repeats the
compact 2K route for two cycles, verifies ten streaming samples with real local
player movement, and requires the terrain to return to final cold idle with the
standard 25-resource active window.
G39 is the active distributed edit streaming quality gate: it streams to four
distant compact 2K regions, applies real carve/construct edits, verifies
authoritative samples, reloads the scene, and verifies all four edits replay
from the journal.
G40 is the active edit visual material feedback quality gate: it captures a
focused terrain patch before and after real edits, requires visible image delta,
verifies material stability, and checks authoritative edited samples.
G41 is the latest completed runtime frame budget telemetry quality gate: it
measures idle, movement/streaming, edit, and reload phase frame/update costs in
the compact 2K runtime scene.
G42 is the latest completed collision traversal stability quality gate: it
drives the real player over flat, mountain/sloped, and edited compact 2K terrain
while checking floor contact, control state, vertical stability, and
active-resource bounds.
G43 is the latest completed view distance presentation quality gate: it captures
multiple first-person compact 2K views and rejects tiny one-chunk-only
presentation.
G44 is the latest completed edit policy and shape quality gate: it locks the default
sphere carve/place policy and verifies repeated edit shape behavior with
authoritative samples.
G45 is the latest completed storage recovery schema quality gate: it verifies compact
storage policy, journal versioning, reload, truncated-tail recovery, and
compaction/reopen behavior.
G46 is the latest completed terrain addon API contract quality gate: it locks
the minimal public `WtTerrainWorld` API for lifecycle, profiles, streaming,
editing, storage, telemetry, debug snapshots, and authoritative sample queries.
G47 is the latest completed validation workaround removal quality gate: it moves
required material and mesh-inspection helpers into `world-transvoxel-terrain`
and audits historical backend-facing tests as quarantined evidence.
G48 is the latest completed native hot-path boundary quality gate: it exposes
the addon hot-path boundary through `WtTerrainWorld`, verifies native/backend
ownership for generation, meshing, streaming, edit application, and storage, and
rejects GDScript terrain hot loops in normal runtime paths.
G49 is the latest completed debug telemetry UI quality gate: it adds a
mouse-transparent telemetry overlay and JSON export to the normal validation
playtest scene for active chunks, queues, frame/update cost, edit state,
material state, and storage state.
Current claim boundary after G49: automated validation-grade compact 2K terrain
runtime with measured frame/update telemetry, collision traversal stability, and
view-distance presentation coverage plus default sphere edit policy/repeated edit
shape validation plus compact storage recovery schema evidence and a minimal
game-facing terrain addon API contract plus validation-workaround removal
evidence plus native hot-path boundary evidence and debug telemetry UI evidence,
not production-ready large-world terrain.
The production gap is tracked
in
[`docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md`](docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md).
The finite Terrain 1.0 roadmap is tracked in
[`docs/FINITE_PRODUCTION_ROADMAP.md`](docs/FINITE_PRODUCTION_ROADMAP.md) as
G41 through G60.
This repository is not the sandbox and not a production game. Its job is to
import `world-transvoxel` and
`world-transvoxel-terrain` as addons, run real game-facing integration paths,
and report every failure back to the addon repositories instead of hiding
workarounds here.

## Boundary

- `world-transvoxel` remains the low-level MIT-backed Transvoxel addon.
- `world-transvoxel-terrain` remains the reusable terrain addon.
- This repository validates game-project integration only.
- Do not fork or copy `world-transvoxel-sandbox`.
- Do not add production gameplay systems, fluids, planets, vegetation, GPU
  compute, or 0BSD backend replacement here before their contracts exist.
- The larger target is tracked in
  [`docs/PLAYABLE_WORLD_TARGET.md`](docs/PLAYABLE_WORLD_TARGET.md).
- The current production-readiness gap is tracked in
  [`docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md`](docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md).
- The finite Terrain 1.0 roadmap is tracked in
  [`docs/FINITE_PRODUCTION_ROADMAP.md`](docs/FINITE_PRODUCTION_ROADMAP.md).

## Validate

The committed repository does not vendor addon source. The validation tools
build ignored Godot projects under `artifacts/.../project` from sibling local
repos.

```console
python tools/validate_g0_contract.py
python tools/root_project_safe_import.py
python tools/g0_install_run_smoke.py
python tools/validate_playable_world_target.py
python tools/validate_production_gap_audit.py
python tools/validate_finite_production_roadmap.py
python tools/validate_g1_contract.py
python tools/g1_visible_playtest_smoke.py
python tools/g1_visual_capture.py --windowed
python tools/validate_g2_contract.py
python tools/g2_first_person_baseline_smoke.py
python tools/validate_g3_contract.py
python tools/g3_generation_modes_smoke.py --windowed
python tools/validate_g4_contract.py
python tools/g4_edit_interaction_smoke.py
python tools/validate_g5_contract.py
python tools/g5_material_performance_smoke.py --windowed
python tools/validate_g6_contract.py
python tools/g6_profile_selectable_playable_world_smoke.py --windowed
python tools/human_input_capture_smoke.py
python tools/prepare_human_playtest.py --profile flat_8x8 --reuse-bake
python tools/validate_g7_contract.py
python tools/g7_human_visual_handoff.py --reuse-bake --import-projects
python tools/validate_g8_contract.py
python tools/g8_2000x2000_window_plan.py
python tools/g8_runtime_active_window_smoke.py
python tools/validate_g9_contract.py
python tools/g9_sparse_2k_playable_profile_smoke.py
python tools/validate_g10_contract.py
python tools/g10_single_viewer_2k_playable_streaming_smoke.py
python tools/validate_g11_contract.py
python tools/g11_generated_16x16_playable_streaming_smoke.py
python tools/validate_g12_contract.py
python tools/g12_generated_32x32_playable_streaming_smoke.py
python tools/validate_g13_contract.py
python tools/g13_generated_fixture_vertical_coverage_smoke.py
python tools/validate_g14_contract.py
python tools/g14_generated_64x64_playable_streaming_smoke.py
python tools/validate_g15_contract.py
python tools/g15_g14_scale_telemetry_guard.py
python tools/validate_g16_contract.py
python tools/g16_generated_128x128_playable_streaming_smoke.py
python tools/validate_g17_contract.py
python tools/g17_generated_128x128_human_handoff.py --import-project
python tools/validate_g18_contract.py
python tools/g18_world_budget_guard.py
python tools/validate_g19_contract.py
python tools/g19_compact_2k_on_demand_smoke.py
python tools/validate_g20_contract.py
python tools/g20_compact_terrain_resolution.py
python tools/validate_g21_contract.py
python tools/g21_compact_2k_human_handoff.py --import-project
python tools/validate_g22_contract.py
python tools/g22_exact_compact_handoff_runtime_proof.py --skip-build
python tools/validate_g23_contract.py
python tools/g23_real_compact_human_playable_streaming.py --skip-build
python tools/validate_g24_contract.py
python tools/g24_autonomous_large_terrain_acceptance.py --skip-build
python tools/validate_g25_contract.py
python tools/g25_full_terrain_visual_baseline.py --skip-build
python tools/validate_g26_contract.py
python tools/g26_full_terrain_playable_experience.py --skip-build
python tools/validate_g27_contract.py
python tools/g27_full_terrain_handoff_preflight.py --skip-build
python tools/validate_g28_contract.py
python tools/g28_normal_project_launch_preflight.py --skip-build
python tools/validate_g29_contract.py
python tools/g29_compact_2k_human_ready_handoff.py --skip-build
python tools/validate_g30_contract.py
python tools/g30_compact_2k_review_bundle.py
python tools/validate_g31_contract.py
python tools/g31_review_bundle_launch_preflight.py
python tools/validate_g32_contract.py
python tools/g32_review_bundle_runtime_proof.py
python tools/validate_g33_contract.py
python tools/g33_runtime_terrain_quality_gate.py
python tools/validate_g34_contract.py
python tools/g34_edit_latency_persistence_quality.py
python tools/validate_g35_contract.py
python tools/g35_terrain_correctness_artifact_quality.py
python tools/validate_g36_contract.py
python tools/g36_cold_idle_performance_quality.py
python tools/validate_g37_contract.py
python tools/g37_streaming_movement_performance_quality.py
python tools/validate_g38_contract.py
python tools/g38_streaming_endurance_stability_quality.py
python tools/validate_g39_contract.py
python tools/g39_distributed_edit_streaming_quality.py
python tools/validate_g40_contract.py
python tools/g40_edit_visual_material_feedback_quality.py
python tools/validate_g41_contract.py
python tools/g41_runtime_frame_budget_telemetry_quality.py
python tools/validate_g42_contract.py
python tools/g42_collision_traversal_stability_quality.py
python tools/validate_g43_contract.py
python tools/g43_view_distance_presentation_quality.py
python tools/validate_g44_contract.py
python tools/g44_edit_policy_shape_quality.py
python tools/validate_g45_contract.py
python tools/g45_storage_recovery_schema_quality.py
python tools/validate_g46_contract.py
python tools/g46_terrain_addon_api_contract_quality.py
python tools/validate_g47_contract.py
python tools/g47_validation_workaround_removal_quality.py
python tools/validate_active_track_guardrails.py
```

Expected marker:

```text
WT_VALIDATION_G0_CONTRACT_PASS implementation=install_run_validation_scaffold next=human_visible_playtest_confirmation
WT_VALIDATION_ROOT_PROJECT_SAFE_IMPORT_PASS engines=2 report=artifacts/root_project_safe_import/root_project_safe_import_report.json
WT_VALIDATION_G0_SMOKE_PASS engines=2 report=artifacts/g0_install_run_smoke/g0_install_run_smoke_report.json
WT_VALIDATION_PLAYABLE_WORLD_TARGET_PASS next=native_hot_path_boundary_quality
WT_VALIDATION_PRODUCTION_GAP_AUDIT_PASS next=native_hot_path_boundary_quality
WT_VALIDATION_FINITE_PRODUCTION_ROADMAP_PASS first=G41 final=G60 terrain_1_0=true
WT_VALIDATION_G1_CONTRACT_PASS implementation=human_visible_playtest_guard next=human_rerun_confirmation
WT_VALIDATION_G1_SMOKE_PASS engines=2 report=artifacts/g1_visible_playtest/g1_visible_playtest_report.json
WT_VALIDATION_G1_VISUAL_CAPTURE_RUN_PASS engines=2 report=artifacts/g1_visual_capture/g1_visual_capture_report.json
WT_VALIDATION_G2_CONTRACT_PASS implementation=first_person_flat_baseline next=g3_terrain_generation_modes
WT_VALIDATION_G2_SMOKE_PASS engines=2 report=artifacts/g2_first_person_baseline/g2_first_person_baseline_report.json
WT_VALIDATION_G3_CONTRACT_PASS implementation=flat_and_mountain_baked_generation_modes next=g4_terrain_edit_interaction
WT_VALIDATION_G3_SMOKE_PASS profiles=2 engines=2 report=artifacts/g3_generation_modes/g3_generation_modes_report.json
WT_VALIDATION_G4_CONTRACT_PASS implementation=first_person_edit_interaction next=g5_material_performance_baseline
WT_VALIDATION_G4_SMOKE_PASS engines=2 report=artifacts/g4_edit_interaction/g4_edit_interaction_report.json
WT_VALIDATION_G5_CONTRACT_PASS implementation=materialized_performance_baseline next=g6_profile_selectable_playable_world
WT_VALIDATION_G5_SMOKE_PASS engines=2 report=artifacts/g5_material_performance/g5_material_performance_report.json
WT_VALIDATION_G6_CONTRACT_PASS implementation=profile_selectable_playable_world next=human_visual_verification
WT_VALIDATION_G6_SMOKE_PASS profiles=2 engines=2 report=artifacts/g6_profile_selectable_playable_world/g6_profile_selectable_playable_world_report.json
WT_VALIDATION_HUMAN_INPUT_CAPTURE_SMOKE_PASS engines=2 report=artifacts/human_input_capture/human_input_capture_report.json
WT_VALIDATION_HUMAN_PLAYTEST_READY profile=flat_8x8 project=... scene=res://scenes/validation_playtest.tscn launch=false fullscreen=false report=artifacts/human_playtest/human_playtest_report.json
WT_VALIDATION_G7_CONTRACT_PASS implementation=human_visual_handoff next=human_profile_review
WT_VALIDATION_G7_HANDOFF_READY profiles=2 imported=true report=artifacts/g7_human_visual_handoff/g7_human_visual_handoff_report.json
WT_VALIDATION_G8_CONTRACT_PASS implementation=bounded_2000x2000_streaming runtime=required
WT_VALIDATION_G8_WINDOW_PLAN_PASS map_blocks=2000 chunk_grid=125x125 max_window_columns=25 active_budget=256
WT_VALIDATION_G8_RUNTIME_ACTIVE_WINDOW_PASS pages=93 samples=5 max_render_resources=25 max_collision_resources=25 active_budget=256
WT_VALIDATION_G8_RUNTIME_SMOKE_PASS engines=2 report=artifacts/g8_runtime_active_window/g8_runtime_active_window_report.json
WT_VALIDATION_G9_CONTRACT_PASS implementation=sparse_2k_playable_profile
WT_VALIDATION_G9_SPARSE_2K_PLAYABLE_PASS profile=g8_sparse_2k resources=93 viewers=5 triangles=... materialized=93 edit_replacements=1
WT_VALIDATION_G9_SPARSE_2K_PLAYABLE_SMOKE_PASS engines=2 report=artifacts/g9_sparse_2k_playable_profile/g9_sparse_2k_playable_profile_report.json
WT_VALIDATION_G10_CONTRACT_PASS implementation=single_viewer_2k_playable_streaming
WT_VALIDATION_G10_SINGLE_VIEWER_2K_PLAYABLE_STREAMING_PASS profile=g10_single_viewer_2k samples=5 pages=93 max_render_resources=25 max_collision_resources=25 edit_replacements=...
WT_VALIDATION_G10_SINGLE_VIEWER_2K_PLAYABLE_STREAMING_SMOKE_PASS engines=2 report=artifacts/g10_single_viewer_2k_playable_streaming/g10_single_viewer_2k_playable_streaming_report.json
WT_VALIDATION_G11_CONTRACT_PASS implementation=generated_16x16_playable_streaming
WT_VALIDATION_G11_GENERATED_16X16_PLAYABLE_STREAMING_PASS profile=g11_generated_16x16 samples=5 pages=256 max_render_resources=25 max_collision_resources=25 edit_replacements=...
WT_VALIDATION_G11_GENERATED_16X16_PLAYABLE_STREAMING_SMOKE_PASS engines=2 report=artifacts/g11_generated_16x16_playable_streaming/g11_generated_16x16_playable_streaming_report.json
WT_VALIDATION_G12_CONTRACT_PASS implementation=generated_32x32_playable_streaming
WT_VALIDATION_G12_GENERATED_32X32_PLAYABLE_STREAMING_PASS profile=g12_generated_32x32 samples=5 pages=1024 max_render_resources=25 max_collision_resources=25 edit_replacements=...
WT_VALIDATION_G12_GENERATED_32X32_PLAYABLE_STREAMING_SMOKE_PASS engines=2 report=artifacts/g12_generated_32x32_playable_streaming/g12_generated_32x32_playable_streaming_report.json
WT_VALIDATION_G13_CONTRACT_PASS implementation=generated_fixture_vertical_coverage_guard
WT_VALIDATION_G13_GENERATED_FIXTURE_VERTICAL_COVERAGE_PASS profiles=4 active_y=0.0..16.0 required_lower_margin=1.00 required_upper_margin=0.75 report=artifacts/g13_generated_fixture_vertical_coverage/g13_generated_fixture_vertical_coverage_report.json
WT_VALIDATION_G14_CONTRACT_PASS implementation=generated_64x64_playable_streaming
WT_VALIDATION_G14_GENERATED_64X64_PLAYABLE_STREAMING_PASS profile=g14_generated_64x64 samples=5 pages=4096 max_render_resources=25 max_collision_resources=25 edit_replacements=...
WT_VALIDATION_G14_GENERATED_64X64_PLAYABLE_STREAMING_SMOKE_PASS engines=2 report=artifacts/g14_generated_64x64_playable_streaming/g14_generated_64x64_playable_streaming_report.json
WT_VALIDATION_G15_CONTRACT_PASS implementation=g14_scale_telemetry_guard
WT_VALIDATION_G15_G14_SCALE_TELEMETRY_PASS pages=4096 engines=2 density_bytes=275298660 materials_bytes=137649330 max_render_resources=25 max_collision_resources=25 report=artifacts/g15_g14_scale_telemetry/g15_g14_scale_telemetry_report.json
WT_VALIDATION_G16_CONTRACT_PASS implementation=generated_128x128_playable_streaming
WT_VALIDATION_G16_GENERATED_128X128_PLAYABLE_STREAMING_PASS profile=g16_generated_128x128 samples=5 pages=16384 max_render_resources=25 max_collision_resources=25 edit_replacements=...
WT_VALIDATION_G16_GENERATED_128X128_PLAYABLE_STREAMING_SMOKE_PASS engines=2 report=artifacts/g16_generated_128x128_playable_streaming/g16_generated_128x128_playable_streaming_report.json
WT_VALIDATION_G17_CONTRACT_PASS implementation=generated_128x128_human_handoff
WT_VALIDATION_G17_GENERATED_128X128_HUMAN_HANDOFF_READY profile=g16_generated_128x128 imported=true project=... scene=res://scenes/validation_playtest.tscn fullscreen=false report=artifacts/g17_generated_128x128_human_handoff/g17_generated_128x128_human_handoff_report.json
WT_VALIDATION_G18_CONTRACT_PASS implementation=production_terrain_budget_pivot
WT_VALIDATION_G18_WORLD_BUDGET_GUARD_PASS production_ready=false max_file_mb=100 target_file_mb=50 load_to_play_seconds=30 oversized_stress_artifacts=... report=artifacts/g18_world_budget_guard/g18_world_budget_guard_report.json
WT_VALIDATION_G19_CONTRACT_PASS implementation=compact_2k_on_demand
WT_VALIDATION_G19_COMPACT_2K_ON_DEMAND_PASS profile=g19_compact_2k_on_demand samples=5 pages=16384 max_render_resources=25 max_collision_resources=25 edit_replacements=... dense_world_files=0
WT_VALIDATION_G19_COMPACT_2K_ON_DEMAND_SMOKE_PASS engines=2 max_file_bytes=... total_bytes=... max_engine_seconds=... report=artifacts/g19_compact_2k_on_demand/g19_compact_2k_on_demand_report.json
WT_VALIDATION_G20_CONTRACT_PASS implementation=compact_terrain_resolution
WT_VALIDATION_G20_COMPACT_TERRAIN_RESOLUTION_PASS compact_path_resolved=true map_blocks=2048 active_budget=25 engines=2 max_file_bytes=... total_bytes=... max_engine_ms=... report=artifacts/g19_compact_2k_on_demand/g19_compact_2k_on_demand_report.json
WT_VALIDATION_G21_CONTRACT_PASS implementation=compact_2k_human_handoff
WT_VALIDATION_G21_COMPACT_2K_HUMAN_HANDOFF_READY profile=g19_compact_2k_on_demand imported=true project=... scene=res://scenes/validation_playtest.tscn fullscreen=false report=artifacts/g21_compact_2k_human_handoff/g21_compact_2k_human_handoff_report.json
WT_VALIDATION_G22_CONTRACT_PASS implementation=exact_compact_handoff_runtime_proof
WT_VALIDATION_G22_EXACT_COMPACT_HANDOFF_RUNTIME_PASS profile=g19_compact_2k_on_demand captures=3 pages=16384 max_render_resources=25 max_collision_resources=25 edit_replacements=... construct_verified=1 pending_retirements=0 render_fading_resources=0 dense_world_files=0
WT_VALIDATION_G22_EXACT_COMPACT_HANDOFF_RUNTIME_SMOKE_PASS engines=2 captures=... max_file_bytes=... total_bytes=... max_engine_seconds=... report=artifacts/g22_exact_compact_handoff_runtime_proof/g22_exact_compact_handoff_runtime_proof_report.json
WT_VALIDATION_G23_CONTRACT_PASS implementation=real_compact_human_playable_streaming
WT_VALIDATION_G23_REAL_COMPACT_HUMAN_PLAYABLE_STREAMING_PASS profile=g19_compact_2k_on_demand initial_resources=25 viewer_updates_delta=... player_motion=... camera_delta=... click_edits=2 pending_retirements=0 render_fading_resources=0 dense_world_files=0
WT_VALIDATION_G23_REAL_COMPACT_HUMAN_PLAYABLE_STREAMING_SMOKE_PASS engines=2 max_engine_seconds=... report=artifacts/g23_real_compact_human_playable_streaming/g23_real_compact_human_playable_streaming_report.json
WT_VALIDATION_G24_CONTRACT_PASS implementation=autonomous_large_terrain_acceptance
WT_VALIDATION_G24_AUTONOMOUS_LARGE_TERRAIN_ACCEPTANCE_PASS profile=g19_compact_2k_on_demand samples=... pages=16384 map_blocks=2048 max_render_resources=25 max_collision_resources=25 player_stream_updates=... camera_delta=... click_edits=2 captures=... dense_world_files=0
WT_VALIDATION_G24_AUTONOMOUS_LARGE_TERRAIN_ACCEPTANCE_SMOKE_PASS engines=2 max_engine_seconds=... report=artifacts/g24_autonomous_large_terrain_acceptance/g24_autonomous_large_terrain_acceptance_report.json
WT_VALIDATION_G25_CONTRACT_PASS implementation=full_terrain_visual_baseline
WT_VALIDATION_G25_FULL_TERRAIN_VISUAL_BASELINE_PASS profile=g19_compact_2k_on_demand pages=16384 map_blocks=2048 full_visual_blocks=2048x2048 full_visual_vertices=... full_visual_triangles=... native_render_resources=... native_collision_resources=... capture_colored_samples=... dense_world_files=0
WT_VALIDATION_G25_FULL_TERRAIN_VISUAL_BASELINE_SMOKE_PASS engines=2 max_engine_seconds=... report=artifacts/g25_full_terrain_visual_baseline/g25_full_terrain_visual_baseline_report.json
WT_VALIDATION_G26_CONTRACT_PASS implementation=full_terrain_playable_experience
WT_VALIDATION_G26_FULL_TERRAIN_PLAYABLE_EXPERIENCE_PASS profile=g19_compact_2k_on_demand pages=16384 map_blocks=2048 captures=3 player_stream_updates=... max_render_resources=25 max_collision_resources=25 full_visual_visible=true dense_world_files=0
WT_VALIDATION_G26_FULL_TERRAIN_PLAYABLE_EXPERIENCE_SMOKE_PASS engines=2 max_engine_seconds=... report=artifacts/g26_full_terrain_playable_experience/g26_full_terrain_playable_experience_report.json
WT_VALIDATION_G27_CONTRACT_PASS implementation=full_terrain_handoff_preflight
WT_VALIDATION_G27_FULL_TERRAIN_HANDOFF_PREFLIGHT_PASS profile=g19_compact_2k_on_demand pages=16384 map_blocks=2048 captures=2 material_auto_applies=... player_stream_updates=... max_render_resources=25 max_collision_resources=25 human_input=false full_visual_visible=true dense_world_files=0
WT_VALIDATION_G27_FULL_TERRAIN_HANDOFF_PREFLIGHT_SMOKE_PASS engines=2 max_engine_seconds=... project=... scene=res://scenes/validation_playtest.tscn report=artifacts/g27_full_terrain_handoff_preflight/g27_full_terrain_handoff_preflight_report.json
WT_VALIDATION_G28_CONTRACT_PASS implementation=normal_project_launch_preflight
WT_VALIDATION_G28_NORMAL_PROJECT_LAUNCH_PASS profile=g19_compact_2k_on_demand main_scene=res://scenes/validation_playtest.tscn human_input=false engines=2 max_ready_seconds=... handoff_human_input_restored=true dense_world_files=0
WT_VALIDATION_G28_NORMAL_PROJECT_LAUNCH_SMOKE_PASS engines=2 max_ready_seconds=... report=artifacts/g28_normal_project_launch_preflight/g28_normal_project_launch_preflight_report.json
WT_VALIDATION_G29_CONTRACT_PASS implementation=compact_2k_human_ready_handoff
WT_VALIDATION_G29_COMPACT_2K_HUMAN_READY_HANDOFF_PASS profile=g19_compact_2k_on_demand project=... scene=res://scenes/validation_playtest.tscn human_input=true imported_engines=2 review=HUMAN_REVIEW.md dense_world_files=0 report=artifacts/g29_compact_2k_human_ready_handoff/g29_compact_2k_human_ready_handoff_report.json
WT_VALIDATION_G30_CONTRACT_PASS implementation=compact_2k_review_bundle
WT_VALIDATION_G30_COMPACT_2K_REVIEW_BUNDLE_PASS profile=g19_compact_2k_on_demand project=project/project.godot manifest=HANDOFF_MANIFEST.json index=REVIEW_INDEX.md evidence_files=... project_files=... total_bytes=... dense_world_files=0
WT_VALIDATION_G31_CONTRACT_PASS implementation=review_bundle_launch_preflight
WT_VALIDATION_G31_REVIEW_BUNDLE_LAUNCH_PASS profile=g19_compact_2k_on_demand engines=2 max_ready_seconds=... launch_copy_human_input=false source_bundle_human_input=true dense_world_files=0
WT_VALIDATION_G31_REVIEW_BUNDLE_LAUNCH_SMOKE_PASS engines=2 max_ready_seconds=... report=artifacts/g31_review_bundle_launch_preflight/g31_review_bundle_launch_preflight_report.json
WT_VALIDATION_G32_CONTRACT_PASS implementation=review_bundle_runtime_proof
WT_VALIDATION_G32_REVIEW_BUNDLE_RUNTIME_PASS profile=g19_compact_2k_on_demand engines=2 scripts=6 exact_review_bundle=true g25=true g26=true g27=true map_blocks=2048 max_script_seconds=... runtime_copy_human_input=false source_bundle_human_input=true dense_world_files=0
WT_VALIDATION_G32_REVIEW_BUNDLE_RUNTIME_SMOKE_PASS engines=2 scripts=6 max_script_seconds=... report=artifacts/g32_review_bundle_runtime_proof/g32_review_bundle_runtime_proof_report.json
WT_VALIDATION_G33_CONTRACT_PASS implementation=runtime_terrain_quality_gate
WT_VALIDATION_G33_RUNTIME_TERRAIN_QUALITY_PASS profile=g19_compact_2k_on_demand engines=2 g25=2 g26=2 g27=2 map_blocks=2048 max_active_resources=25 max_script_seconds=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g33_runtime_terrain_quality_gate/g33_runtime_terrain_quality_gate_report.json
WT_VALIDATION_G34_CONTRACT_PASS implementation=edit_latency_persistence_quality
WT_VALIDATION_G34_EDIT_LATENCY_PERSISTENCE_PASS profile=g19_compact_2k_on_demand edits=2 replayed=2 max_commit_frames=... max_settle_frames=... max_commit_ms=... max_settle_ms=... journal_bytes=... max_render_resources=25 max_collision_resources=25 dense_world_files=0
WT_VALIDATION_G34_EDIT_LATENCY_PERSISTENCE_SMOKE_PASS profile=g19_compact_2k_on_demand engines=2 edits=2 replayed=2 max_commit_frames=... max_settle_frames=... max_commit_ms=... max_settle_ms=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g34_edit_latency_persistence_quality/g34_edit_latency_persistence_quality_report.json
WT_VALIDATION_G35_CONTRACT_PASS implementation=terrain_correctness_artifact_quality
WT_VALIDATION_G35_TERRAIN_CORRECTNESS_ARTIFACT_PASS profile=g19_compact_2k_on_demand map_blocks=2048 surface_samples=... backend_samples=... max_backend_height_error=... min_height=... max_height=... max_neighbor_delta=... max_diagonal_pair_delta=... material_ids=... capture_colored_samples=... max_render_resources=25 max_collision_resources=25 dense_world_files=0
WT_VALIDATION_G35_TERRAIN_CORRECTNESS_ARTIFACT_SMOKE_PASS profile=g19_compact_2k_on_demand engines=2 map_blocks=2048 max_backend_height_error=... max_neighbor_delta=... max_diagonal_pair_delta=... min_height=... max_height=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g35_terrain_correctness_artifact_quality/g35_terrain_correctness_artifact_quality_report.json
WT_VALIDATION_G36_CONTRACT_PASS implementation=cold_idle_performance_quality
WT_VALIDATION_G36_COLD_IDLE_PERFORMANCE_PASS profile=g19_compact_2k_on_demand idle_frames=300 viewer_update_delta=0 edit_replacement_delta=0 material_auto_apply_delta=0 max_render_resources=25 max_collision_resources=25 max_active_records=25 max_queued_render=0 max_queued_collision=0 max_pending_retirements=0 max_render_fading_resources=0 cold_idle=true dense_world_files=0
WT_VALIDATION_G36_COLD_IDLE_PERFORMANCE_SMOKE_PASS profile=g19_compact_2k_on_demand engines=2 idle_frames=300 viewer_update_delta=0 edit_replacement_delta=0 material_auto_apply_delta=0 max_render_resources=25 max_collision_resources=25 max_active_records=25 quality_track=runtime_terrain dense_world_files=0 report=artifacts/g36_cold_idle_performance_quality/g36_cold_idle_performance_quality_report.json
WT_VALIDATION_G37_CONTRACT_PASS implementation=streaming_movement_performance_quality
WT_VALIDATION_G37_STREAMING_MOVEMENT_PERFORMANCE_PASS profile=g19_compact_2k_on_demand route_samples=5 local_motion_samples=5 total_player_motion=... viewer_updates_delta=... max_settle_frames=... max_render_resources=... max_collision_resources=... max_active_records=... max_queued_render=... max_queued_collision=... max_pending_retirements=... max_render_fading_resources=0 max_material_auto_apply_delta=... dense_world_files=0
WT_VALIDATION_G37_STREAMING_MOVEMENT_PERFORMANCE_SMOKE_PASS profile=g19_compact_2k_on_demand engines=2 route_samples=5 max_settle_frames=... min_total_player_motion=... max_render_resources=... max_collision_resources=... max_active_records=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g37_streaming_movement_performance_quality/g37_streaming_movement_performance_quality_report.json
WT_VALIDATION_G38_CONTRACT_PASS implementation=streaming_endurance_stability_quality
WT_VALIDATION_G38_STREAMING_ENDURANCE_STABILITY_PASS profile=g19_compact_2k_on_demand route_cycles=2 route_samples=10 local_motion_samples=10 total_player_motion=... viewer_updates_delta=... max_settle_frames=... max_render_resources=... max_collision_resources=... max_active_records=... max_pending_retirements=... max_render_fading_resources=0 final_render_resources=25 final_collision_resources=25 final_active_records=25 final_cold_idle=true dense_world_files=0
WT_VALIDATION_G38_STREAMING_ENDURANCE_STABILITY_SMOKE_PASS profile=g19_compact_2k_on_demand engines=2 route_cycles=2 route_samples=10 max_settle_frames=... min_total_player_motion=... final_cold_idle=true quality_track=runtime_terrain dense_world_files=0 report=artifacts/g38_streaming_endurance_stability_quality/g38_streaming_endurance_stability_quality_report.json
WT_VALIDATION_G39_CONTRACT_PASS implementation=distributed_edit_streaming_quality
WT_VALIDATION_G39_DISTRIBUTED_EDIT_STREAMING_PASS profile=g19_compact_2k_on_demand edit_sites=4 replayed=4 max_commit_frames=... max_settle_frames=... journal_bytes=... max_render_resources=25 max_collision_resources=25 final_render_resources=25 final_collision_resources=25 final_cold_idle=true dense_world_files=0
WT_VALIDATION_G39_DISTRIBUTED_EDIT_STREAMING_SMOKE_PASS profile=g19_compact_2k_on_demand engines=2 edit_sites=4 replayed=4 max_commit_frames=... max_settle_frames=... final_cold_idle=true quality_track=runtime_terrain dense_world_files=0 report=artifacts/g39_distributed_edit_streaming_quality/g39_distributed_edit_streaming_quality_report.json
WT_VALIDATION_G40_CONTRACT_PASS implementation=edit_visual_material_feedback_quality
WT_VALIDATION_G40_EDIT_VISUAL_MATERIAL_FEEDBACK_PASS profile=g19_compact_2k_on_demand edits=2 changed_samples=... before_colored_samples=... after_colored_samples=... material_auto_apply_delta=... max_commit_frames=... max_settle_frames=... max_render_resources=25 max_collision_resources=25 edit_replacement_delta=... dense_world_files=0
WT_VALIDATION_G40_EDIT_VISUAL_MATERIAL_FEEDBACK_SMOKE_PASS profile=g19_compact_2k_on_demand engines=2 edits=2 min_changed_samples=... max_commit_frames=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g40_edit_visual_material_feedback_quality/g40_edit_visual_material_feedback_quality_report.json
WT_VALIDATION_G41_CONTRACT_PASS implementation=runtime_frame_budget_telemetry_quality
WT_VALIDATION_G41_RUNTIME_FRAME_BUDGET_TELEMETRY_PASS profile=g19_compact_2k_on_demand phases=... total_frames=... max_frame_ms=... max_avg_frame_ms=... movement_samples=... edits=2 reload_ready_frames=... max_render_resources=... max_collision_resources=... max_active_records=... max_queued_render=... max_queued_collision=... max_pending_retirements=... max_render_fading_resources=0 dense_world_files=0 telemetry=res://artifacts/g41_runtime_frame_budget_telemetry_quality/frame_telemetry.json
WT_VALIDATION_G41_RUNTIME_FRAME_BUDGET_TELEMETRY_SMOKE_PASS profile=g19_compact_2k_on_demand engines=2 phases=... total_frames=... max_frame_ms=... max_avg_frame_ms=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g41_runtime_frame_budget_telemetry_quality/g41_runtime_frame_budget_telemetry_quality_report.json
WT_VALIDATION_G42_CONTRACT_PASS implementation=collision_traversal_stability_quality
WT_VALIDATION_G42_COLLISION_TRAVERSAL_STABILITY_PASS profile_cases=3 route_segments=... edited_segments=... total_motion=... min_floor_contact_ratio=... max_off_floor_streak=... min_player_y=... max_abs_vertical_velocity=... max_render_resources=... max_collision_resources=... max_active_records=... max_render_fading_resources=0 dense_world_files=0
WT_VALIDATION_G42_COLLISION_TRAVERSAL_STABILITY_SMOKE_PASS engines=2 profile_cases=3 route_segments=... total_motion=... min_floor_contact_ratio=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g42_collision_traversal_stability_quality/g42_collision_traversal_stability_quality_report.json
WT_VALIDATION_G43_CONTRACT_PASS implementation=view_distance_presentation_quality
WT_VALIDATION_G43_VIEW_DISTANCE_PRESENTATION_PASS profile=g19_compact_2k_on_demand captures=3 full_visual_blocks=2048x2048 min_colored_samples=... min_horizontal_bins=... min_vertical_bins=... min_mid_band_samples=... max_render_resources=25 max_collision_resources=25 max_render_fading_resources=0 dense_world_files=0
WT_VALIDATION_G43_VIEW_DISTANCE_PRESENTATION_SMOKE_PASS profile=g19_compact_2k_on_demand engines=2 captures=3 min_colored_samples=... min_horizontal_bins=... min_mid_band_samples=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g43_view_distance_presentation_quality/g43_view_distance_presentation_quality_report.json
WT_VALIDATION_G44_CONTRACT_PASS implementation=edit_policy_shape_quality
WT_VALIDATION_G44_EDIT_POLICY_SHAPE_PASS profile=g19_compact_2k_on_demand default_shape=sphere dig_radius=1.800 place_radius=1.800 place_material=4 alternate_shape_toggles=false edits=6 inside_samples=... outside_unchanged_samples=... max_commit_frames=... max_settle_frames=... edit_replacement_delta=... max_render_resources=25 max_collision_resources=25 max_active_records=25 max_pending_retirements=0 max_render_fading_resources=0 dense_world_files=0
WT_VALIDATION_G44_EDIT_POLICY_SHAPE_SMOKE_PASS profile=g19_compact_2k_on_demand engines=2 edits=6 inside_samples=... outside_unchanged_samples=... max_commit_frames=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g44_edit_policy_shape_quality/g44_edit_policy_shape_quality_report.json
WT_VALIDATION_G45_CONTRACT_PASS implementation=storage_recovery_schema_quality
WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_PASS profile=g19_compact_2k_on_demand compact_2k_edits=3 compact_2k_replayed=3 compact_2k_recovered=3 journal_magic=WTEDIT journal_format_version=1 journal_source_revision=190019 journal_bytes=... truncated_tail_bytes=... recovery_truncated_to_bytes=... compaction_profile=g8_sparse_2k compacted_pages=93 compacted_source_revision=8102 compacted_world_revision=... compacted_reopened=1 compacted_journal_exists=false max_render_resources=25 max_collision_resources=25 max_active_records=25 dense_world_files=0
WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_SMOKE_PASS profile=g19_compact_2k_on_demand engines=2 compact_2k_edits=3 compact_2k_replayed=3 compact_2k_recovered=3 compaction_profile=g8_sparse_2k compacted_pages=93 compacted_reopened=1 quality_track=runtime_terrain dense_world_files=0 report=artifacts/g45_storage_recovery_schema_quality/g45_storage_recovery_schema_quality_report.json
WT_VALIDATION_G46_CONTRACT_PASS implementation=terrain_addon_api_contract_quality
WT_VALIDATION_G46_TERRAIN_ADDON_API_CONTRACT_PASS profile=g19_compact_2k_on_demand api_version=1 public_methods=22 stable_groups=7 lifecycle=1 streaming=1 edits=1 storage=1 telemetry=1 debug=1 samples=... edit_committed=1 world_revision_delta=... max_render_resources=25 max_collision_resources=25 max_active_records=25 direct_backend_calls=0 dense_world_files=0
WT_VALIDATION_G46_TERRAIN_ADDON_API_CONTRACT_SMOKE_PASS profile=g19_compact_2k_on_demand engines=2 api_version=1 public_methods=22 stable_groups=7 direct_backend_calls=0 quality_track=runtime_terrain dense_world_files=0 report=artifacts/g46_terrain_addon_api_contract_quality/g46_terrain_addon_api_contract_quality_report.json
WT_VALIDATION_G47_CONTRACT_PASS implementation=validation_workaround_removal_quality
WT_VALIDATION_G47_VALIDATION_WORKAROUND_REMOVAL_PASS profile=g19_compact_2k_on_demand moved_helpers=2 local_workaround_files=0 material_impl=terrain_addon_material_applicator mesh_stats_impl=terrain_addon_mesh_stats materialized=... max_render_resources=25 max_collision_resources=25 max_active_records=25 dense_world_files=0
WT_VALIDATION_G47_VALIDATION_WORKAROUND_REMOVAL_SMOKE_PASS profile=g19_compact_2k_on_demand engines=2 moved_helpers=2 local_workaround_files=0 direct_runtime_backend_refs=0 quarantined_historical_backend_tests=... quality_track=runtime_terrain dense_world_files=0 report=artifacts/g47_validation_workaround_removal_quality/g47_validation_workaround_removal_quality_report.json
WT_VALIDATION_G48_CONTRACT_PASS implementation=native_hot_path_boundary_quality
WT_VALIDATION_G48_NATIVE_HOT_PATH_BOUNDARY_PASS profile=g19_compact_2k_on_demand hot_paths=5 native_owned=5 gdscript_hot_loops=0 edit_committed=1 max_render_resources=25 max_collision_resources=25 max_active_records=25 dense_world_files=0
WT_VALIDATION_G48_NATIVE_HOT_PATH_BOUNDARY_SMOKE_PASS profile=g19_compact_2k_on_demand engines=2 hot_paths=5 native_owned=5 gdscript_hot_loops=0 quality_track=runtime_terrain dense_world_files=0 report=artifacts/g48_native_hot_path_boundary_quality/g48_native_hot_path_boundary_quality_report.json
WT_VALIDATION_G49_CONTRACT_PASS implementation=debug_telemetry_ui_quality
WT_VALIDATION_G49_DEBUG_TELEMETRY_UI_PASS profile=g19_compact_2k_on_demand categories=6 overlay=1 exported=1 active_chunks=25 queued_render=0 queued_collision=0 frame_samples=... edit_committed=1 materialized=... storage_visible=1 dense_world_files=0
WT_VALIDATION_G49_DEBUG_TELEMETRY_UI_SMOKE_PASS profile=g19_compact_2k_on_demand engines=2 categories=6 overlay=1 exported=1 quality_track=runtime_terrain dense_world_files=0 report=artifacts/g49_debug_telemetry_ui_quality/g49_debug_telemetry_ui_quality_report.json
WT_VALIDATION_ACTIVE_TRACK_GUARDRAILS_PASS active=runtime_terrain_quality post_g33_review_milestones=0
```

## Active terrain quality track

The active direction is runtime terrain quality, not repeated human-review
packaging. The current baseline is:

```console
python tools/g32_review_bundle_runtime_proof.py
python tools/g33_runtime_terrain_quality_gate.py
python tools/g34_edit_latency_persistence_quality.py
python tools/g35_terrain_correctness_artifact_quality.py
python tools/g36_cold_idle_performance_quality.py
python tools/g37_streaming_movement_performance_quality.py
python tools/g38_streaming_endurance_stability_quality.py
python tools/g39_distributed_edit_streaming_quality.py
python tools/g40_edit_visual_material_feedback_quality.py
python tools/g41_runtime_frame_budget_telemetry_quality.py
python tools/g42_collision_traversal_stability_quality.py
python tools/g43_view_distance_presentation_quality.py
python tools/g44_edit_policy_shape_quality.py
python tools/g45_storage_recovery_schema_quality.py
python tools/g46_terrain_addon_api_contract_quality.py
python tools/g47_validation_workaround_removal_quality.py
python tools/g48_native_hot_path_boundary_quality.py
python tools/g49_debug_telemetry_ui_quality.py
python tools/validate_production_gap_audit.py
python tools/validate_finite_production_roadmap.py
```

G49 is the latest completed terrain quality gate. Current state after G49 is
automated validation-grade compact 2K terrain runtime with measured frame/update
telemetry, collision traversal stability, and view-distance presentation
coverage plus default sphere edit policy/repeated edit shape validation and
compact storage recovery schema evidence plus a minimal game-facing terrain
addon API contract plus validation-workaround removal evidence plus native
hot-path boundary evidence plus debug telemetry UI evidence, not production-ready
large-world terrain. The gap to the expected final world/terrain is tracked in
[`docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md`](docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md).
The finite Terrain 1.0 roadmap is
[`docs/FINITE_PRODUCTION_ROADMAP.md`](docs/FINITE_PRODUCTION_ROADMAP.md): G41
through G60, with G60 as the release-candidate finish line. Next terrain work is
G50 terrain profile standard quality and must advance through that finite list
instead of appending unbounded "next useful" tasks.
Human-visible review remains useful as a final sanity check, but it is not the
active project direction.

Run the drift guard before adding or accepting any new milestone:

```console
python tools/validate_active_track_guardrails.py
```

The guard rejects post-G33 roadmap milestones that drift back into review,
handoff, bundle, packaging, or launch work instead of runtime terrain quality.

## Human-visible sanity check

Do not open the repository-root `project.godot` for terrain playtesting. The
root project is only a safe notice project and intentionally does not vendor
addons.

After running the G1 smoke command, open:

```text
artifacts/g1_visible_playtest/project/project.godot
```

After running the G1 visual capture command, the newest generated project is:

```text
artifacts/g1_visual_capture/project/project.godot
```

For current human visual testing of the 8 by 8 multi-chunk flat fixture, prepare
the dedicated generated project instead of manually patching ignored artifacts:

```console
python tools/prepare_human_playtest.py --profile flat_8x8 --reuse-bake --import-project
```

Then open:

```text
artifacts/human_playtest/project/project.godot
```

For G7 review of both generated profiles, run:

```console
python tools/g7_human_visual_handoff.py --reuse-bake --import-projects
```

Then open:

```text
artifacts/g7_human_visual_handoff/flat_8x8/project/project.godot
artifacts/g7_human_visual_handoff/mountain_8x8/project/project.godot
```

Run `res://scenes/validation_playtest.tscn`. The scene auto-starts the addon
reference terrain world, submits the selected profile's viewer update set, adds
a small WASD/jump playable character with a first-person camera and crosshair,
shows orientation markers, and shows a validation status overlay below the addon
debug overlay. Left mouse carves terrain and right mouse places/constructs
terrain through the terrain addon edit bridge. The automated G1/G4/G6 guards
check nonzero terrain triangle geometry, terrain collision resources, player
presence, crosshair presence, scripted player movement, edit commits,
replacement metrics, and sample updates. A gray rectangle alone is not an
acceptable G1 result.

Do not request current compact near-2K human-visible sanity check until the
runtime terrain quality gate passes. G24 is capped-window regression evidence
only, G25 is an overhead visual baseline, G26 is first-person full-terrain
runtime evidence, G27 is scene-level runtime preflight, G28 is normal launch
preflight, G29 is the human-ready project generator, G30 is the auditable bundle
generator, G31 is launch preflight, G32 is exact bundle runtime proof, and G33
is the active runtime terrain quality gate. First run:

```console
python tools/g31_review_bundle_launch_preflight.py
python tools/g32_review_bundle_runtime_proof.py
python tools/g33_runtime_terrain_quality_gate.py
```

Then open:

```text
artifacts/g30_compact_2k_review_bundle/project/project.godot
```

The G31 proof is the automated prerequisite before human review. It copies the
G30 review bundle to a separate launch workspace, removes stale Godot import
cache, disables human input only in that automation copy, imports it, and proves
the copied bundle reaches the ready marker through `project.godot`. Open the
original G30 bundle for human review; it remains human-input enabled. The G32
proof is the autonomous runtime prerequisite on the exact copied review bundle:
it runs G25, G26, and G27 from `bundle_runtime_copy`, preserving the source G30
bundle for human review while proving compact 2048 by 2048 terrain visibility,
first-person captures, event-driven material application, local native
Transvoxel chunks following scripted player movement for editable/collision
detail, bounded material-repair audit behavior, committed terrain edits, and
rejection of dense near-2K source/world files.
