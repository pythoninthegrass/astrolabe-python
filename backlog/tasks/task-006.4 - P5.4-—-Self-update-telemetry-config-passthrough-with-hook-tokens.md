---
id: TASK-006.4
title: P5.4 — Self-update + telemetry config passthrough with hook tokens
status: To Do
assignee: []
created_date: '2026-07-03 23:22'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-006
priority: medium
ordinal: 30000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
UpdateConfiguration and telemetry class attributes serialize into the configure payload. Execution is entirely Swift-side. pre_update, post_update, on_fail hook tokens carried in configure. Reference: §6, §8.1 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 configure payload conformance fixture validates correctly
- [ ] #2 pre_update, post_update, on_fail hooks invoked in a mocked update cycle
<!-- AC:END -->
