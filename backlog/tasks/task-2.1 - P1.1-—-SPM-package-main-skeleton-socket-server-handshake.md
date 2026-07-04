---
id: TASK-2.1
title: 'P1.1 — SPM package, @main skeleton, socket server, handshake'
status: To Do
assignee: []
created_date: '2026-07-03 23:20'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
parent_task_id: TASK-2
priority: high
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create swift-host/Package.swift depending on upstream Astrolabe via SPM. Implement @main PyHost: Astrolabe conformance, Unix domain socket server, 4-byte length-prefixed framing codec, and handshake sequence (hello/configure). Reference: §8.1, §4.2 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Handshake round-trip test passes
- [ ] #2 Protocol version mismatch exits non-zero
<!-- AC:END -->
