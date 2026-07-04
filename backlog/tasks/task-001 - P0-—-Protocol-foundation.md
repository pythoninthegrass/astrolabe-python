---
id: TASK-001
title: P0 — Protocol foundation
status: Done
assignee: []
created_date: '2026-07-03 23:14'
updated_date: '2026-07-04 00:40'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
modified_files:
  - protocol/PROTOCOL.md
  - protocol/schema/treespec.schema.json
  - protocol/schema/rpc.schema.json
  - protocol/schema/identity.md
  - tests/conformance/
  - tests/python/test_schema_conformance.py
  - scripts/validate_schemas.py
  - Taskfile.yml
  - pyproject.toml
priority: high
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Complete protocol/ directory: framing spec, JSON schemas, and identity rules. Both toolchains validate against these in CI. All other phases depend on P0.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
P0 Protocol foundation complete. All three subtasks done. protocol/ directory fully populated: PROTOCOL.md (normative wire spec with JSON examples for all 9 methods), treespec.schema.json (JSON Schema covering all 9 node types and 18 modifier kinds), rpc.schema.json (JSON-RPC 2.0 envelope and per-method schemas), identity.md (OQ-1 resolved — identity is colon-delimited content strings, not canonical JSON). 16 golden conformance fixtures covering all node types. 20 passing pytest tests. task schema:validate target functional. All downstream phases (P1–P6) may now proceed.
<!-- SECTION:FINAL_SUMMARY:END -->
