---
id: TASK-2.5
title: P1.5 — Subprocess supervision + evaluate-failure semantics
status: To Do
assignee: []
created_date: '2026-07-03 23:21'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-2
priority: high
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Spawn Python subprocess with clean env + ASTROLABE_SOCKET. Restart policy: exponential backoff 1s→60s cap, counter resets after 10 min healthy. On shutdown (SIGTERM), send shutdown RPC, wait ≤2s, then SIGTERM child. Evaluate timeout and 2xx errors must keep the previous tree mounted. Reference: §8.3, §7 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Kill-child test: process recovers within backoff budget
- [ ] #2 Evaluate timeout leaves prior tree mounted
<!-- AC:END -->
