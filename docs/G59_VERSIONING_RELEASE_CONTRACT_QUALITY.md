# G59 - Versioning release contract quality

Status: complete when `WT_VALIDATION_G59_CONTRACT_PASS` and
`WT_VALIDATION_G59_VERSIONING_RELEASE_CONTRACT_SMOKE_PASS` both pass.

G59 locks the release contract required before the Terrain 1.0 release-candidate
gate.

The gate verifies that `docs/VERSIONING_RELEASE_CONTRACT.md` defines:

- versioning;
- compatibility;
- migration policy;
- license boundary;
- source/reference policy;
- release checklist.

Expected contract marker:

```text
WT_VALIDATION_G59_VERSIONING_RELEASE_CONTRACT_PASS sections=6 supported_godot=2 release_checklist=1 mit_boundary=1
```

Expected smoke marker:

```text
WT_VALIDATION_G59_VERSIONING_RELEASE_CONTRACT_SMOKE_PASS sections=6 supported_godot=2 release_checklist=1 mit_boundary=1 report=artifacts/g59_versioning_release_contract_quality/g59_versioning_release_contract_quality_report.json
```

Validator marker:

```text
WT_VALIDATION_G59_CONTRACT_PASS implementation=versioning_release_contract_quality
```
