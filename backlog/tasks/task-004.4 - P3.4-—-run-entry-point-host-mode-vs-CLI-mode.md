---
id: TASK-004.4
title: 'P3.4 — run() entry point: host mode vs CLI mode'
status: To Do
assignee: []
created_date: '2026-07-03 23:21'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-004
priority: medium
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement cli.py run() entry point: with --astrolabe-host, start the asyncio RPC host loop (host.py). Without the flag, invoke the install flow (P5). Wires setup.py_ base class to the runtime. Reference: §3, §9 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 python mysetup.py --astrolabe-host starts and serves RPC
- [ ] #2 Without --astrolabe-host, install flow is invoked
<!-- AC:END -->
