# Astrolabe Python SDK — Wire Protocol Specification

**Version:** 1
**Status:** Normative
**Upstream reference:** photon-hq/Astrolabe v0.4.0

This document is the normative specification for the private wire protocol between
the `AstrolabePyHost` Swift shim and the Python runtime host. It is the authoritative
source of truth; both toolchains generate and validate against the schemas in
`protocol/schema/`. Do not rely on this protocol remaining stable across major versions.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Transport and Framing](#2-transport-and-framing)
3. [Handshake](#3-handshake)
4. [Methods — Swift → Python](#4-methods--swift--python)
5. [Methods — Python → Swift](#5-methods--python--swift)
6. [Error Model](#6-error-model)
7. [Version Bump Procedure](#7-version-bump-procedure)

---

## 1. Overview

The protocol is a **JSON-RPC 2.0** session over a **Unix domain socket**. It is:

- **Bidirectional**: both the Swift shim and the Python host may originate requests.
- **Private**: it is not a public or stable API surface. External consumers must not
  integrate against it directly.
- **Fail-closed on version skew**: a protocol version mismatch aborts startup with a
  non-zero exit code (see §3 and §7).

The protocol is intentionally minimal. It carries exactly the messages needed to
implement §2 of the system overview: tree evaluation, callback invocation, and
storage proxying. No engine semantics are implemented in Python.

---

## 2. Transport and Framing

### 2.1 Socket

- **Path:** `/var/run/astrolabe/py-host.sock`
- **Ownership:** root, mode `0600`
- **Passed to Python subprocess via:** `ASTROLABE_SOCKET` environment variable
- **Lifecycle:** created by the Swift host before spawning Python; unlinked on shutdown

### 2.2 Framing

Each message is framed as:

```text
┌─────────────────────┬──────────────────────────────────────────────────┐
│  4-byte length (BE) │  UTF-8 JSON payload                              │
└─────────────────────┴──────────────────────────────────────────────────┘
```

- Length is a 32-bit **big-endian unsigned integer** encoding the byte length of the
  JSON payload that immediately follows.
- Payload is **UTF-8 encoded JSON**. Payloads may contain arbitrary string content
  (e.g. shell output, tracebacks) — newline-delimited JSON is not used.
- Maximum payload size: 16 MiB. Messages exceeding this limit must be rejected by the
  receiver with error code `101` and the connection closed.

### 2.3 JSON-RPC 2.0

Messages follow [JSON-RPC 2.0](https://www.jsonrpc.org/specification) semantics:

- **Request:** `{"jsonrpc": "2.0", "id": <int>, "method": "<name>", "params": {...}}`
- **Success response:** `{"jsonrpc": "2.0", "id": <int>, "result": {...}}`
- **Error response:** `{"jsonrpc": "2.0", "id": <int|null>, "error": {"code": <int>, "message": "<str>", "data": {...}}}`

Concurrency is supported: multiple requests may be in-flight simultaneously. Request
IDs are **per-direction monotonically increasing integers** starting at 0; the Swift
side and the Python side each maintain their own counter independently.

Notifications (id-less requests) are not used; every request expects a response.

---

## 3. Handshake

The handshake is the first exchange after the socket connection is established.
It runs exactly once per connection and must complete before any other messages
are exchanged.

### 3.1 Sequence

1. Swift host sends `hello` (see §4.1).
2. Python host validates `protocol_version`, replies with its own `protocol_version`
   and `sdk_version`.
3. On `protocol_version` mismatch: **both sides log the mismatch and exit non-zero.**
   The launchd restart policy governs retry. Never attempt best-effort parsing across
   protocol versions (INV-6).
4. On version match: Python host sends `configure` (see §5.1) exactly once,
   immediately after the hello response.
5. Swift host applies the configuration, then enters the upstream startup sequence.
   No `evaluate` request is sent before `configure` completes.

### 3.2 Hello — request

Direction: **Swift → Python**

```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "method": "hello",
  "params": {
    "protocol_version": 1,
    "host_version": "0.1.0",
    "upstream_version": "0.4.0",
    "capabilities": ["telemetry", "self_update"]
  }
}
```

Fields:

| Field                | Type         | Description                                           |
| -------------------- | ------------ | ----------------------------------------------------- |
| `protocol_version`   | integer      | This document's version (currently `1`).              |
| `host_version`       | string       | SemVer of the `AstrolabePyHost` binary.               |
| `upstream_version`   | string       | SemVer of the upstream Astrolabe Swift framework.     |
| `capabilities`       | string array | Optional features available. Python may inspect these |
|                      |              | to enable conditional behaviour.                      |

### 3.3 Hello — response

Direction: **Python → Swift**

```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "result": {
    "protocol_version": 1,
    "sdk_version": "0.1.0"
  }
}
```

If `protocol_version` in the response differs from the request, the Swift host logs
and exits non-zero immediately.

---

## 4. Methods — Swift → Python

### 4.1 `evaluate`

Request a new TreeSpec from the Python host. Called by the Swift engine on each tick
when it needs a fresh declaration tree.

**Direction:** Swift → Python

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "evaluate",
  "params": {
    "env": {
      "isEnrolled": "true",
      "gitHubToken": "ghp_example"
    },
    "tick_id": 42
  }
}
```

Fields:

| Field      | Type    | Description                                                        |
| ---------- | ------- | ------------------------------------------------------------------ |
| `env`      | object  | Environment snapshot: keypath → string-encoded value.              |
| `tick_id`  | integer | Monotonically increasing tick counter from the Swift engine.       |

**Response (success):**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "version": 1,
    "root": {
      "type": "group",
      "payload": {
        "children": [
          {
            "type": "brew",
            "payload": {"name": "wget", "pkg_type": "formula"},
            "modifiers": []
          }
        ]
      },
      "modifiers": []
    }
  }
}
```

The `result` is a complete TreeSpec document conforming to `protocol/schema/treespec.schema.json`.

**Response (evaluation error):**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": 201,
    "message": "Exception in body()",
    "data": {
      "exception_type": "ValueError",
      "traceback": "Traceback (most recent call last):\n  File ...\nValueError: invalid config"
    }
  }
}
```

**Behaviour on error or timeout:**

- Error code `2xx`: Swift engine **keeps the previous tree** and surfaces the error
  via host logging/telemetry. Mounted nodes are not affected.
- Timeout: default 5 seconds, configurable via `configure.eval_timeout_ms`. Swift
  keeps the previous tree and logs a timeout error (code `202`).

### 4.2 `invoke`

Execute a registered Python callback. Called by the Swift engine when a proxied
closure must run (mount, check, hook, on_change, etc.).

**Direction:** Swift → Python

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "invoke",
  "params": {
    "token": "cb:3",
    "kind": "mount",
    "args": {},
    "deadline_ms": 1751586885000
  }
}
```

Fields:

| Field         | Type    | Description                                                              |
| ------------- | ------- | ------------------------------------------------------------------------ |
| `token`       | string  | Callback token from the registry. Pattern: `cb:<integer>`.               |
| `kind`        | string  | One of the values in the table below.                                    |
| `args`        | object  | Kind-specific arguments. See §4.2.1.                                     |
| `deadline_ms` | integer | Absolute deadline (milliseconds since epoch). Python raises on timeout.  |

**Supported `kind` values:**

| `kind`           | Trigger                                              |
| ---------------- | ---------------------------------------------------- |
| `mount`          | Node first converged (installed/started)             |
| `check`          | Periodic drift check                                 |
| `unmount`        | Node removed (uninstalled/stopped)                   |
| `pre_install`    | Before package installation                          |
| `post_install`   | After package installation                           |
| `pre_uninstall`  | Before package removal                               |
| `task`           | Manual task trigger                                  |
| `on_change`      | Observed environment keypath changed                 |
| `on_start`       | Daemon startup (`Astrolabe.onStart`)                 |
| `on_exit`        | Daemon shutdown (`Astrolabe.onExit`)                 |
| `dialog_button`  | User pressed a dialog button                         |
| `pre_update`     | Before self-update download                          |
| `post_update`    | After self-update install                            |
| `on_fail`        | Callback or reconciler failure                       |

**Response (success):**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "ok": true,
    "value": null
  }
}
```

`value` is the return value of the Python callable (JSON-serializable). For callbacks
that return nothing, `value` is `null`.

**Response (callback error):**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "error": {
    "code": 301,
    "message": "Unknown callback token",
    "data": {"token": "cb:99"}
  }
}
```

**Response (timeout):**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "error": {
    "code": 302,
    "message": "Callback timed out",
    "data": {"token": "cb:3", "kind": "mount", "deadline_ms": 1751586885000}
  }
}
```

**Behaviour on error:**

- `3xx` from a `mount` invoke: Swift treats it as a mount failure (same path as a
  thrown Swift closure). Upstream logs the failure; the drift loop retries.
- `check` returns Bool: Python must return `{"ok": true, "value": true|false}`.
  Non-bool `value` on a `check` invoke is treated as error `303`.
- Unknown token (`301`): Swift treats as a hard callback failure.
- Timeout (`302`): Swift treats as a failed callback per upstream failure semantics.

#### 4.2.1 `args` by kind

| `kind`           | `args` shape                                                   |
| ---------------- | -------------------------------------------------------------- |
| `mount`          | `{}`                                                           |
| `check`          | `{}`                                                           |
| `unmount`        | `{}`                                                           |
| `pre_install`    | `{}`                                                           |
| `post_install`   | `{}`                                                           |
| `pre_uninstall`  | `{}`                                                           |
| `task`           | `{}`                                                           |
| `on_change`      | `{"keypath": "<str>", "old_value": <any>, "new_value": <any>}` |
| `on_start`       | `{}`                                                           |
| `on_exit`        | `{}`                                                           |
| `dialog_button`  | `{"label": "<str>", "state_key": "<str>"}`                     |
| `pre_update`     | `{"version": "<str>"}`                                         |
| `post_update`    | `{"version": "<str>"}`                                         |
| `on_fail`        | `{"reason": "<str>"}`                                          |

### 4.3 `storage_changed`

Push notification from Swift when a `@Storage` value changes externally (e.g. via
`AstrolabeUtils` from another process).

**Direction:** Swift → Python

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "storage_changed",
  "params": {
    "key": "hasCompletedOnboarding",
    "value": true
  }
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {"ok": true}
}
```

Python updates its `Storage` descriptor cache with the new value. No `state_changed`
notification is needed (Swift already knows the value changed).

### 4.4 `shutdown`

Signals that the daemon is exiting. Python must return the ack promptly and then
clean up. Swift sends SIGTERM to the Python subprocess ≤ 2 seconds after this message.

**Direction:** Swift → Python

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "shutdown",
  "params": {
    "reason": "SIGTERM"
  }
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {"ok": true}
}
```

Mirrors `Astrolabe.onExit` timing. Python must not initiate new RPC calls after
receiving `shutdown`.

---

## 5. Methods — Python → Swift

### 5.1 `configure`

Sent exactly once, immediately after Python responds to `hello`. Swift must not
send `evaluate` before receiving `configure`.

**Direction:** Python → Swift

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "method": "configure",
  "params": {
    "poll_interval": 10.0,
    "daemon_mode": true,
    "version": "1.0.0",
    "update": {
      "source": {"kind": "github", "repo": "acme/mysetup"},
      "interval_hours": 1,
      "pre_update_token": "cb:1",
      "post_update_token": "cb:2",
      "on_fail_token": "cb:3"
    },
    "telemetry": null,
    "commands": [
      {"name": "status", "help": "Show current install status"},
      {"name": "reset", "help": "Reset onboarding flag"}
    ],
    "on_start_token": "cb:4",
    "on_exit_token": "cb:5"
  }
}
```

