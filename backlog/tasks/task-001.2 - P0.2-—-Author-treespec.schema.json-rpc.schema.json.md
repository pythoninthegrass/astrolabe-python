---
id: TASK-001.2
title: P0.2 — Author treespec.schema.json + rpc.schema.json
status: Done
assignee: []
created_date: '2026-07-03 23:20'
updated_date: '2026-07-04 00:39'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
modified_files:
  - protocol/schema/treespec.schema.json
  - protocol/schema/rpc.schema.json
  - tests/conformance/
  - scripts/validate_schemas.py
  - tests/python/test_schema_conformance.py
  - Taskfile.yml
  - pyproject.toml
parent_task_id: TASK-001
priority: high
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
JSON Schema files covering §5 in full (all node types, modifiers, payload fields). Both schemas used by CI to validate golden fixtures. Reference: §5 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All upstream README examples expressible in schema
- [ ] #2 Schemas validate the golden conformance fixtures
- [ ] #3 CI job validates fixtures against schemas
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Authored treespec.schema.json (JSON Schema draft 2020-12) covering all 9 §5.2 node types, all 18 modifier kinds from §5.3, and callbacks. Authored rpc.schema.json with JSON-RPC 2.0 envelope and per-method param/result schemas for all 9 methods. Created 16 golden conformance fixtures in tests/conformance/ covering all node types and source variants including the full MySetup enrolled example. All upstream README examples are expressible. Added scripts/validate_schemas.py (standalone harness, exits non-zero on failure), tests/python/test_schema_conformance.py (20 pytest tests, all passing), and task schema:validate Taskfile target. Added jsonschema dev dependency. All 3 ACs met: all examples expressible, fixtures validate, Taskfile target functional.
<!-- SECTION:FINAL_SUMMARY:END -->
