---
id: TASK-005.1
title: P4.1 — Environment descriptor
status: To Do
assignee: []
created_date: '2026-07-03 23:21'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-005
priority: medium
ordinal: 24000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement Environment(key) descriptor: read-only, backed by the contextvar evaluation snapshot pushed per evaluate/invoke call. Raises if read outside an active evaluation or callback context. Reference: §6 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Reading Environment outside context raises an error
- [ ] #2 Conditional-body conformance fixture (enrollment example) passes
<!-- AC:END -->
