---
id: TASK-3.1
title: P2.1 — Declaration dataclasses + payload serialization
status: To Do
assignee: []
created_date: '2026-07-03 23:21'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-3
priority: high
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement frozen dataclass-like values for all §5.2 node types: Brew, Pkg, Sys, Jamf, LaunchDaemon, LaunchAgent, Customized, Group, Anchor. Payload serialization to TreeSpec JSON. Modifier methods return new values (immutable chaining). Reference: §5.2, §6 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Round-trip serialize → schema-validate for every node type
- [ ] #2 Frozen/immutable: modifier returns new instance, original unchanged
<!-- AC:END -->
