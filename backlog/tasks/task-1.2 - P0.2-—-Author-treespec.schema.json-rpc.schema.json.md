---
id: TASK-1.2
title: P0.2 — Author treespec.schema.json + rpc.schema.json
status: To Do
assignee: []
created_date: '2026-07-03 23:20'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-1
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