Fields:

| Field             | Type         | Required | Description                                                   |
| ----------------- | ------------ | -------- | ------------------------------------------------------------- |
| `poll_interval`   | number       | yes      | Tick interval in seconds (maps to `Astrolabe.pollInterval`).  |
| `daemon_mode`     | boolean      | yes      | `true` = run as LaunchDaemon; `false` = LaunchAgent.          |
| `version`         | string       | yes      | User script version string surfaced in telemetry/update.      |
| `update`          | object\|null | yes      | Self-update configuration. `null` = disabled.                 |
| `telemetry`       | object\|null | yes      | Telemetry backend configuration. `null` = disabled.           |
| `commands`        | array        | yes      | Custom CLI subcommands to register. May be empty.             |
| `on_start_token`  | string\|null | no       | Callback for `Astrolabe.onStart`. `null` = no hook.           |
| `on_exit_token`   | string\|null | no       | Callback for `Astrolabe.onExit`. `null` = no hook.            |

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "result": {"ok": true}
}
```

### 5.2 `state_changed`

Signals that a `@State` variable was mutated inside a callback. Swift schedules the
next evaluation tick (mirrors upstream `StateNotifier`).

**Direction:** Python → Swift

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "state_changed",
  "params": {}
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {"ok": true}
}
```

