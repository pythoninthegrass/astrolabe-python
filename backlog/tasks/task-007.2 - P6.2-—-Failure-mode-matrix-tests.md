---
id: TASK-007.2
title: P6.2 — Failure-mode matrix tests
status: To Do
assignee: []
created_date: '2026-07-03 23:22'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-007
priority: low
ordinal: 32000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Cover the failure-mode matrix: Python crash mid-mount (Swift keeps mounted state, recovers via subprocess supervision), evaluate timeout (keeps previous tree), protocol desync (version mismatch exits non-zero), manifest drift (interpreter/script moved, host logs clear error). Reference: §10, §7, §9 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Each failure mode has a test verifying the documented recovery or error behavior
<!-- AC:END -->
