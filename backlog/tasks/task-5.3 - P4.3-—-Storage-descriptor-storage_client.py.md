---
id: TASK-5.3
title: P4.3 — Storage descriptor + storage_client.py
status: To Do
assignee: []
created_date: '2026-07-03 23:21'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-5
priority: medium
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement Storage(key, default) descriptor: reads/writes proxy via storage_read/storage_write RPCs. Values must be JSON-serializable. Push notifications via storage_changed RPC. Implement storage_client.py as standalone AstrolabeUtils analog for custom commands (no socket required). Reference: §6, §4.3, §4.4 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Value written from Python readable via upstream AstrolabeUtils on same machine (interop test)
- [ ] #2 Value written via AstrolabeUtils readable from Python via storage_changed
<!-- AC:END -->
