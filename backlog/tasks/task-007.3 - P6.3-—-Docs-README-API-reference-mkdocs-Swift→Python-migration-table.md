---
id: TASK-007.3
title: 'P6.3 — Docs: README, API reference (mkdocs), Swift→Python migration table'
status: To Do
assignee: []
created_date: '2026-07-03 23:22'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-007
priority: low
ordinal: 33000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Write README for the SDK, generate API reference via mkdocs, and produce a migration table mapping every upstream Swift API element to its Python equivalent (or a §12 deviations register entry for intentional gaps). Reference: §12 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CI green on macOS runner
- [ ] #2 Migration table covers 100% of upstream README API surface, or links a §12 deviations entry for each gap
<!-- AC:END -->
