# G58 - Documentation examples quality

Status: complete when `WT_VALIDATION_G58_CONTRACT_PASS` and
`WT_VALIDATION_G58_DOCUMENTATION_EXAMPLES_SMOKE_PASS` both pass.

G58 proves that the current addon stack has concrete adoption examples before
release-contract work begins.

The gate verifies documentation for:

- installation;
- profile setup;
- terrain editing;
- storage;
- telemetry;
- troubleshooting.

Primary example document:

```text
docs/TERRAIN_ADOPTION_EXAMPLES.md
```

Expected documentation marker:

```text
WT_VALIDATION_G58_DOCUMENTATION_EXAMPLES_PASS sections=6 code_blocks=... integration_readme=1
```

Expected smoke marker:

```text
WT_VALIDATION_G58_DOCUMENTATION_EXAMPLES_SMOKE_PASS sections=6 code_blocks=... integration_readme=1 report=artifacts/g58_documentation_examples_quality/g58_documentation_examples_quality_report.json
```

Contract marker:

```text
WT_VALIDATION_G58_CONTRACT_PASS implementation=documentation_examples_quality
```
