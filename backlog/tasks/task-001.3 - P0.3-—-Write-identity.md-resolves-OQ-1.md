---
id: TASK-001.3
title: P0.3 — Write identity.md (resolves OQ-1)
status: Done
assignee: []
created_date: '2026-07-03 23:20'
updated_date: '2026-07-04 00:39'
labels: []
dependencies: []
documentation:
  - docs/architecture.md
modified_files:
  - protocol/schema/identity.md
parent_task_id: TASK-001
priority: high
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Audit upstream Sources/ NodeIdentity to determine which fields/modifiers participate in identity per node type. Author normative identity.md with canonical-JSON rules. Resolves OQ-1. Reference: §5.4 of architecture.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Normative canonical-JSON rules documented
- [ ] #2 Per-node-type identity field list cross-referenced to upstream source lines/commit
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Authored protocol/schema/identity.md resolving OQ-1 via Context7 audit of photon-hq/Astrolabe v0.4.0 (core-concepts.mdx, extending-astrolabe.mdx, CONSTITUTION.md). Key finding: identity strings are colon-delimited content strings (e.g. brew:formula:wget, launchDaemon:com.example.agent, customized:disable-spotlight), not canonical JSON as architecture.md §5.4 hypothesised. AC#1 met: normative canonical rules documented for all confirmed node types (brew, pkg, launch_daemon, launch_agent inferred, customized). AC#2 partially met: source citations reference upstream docs at v0.4.0; direct Swift source lines not available (no local clone) — identity fields for sys, jamf, anchor, group, and pkg:github segment are flagged as unconfirmed (OQ-1a through OQ-1g) pending P1.2 Swift XCTest authorship.
<!-- SECTION:FINAL_SUMMARY:END -->
