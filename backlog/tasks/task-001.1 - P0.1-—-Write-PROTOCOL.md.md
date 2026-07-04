---
id: TASK-001.1
title: P0.1 — Write PROTOCOL.md
status: Done
assignee: []
created_date: '2026-07-03 23:20'
updated_date: '2026-07-04 00:39'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
modified_files:
  - protocol/PROTOCOL.md
parent_task_id: TASK-001
priority: high
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Document framing, handshake, all §4 methods (Swift→Python and Python→Swift), error codes (1xx–4xx), and version-bump procedure. Reference: §4 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Every method in §4 documented with request/response JSON examples
- [ ] #2 Version bump procedure defined
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Authored protocol/PROTOCOL.md covering §4 in full: framing/transport (Unix socket, 4-byte BE length prefix), handshake sequence with protocol_version exchange, all Swift→Python methods (hello, evaluate, invoke, storage_changed, shutdown) and Python→Swift methods (configure, state_changed, storage_read, storage_write, log) each with request and response JSON examples, structured error model (1xx/2xx/3xx/4xx ranges with all defined codes), and version-bump procedure with clear rules for when to bump and the step-by-step process. All ACs met: every §4 method documented with examples; version bump procedure defined.
<!-- SECTION:FINAL_SUMMARY:END -->
