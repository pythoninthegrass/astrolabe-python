---
id: TASK-002.4
title: >-
  P1.4 — configure application (poll interval, daemon mode, version, telemetry,
  update, hooks)
status: To Do
assignee: []
created_date: '2026-07-03 23:21'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-002
priority: high
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Apply the configure payload from Python before the engine starts: poll_interval, daemon_mode, version, update config, telemetry config, custom command names, on_start_token, on_exit_token. Engine startup must be gated on configure receipt. Reference: §8.1 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Engine does not start before configure is received
- [ ] #2 Each configure field is observably applied
<!-- AC:END -->
