---
id: TASK-003.2
title: 'P2.2 — Modifier system: chaining, ordered serialization'
status: To Do
assignee: []
created_date: '2026-07-03 23:21'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-003
priority: high
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Config modifiers and callback modifiers serialize as an ordered list on each node. Modifier application returns a new declaration value. Group-level modifiers serialized only on the group node (propagation is Swift-side per INV-1/INV-5). Reference: §5.3 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Order-preservation tests: modifier sequence matches serialized order
- [ ] #2 Reuse-after-modify test: original declaration unchanged after modifier chain
<!-- AC:END -->
