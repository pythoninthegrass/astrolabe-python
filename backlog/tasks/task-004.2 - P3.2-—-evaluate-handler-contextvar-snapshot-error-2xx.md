---
id: TASK-004.2
title: 'P3.2 — evaluate handler: contextvar snapshot, error 2xx'
status: To Do
assignee: []
created_date: '2026-07-03 23:21'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-004
priority: medium
ordinal: 21000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Handle the evaluate RPC method: push env/state snapshot into a contextvar, run user body() generator, serialize to TreeSpec, return JSON. On user exception, return structured error 2xx with traceback in data.traceback. Never tear down mounted nodes on evaluation failure. Default timeout 5s. Reference: §4.3, §4.5, §7 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 User exception in body returns structured 2xx error
- [ ] #2 Python process survives a body() exception
<!-- AC:END -->
