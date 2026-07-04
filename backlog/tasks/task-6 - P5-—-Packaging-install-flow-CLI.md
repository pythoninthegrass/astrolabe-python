---
id: TASK-6
title: 'P5 — Packaging, install flow, CLI'
status: To Do
assignee: []
created_date: '2026-07-03 23:14'
updated_date: '2026-07-03 23:19'
labels: []
dependencies:
  - TASK-2
  - TASK-4
documentation:
  - docs/architecture.md
priority: medium
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Wheel build with embedded per-arch host binary, install manifest, daemon lifecycle passthrough, custom command registration, self-update and telemetry config. Depends on P1 and P3. Resolves OQ-2 (codesigning) and OQ-3 (AstrolabeState.payloads() read path).
<!-- SECTION:DESCRIPTION:END -->
