---
id: TASK-007.1
title: P6.1 — Port all four upstream Examples/ to Python with golden fixtures
status: To Do
assignee: []
created_date: '2026-07-03 23:22'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-007
priority: low
ordinal: 31000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Port all four upstream Examples/ (Swift) to Python equivalents in examples/. Each must have a corresponding golden TreeSpec JSON fixture in tests/conformance/ validated by the XCTest suite against a Swift-authored equivalent body. Reference: §10 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All four examples produce golden TreeSpec fixtures that pass conformance XCTests
<!-- AC:END -->
