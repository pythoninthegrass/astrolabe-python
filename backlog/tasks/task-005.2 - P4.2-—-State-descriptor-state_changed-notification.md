---
id: TASK-005.2
title: P4.2 — State descriptor + state_changed notification
status: To Do
assignee: []
created_date: '2026-07-03 23:21'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-005
priority: medium
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement State(default) descriptor: in-memory, per-process. Setting it sends state_changed RPC to Swift, which schedules the next tick. Document loudly that @State is lost on Python-process restart (D-3 deviation), not only daemon restart. Reference: §6, §4.4 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Mutation inside a callback triggers a Swift tick in integration test
<!-- AC:END -->
