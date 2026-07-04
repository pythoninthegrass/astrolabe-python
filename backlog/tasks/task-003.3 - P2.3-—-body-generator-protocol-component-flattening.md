---
id: TASK-003.3
title: P2.3 — body() generator protocol + component flattening
status: To Do
assignee: []
created_date: '2026-07-03 23:21'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-003
priority: high
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
body() is a generator yielding declarations (D-1 deviation). Any object with a body() generator can be yielded and is flattened before serialization (reusable components like DevTools()). Group() and 'with group()' context manager (D-2 deviation). Reference: §6 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Upstream DevTools example ports and produces expected conformance fixture
<!-- AC:END -->
