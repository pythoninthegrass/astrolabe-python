---
id: TASK-004.1
title: 'P3.1 — asyncio RPC layer (framing, bidirectional, deadlines)'
status: To Do
assignee: []
created_date: '2026-07-03 23:21'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-004
priority: medium
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement runtime/rpc.py: 4-byte big-endian length-prefix framing, JSON-RPC 2.0 bidirectional requests over Unix domain socket, per-direction monotonic ids, deadline tracking. Single asyncio event loop shared by server (Swift→Python) and client (Python→Swift). Reference: §4.1, §7 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 §10 fuzz tests pass (truncated frames, oversized, invalid UTF-8)
- [ ] #2 Concurrent in-flight invokes resolve correctly
<!-- AC:END -->
