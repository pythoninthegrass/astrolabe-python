# Astrolabe Identity Rules (Normative)

**Status:** Normative — resolves OQ-1
**Upstream reference:** photon-hq/Astrolabe v0.4.0
**Sources:** `docs/content/docs/core-concepts.mdx`, `docs/content/docs/extending-astrolabe.mdx`,
`CONSTITUTION.md` (all from photon-hq/Astrolabe @ v0.4.0, fetched via Context7)

---

## 1. Overview

Astrolabe uses two identity models, depending on the node type:

- **Content identity:** Nodes with an inherent natural identifier (package name,
  launchd label, customized id) use a stable colon-delimited string. Reordering
  siblings does not change these identities; the diff engine can match them positionally
  independent of order.
- **Structural identity:** Sequences, conditionals, and optionals use position-based
  identity — the SwiftUI type-and-position model. Reordering structural nodes
  produces different identities.

The upstream source of record is the Swift engine. The Python SDK serializes nodes
into a `TreeSpec`; the Swift `TreeSpecInterpreter` materializes the spec into real
upstream declaration values and feeds them into the engine's identity machinery.
**Python never computes identity strings.** This document specifies what the Python
SDK must serialize to ensure the materialized Swift nodes carry the correct identity.

> **INV-2:** A declaration authored in Python must produce byte-identical identity
> input as the equivalent Swift declaration, so content-based diffing behaves
> identically. Identity is computed Swift-side from the materialized nodes; Python
> controls identity only via the payload fields it serializes.

---

## 2. Content-Identified Node Types

These nodes use a stable colon-delimited string derived from their payload.
Reordering siblings within a group does not trigger remount.

### 2.1 `brew`

**Identity format:** `brew:<pkg_type>:<name>`

**Examples (from upstream `core-concepts.mdx` and `extending-astrolabe.mdx`):**

```text
brew:formula:wget
brew:cask:firefox
brew:formula:htop
```

**Identity fields:**

| Field      | Source             | Notes                               |
| ---------- | ------------------ | ----------------------------------- |
| `pkg_type` | `payload.pkg_type` | Literal `"formula"` or `"cask"`.    |
| `name`     | `payload.name`     | Homebrew formula or cask name.      |

**Python must serialize both fields in `payload`.** Omitting either produces a node
the Swift shim cannot materialize, not a fallback identity.

### 2.2 `pkg`

**Identity format:** `pkg:<source_kind>:<source_id>`

**Examples (from upstream `core-concepts.mdx` and `extending-astrolabe.mdx`):**

```text
pkg:catalog:homebrew
pkg:internal:tool
```

**Identity fields by source kind:**

| `source.kind` | Identity segment      | Example                |
| ------------- | --------------------- | ---------------------- |
| `catalog`     | `payload.source.id`   | `pkg:catalog:homebrew` |
| `github`      | `payload.source.repo` | `pkg:github:org/tool`  |
| `custom`      | `payload.source.url`  | `pkg:custom:<url>`     |

> **Note:** The upstream docs show `pkg:internal:tool` as an example for a GitHub
> package. The exact mapping of `github` source kind → identity segment has not been
> confirmed at the source-code level (no `NodeIdentity` Swift file was available for
> direct inspection). The `github`/`custom` entries above are derived from the identity
> format pattern. **Flag for confirmation** when upstream source access is available.

### 2.3 `launch_daemon`

**Identity format:** `launchDaemon:<label>`

**Example (from upstream `core-concepts.mdx`):**

```text
launchDaemon:com.example.agent
launchDaemon:com.example.worker
```

**Identity fields:**

| Field   | Source          | Notes                                |
| ------- | --------------- | ------------------------------------ |
| `label` | `payload.label` | Launchd label (reverse-DNS string).  |

`type` in the TreeSpec is `"launch_daemon"` (snake_case); the identity string uses
`launchDaemon` (camelCase) as shown in upstream docs. The Swift shim is responsible
for this translation.

### 2.4 `launch_agent`

**Identity format:** `launchAgent:<label>` (inferred by symmetry with `launch_daemon`)

**Example (inferred):**

```text
launchAgent:com.example.menu
```

> **Note:** The upstream documentation examples show only `launchDaemon` in the
> identity string examples. `launchAgent` is inferred by structural symmetry.
> **Flag for confirmation** when upstream source access is available.

**Identity fields:**

| Field   | Source          | Notes                                |
| ------- | --------------- | ------------------------------------ |
| `label` | `payload.label` | Launchd label (reverse-DNS string).  |

