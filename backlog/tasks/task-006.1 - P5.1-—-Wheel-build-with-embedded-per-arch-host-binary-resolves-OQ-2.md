---
id: TASK-006.1
title: P5.1 — Wheel build with embedded per-arch host binary (resolves OQ-2)
status: To Do
assignee: []
created_date: '2026-07-03 23:22'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-006
priority: medium
ordinal: 27000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build platform wheels (macosx_15_0_arm64, macosx_15_0_x86_64) with compiled AstrolabePyHost binary at astrolabe/_bin/astrolabe-pyhost. uv-based build in CI. Resolve OQ-2: codesigning/notarization for embedded binary in a PyPI wheel. Reference: §3, §9 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 uv add astrolabe-sdk on arm64 macOS yields a runnable host binary
- [ ] #2 uv add astrolabe-sdk on x86_64 macOS yields a runnable host binary
- [ ] #3 Binary is codesigned
<!-- AC:END -->
