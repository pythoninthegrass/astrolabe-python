---
id: TASK-002
title: P1 — Swift host shim
status: To Do
assignee: []
created_date: '2026-07-03 23:14'
updated_date: '2026-07-03 23:19'
labels: []
dependencies:
  - TASK-001
documentation:
  - docs/architecture.md
priority: high
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The only Swift code in the SDK: AstrolabePyHost binary. Depends on P0 (protocol). Covers SPM package, socket server, TreeSpecInterpreter, CallbackProxy, configure application, and subprocess supervision.
<!-- SECTION:DESCRIPTION:END -->
