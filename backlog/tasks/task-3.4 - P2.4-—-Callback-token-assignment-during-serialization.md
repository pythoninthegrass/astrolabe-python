---
id: TASK-3.4
title: P2.4 — Callback token assignment during serialization
status: To Do
assignee: []
created_date: '2026-07-03 23:21'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-3
priority: high
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
During tree serialization, assign stable callback tokens (cb:<n>) to each closure site. Tokens are deterministic within a single tree build, excluded from identity payload (INV-4). Token counter resets per evaluation. Reference: §7, §5.4 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Identical body() called twice yields identical TreeSpec except token generation counter
<!-- AC:END -->