### 2.5 `customized`

**Identity format:** `customized:<id>`

**Example (from upstream `core-concepts.mdx`):**

```text
customized:disable-spotlight
```

**Identity fields:**

| Field | Source       | Notes                                                           |
| ----- | ------------ | --------------------------------------------------------------- |
| `id`  | `payload.id` | User-assigned stable string. Must not change across refactors.  |

The upstream documentation explicitly states: "Keep id stable." Changing `id` is
a remount. Callback tokens (`mount`, `check`, `unmount`) are **excluded** from
identity input (INV-4).

---

## 3. Structurally-Identified Node Types

These nodes use SwiftUI-style type-and-position identity. Reordering them changes
their identity.

### 3.1 `group`

Groups use **structural identity**. The group node itself has no content-based ID;
its children are identified by their own rules (content or structural).

**Identity fields:** none from payload (structural — position within parent)

> **Note:** The upstream `CONSTITUTION.md` states "structural types use positional
> identity for their container structure, similar to SwiftUI's Identifiable protocol."
> Exact Swift-side implementation of group identity (e.g. whether it hashes type+offset
> or uses a tree path) was not confirmed from source. **Flag for confirmation.**

### 3.2 `sys`

**Inferred as content-identified** by `setting.kind` and `setting.value`, but this is
not confirmed from upstream source. Example identity string (inferred):

```text
sys:hostname:dev-mac
```

> **Flag for confirmation.** Until confirmed, the Swift shim must derive sys identity
> from the upstream Swift declaration value; the Python SDK's responsibility is limited
> to faithfully serializing `payload.setting`.

### 3.3 `jamf`

**Inferred as content-identified** by `setting.kind` and `setting.value`, but this is
not confirmed from upstream source. Example identity string (inferred):

```text
jamf:computerName:dev-mac-01
```

> **Flag for confirmation.** Same caveat as `sys`.

### 3.4 `anchor`

`Anchor` carries no payload and is documented as "a modifier-only attachment point
with no operation." It is likely structurally identified (position-based), but this
is not confirmed from upstream source.

> **Flag for confirmation.**

---

## 4. Modifier and Callback Participation in Identity

Per INV-4 and upstream semantics:

- **Config modifiers** (e.g. `loop_interval`, `environment`, `run_at_load`): these
  are payload-equivalent and **do** affect the materialized Swift node's configuration,
  but whether they participate in the identity string is Swift-side. Python faithfully
  serializes them; the shim applies them to the real Swift declaration.
- **Callback modifiers** (e.g. `pre_install`, `on_change`, `task`) and callback objects
  (`mount`, `check`, `unmount`): **excluded from identity input.** Callback tokens are
  ephemeral registry references; changing them does not change the node's identity.
- **Dialog modifier:** similarly excluded — dialog text and button tokens are not
  identity-bearing.

The rule is: if removing a field would change which real-world resource the node
refers to, it participates in identity. Tokens and hook presence do not.

---

## 5. Conformance Test Requirement

Every identity rule in §2 must have a corresponding conformance fixture in
`tests/conformance/` where the `payload` fields are representative of the identity.

The SwiftXCTest (P1.2 AC) is the executable proof: for each fixture, the test
materializes the TreeSpec and asserts that `upstream_node.identity == expected_string`.
Until the Swift test is authored, the identity strings in this document serve as
the specification.

---

## 6. Unresolved / Flagged Items

These items require direct inspection of the upstream `Sources/` (specifically the
Swift type handling identity) to resolve. Until resolved, the Swift shim derives
identity from the materialized upstream declaration value; Python's correctness
obligation is limited to faithfully serializing the fields listed in §2.

| ID     | Item                                                              | Blocking |
| ------ | ----------------------------------------------------------------- | -------- |
| OQ-1a  | Confirm `pkg:github` identity segment (repo vs. org/repo vs. url) | P1.2     |
| OQ-1b  | Confirm `launch_agent` identity string prefix                     | P1.2     |
| OQ-1c  | Confirm `sys` identity format                                     | P1.2     |
| OQ-1d  | Confirm `jamf` identity format                                    | P1.2     |
| OQ-1e  | Confirm `anchor` identity model (content vs. structural)          | P1.2     |
| OQ-1f  | Confirm `group` identity implementation (position hashing)        | P1.2     |
| OQ-1g  | Confirm whether config modifiers participate in identity strings  | P1.2     |
