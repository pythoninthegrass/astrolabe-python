---
id: TASK-002.2
title: 'P1.2 — TreeSpecInterpreter: pure-data nodes + config modifiers'
status: To Do
assignee: []
created_date: '2026-07-03 23:20'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-002
priority: high
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Map validated TreeSpec JSON to upstream declaration values for all §5.2 pure-data node types: brew, pkg, sys, jamf, launch_daemon, launch_agent, group, anchor. Include all config modifiers. Unknown type/kind is a hard evaluation error (keep previous tree). Reference: §8.2 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Exhaustiveness test (reflects over schema node kinds, asserts mapping exists for each)
- [ ] #2 Conformance fixtures for each node type pass
<!-- AC:END -->