`@State` mutations outside callbacks (e.g. during `body()` evaluation) must not call
`state_changed` — they are already within an evaluation cycle.

### 5.3 `storage_read`

Read a value from Swift persistence. Swift is the single source of truth for `@Storage`
(interoperates with `AstrolabeUtils`).

**Direction:** Python → Swift

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "storage_read",
  "params": {
    "key": "hasCompletedOnboarding",
    "type_hint": "boolean"
  }
}
```

Fields:

| Field       | Type   | Required | Description                                                         |
| ----------- | ------ | -------- | ------------------------------------------------------------------- |
| `key`       | string | yes      | Storage key (same namespace as `AstrolabeUtils`).                   |
| `type_hint` | string | no       | JSON type hint (`boolean`, `integer`, `number`, `string`, `object`, |
|             |        |          | `array`) to aid Swift-side deserialization.                         |

**Response (key exists):**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {"value": false}
}
```

**Response (key absent):**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {"value": null}
}
```

### 5.4 `storage_write`

Write a value to Swift persistence. Triggers a tick (mirrors `@Storage` mutation
semantics in upstream).

**Direction:** Python → Swift

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "storage_write",
  "params": {
    "key": "hasCompletedOnboarding",
    "value": true
  }
}
```

`value` must be JSON-serializable (Codable analog). Swift rejects non-serializable
values with error code `401`.

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {"ok": true}
}
```

### 5.5 `log`

Route a log message from Python into the Swift host's logging and telemetry pipeline.
Callers should not expect `log` to be delivered in order relative to other messages.

**Direction:** Python → Swift

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "log",
  "params": {
    "level": "info",
    "message": "Onboarding complete",
    "fields": {
      "user": "alice",
      "duration_ms": 1200
    }
  }
}
```

