---
id: TASK-006.3
title: >-
  P5.3 — Custom command registration + update-status passthrough (addresses
  OQ-3)
status: To Do
assignee: []
created_date: '2026-07-03 23:22'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-006
priority: medium
ordinal: 29000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement astrolabe.cli.command(...) to register argparse subcommands that execute in the Python process without contacting the engine (D-4 deviation). Use StorageClient for read-only state. update-status passthrough to host binary. Address OQ-3: determine if AstrolabeState.payloads() is accessible from another process or only @Storage via AstrolabeUtils. Reference: §6 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Registered command runs with no socket present
- [ ] #2 --help lists registered subcommands
<!-- AC:END -->
