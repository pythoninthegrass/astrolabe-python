---
id: TASK-006.2
title: P5.2 — Install manifest + daemon install/uninstall/force passthrough
status: To Do
assignee: []
created_date: '2026-07-03 23:22'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-006
priority: medium
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
SDK locates bundled astrolabe-pyhost binary, writes install manifest to /Library/Application Support/Astrolabe/py/<label>.json ({interpreter, script, argv, sdk_version}), execs host binary with install-daemon semantics. Passthrough: uninstall-daemon, install-daemon --force, update-status. Re-runs are no-ops. Reference: §9 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 E2E test: install, launchd-kickstart restart, converge
- [ ] #2 Uninstall leaves no plists, sockets, or manifests
<!-- AC:END -->