Fields:

| Field     | Type   | Required | Description                                                    |
| --------- | ------ | -------- | -------------------------------------------------------------- |
| `level`   | string | yes      | One of: `debug`, `info`, `warning`, `error`, `critical`.       |
| `message` | string | yes      | Human-readable log line.                                       |
| `fields`  | object | no       | Structured key-value pairs for telemetry. Values are JSON-any. |

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {"ok": true}
}
```

---

## 6. Error Model

All errors use the JSON-RPC 2.0 `error` response shape:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": 201,
    "message": "Exception in body()",
    "data": {
      "exception_type": "ValueError",
      "traceback": "..."
    }
  }
}
```

### 6.1 Reserved error code ranges

| Range | Category  | Description                                                         |
| ----- | --------- | ------------------------------------------------------------------- |
| 1xx   | Protocol  | Framing errors, schema validation failures, version mismatches.     |
| 2xx   | Evaluate  | Exceptions or timeouts during `body()` evaluation.                  |
| 3xx   | Callback  | Exceptions, timeouts, unknown tokens, type errors in callbacks.     |
| 4xx   | Storage   | Read/write failures, type mismatch, persistence backend errors.     |

### 6.2 Defined codes

| Code | Name                       | Trigger                                                   |
| ---- | -------------------------- | --------------------------------------------------------- |
| 100  | Protocol error             | Generic framing or JSON parse failure.                    |
| 101  | Payload too large          | Message exceeds 16 MiB limit.                             |
| 102  | Schema validation failure  | Message body does not conform to the schema.              |
| 103  | Version mismatch           | `protocol_version` in `hello` response differs.           |
| 201  | Evaluate exception         | User exception raised inside `body()`.                    |
| 202  | Evaluate timeout           | `body()` did not complete within `eval_timeout_ms`.       |
| 301  | Unknown callback token     | `token` not found in any active registry generation.      |
| 302  | Callback timeout           | Callback did not complete before `deadline_ms`.           |
| 303  | Invalid callback return    | `check` callback returned a non-bool value.               |
| 304  | Callback exception         | User exception raised inside a callback.                  |
| 401  | Storage write type error   | `value` in `storage_write` is not JSON-serializable.      |
| 402  | Storage backend error      | Underlying persistence layer failure.                     |

### 6.3 Behaviour on error

- **`2xx` during `evaluate`:** Swift keeps the previous tree unchanged. Mounted nodes
  are not torn down. Error is surfaced via host logging and telemetry.
- **`3xx` from `mount` invoke:** Swift treats it identically to a thrown Swift closure.
  Upstream logs mount failure; the drift loop retries on the next tick.
- **`3xx` from `check` invoke:** Drift check failure. Upstream retries per its policy.
- **`1xx` (framing/schema):** Both sides should close the connection. Swift supervises
  and restarts the Python subprocess.

---

## 7. Version Bump Procedure

`PROTOCOL_VERSION` is the integer in the `protocol_version` field of `hello`. Currently `1`.

### 7.1 When to bump

Bump `PROTOCOL_VERSION` when any of the following change in a backwards-incompatible way:

- A method is added, removed, or renamed.
- A required field is added or removed from any `params` or `result` shape.
- The framing format changes.
- The handshake sequence changes.
- A new error code range is allocated or an existing range is redefined.

Do **not** bump for additive-only changes where both sides can safely ignore unknown
fields (e.g. adding an optional field, adding a new `capabilities` string, adding a new
`kind` to `invoke` that the Python side can handle by returning a `301`).

### 7.2 How to bump

1. Increment `PROTOCOL_VERSION` in this document and in both codebases.
2. Update `treespec.schema.json` and/or `rpc.schema.json` to reflect the change.
3. Add or update conformance fixtures in `tests/conformance/`.
4. Run `task schema:validate` and `task test:conformance` to confirm all fixtures pass.
5. Update this document's method tables and examples to reflect the new behaviour.
6. The handshake immediately rejects a version mismatch (code `103`). There is no
   negotiation or fallback. Both sides must be updated together.
