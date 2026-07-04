---
id: TASK-2.3
title: >-
  P1.3 — CallbackProxy: customized + hook/callback modifiers → invoke bridging
  (resolves OQ-4)
status: To Do
assignee: []
created_date: '2026-07-03 23:20'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-2
priority: high
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement CallbackProxy.swift: customized nodes materialize as upstream Customized(id:mount:check:unmount:) with proxy closures that call invoke(token, kind, args). Hook and callback modifier sites proxied similarly. Strict Bool coercion for check (non-bool → error). Structured errors map to thrown Swift errors. Resolves OQ-4: v1 dialog binding uses named-state-key via on_change kind. Reference: §8.2, §4.3 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 XCTest with mock Python endpoint covers success, user-exception, timeout, unknown-token for each invoke kind
<!-- AC:END -->
