---
id: TASK-004.3
title: 'P3.3 — Callback dispatch: two-generation registry, sync wrapping, timeouts'
status: To Do
assignee: []
created_date: '2026-07-03 23:21'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-004
priority: medium
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement runtime/registry.py: token→callable registry with two-generation retention (tokens from prior tree remain valid until Swift confirms new tree active). Sync callables wrapped in thread executor. asyncio.wait_for enforces deadline_ms. Unknown token → error 301, timeout → error 302. Reference: §7 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 In-flight invoke against previous-generation token succeeds during tree swap
- [ ] #2 Timeout returns error 302
<!-- AC:END -->
