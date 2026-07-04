# Astrolabe Python SDK — Architecture

Status: DRAFT / foundation document
Upstream: https://github.com/photon-hq/Astrolabe (Swift, v0.4.0, macOS 15+, Swift 6.2+)
Audience: implementation agents working across independent sessions. Each parent task below is designed to be completable in isolation given this document and the upstream repo.

---

## 1. Scope and philosophy

### 1.1 What this is

A Python SDK that lets Python developers author Astrolabe configurations. The Swift framework remains the single source of truth for **all** engine behavior: tick loop, tree diffing, reconciliation, drift-check loops, persistence, daemon lifecycle, self-update, and telemetry.

The Python SDK is strictly a **binding layer**:

1. An **authoring API** that mirrors the Swift declaration DSL (`Brew`, `Pkg`, `Sys`, `LaunchDaemon`, `LaunchAgent`, `Customized`, `Group`, `Anchor`, modifiers, `@State` / `@Storage` / `@Environment`).
2. A **resident evaluation host**: a long-lived Python process that (re)evaluates the user's `body` when the Swift engine asks, and executes user callbacks (`Customized` closures, hooks, `on_change`) when the Swift engine invokes them.
3. A **wire protocol** between the Swift daemon and the Python host.
4. A **thin Swift shim target** (`AstrolabePyHost`) — the only Swift code we write. It is a consumer of the upstream framework, not a fork. It translates a serialized declaration tree into real Swift declaration values and proxies callbacks over the wire.

### 1.2 What this is NOT

- Not a reimplementation of the reconciler, differ, scheduler, launchd integration, persistence, or updater in Python. If a behavior exists in Swift, we call it; we never re-derive it.
- Not a new declarative semantics. Python `body` evaluation must be observationally equivalent to Swift `body` evaluation: same tree shape, same identities, same modifier propagation rules.
- Not a general-purpose RPC framework. The protocol is private, versioned, and minimal.

### 1.3 Design invariants (binding on all tasks)

- **INV-1 (Engine authority):** The Swift engine is the only component that mutates system state. Python callbacks execute user code but report results back to Swift; Swift decides scheduling, retries, and drift handling.
- **INV-2 (Identity parity):** A declaration authored in Python must produce byte-identical identity input as the equivalent Swift declaration, so content-based diffing behaves identically. Identity is computed **Swift-side** from the serialized payload; Python never hashes.
- **INV-3 (Pure tree build):** Python `body` evaluation must be treated as pure by contract. The SDK does not prevent I/O in `body` (Python cannot), but the protocol enforces an evaluation timeout and documents that side effects belong in callbacks/hooks, matching upstream's synchronous-tick contract.
- **INV-4 (Callbacks are opaque tokens):** Closures never serialize. The tree spec carries stable callback tokens; the Python host owns a token → callable registry. Callback tokens are excluded from identity input.
- **INV-5 (No API invention):** Every public Python API element must map 1:1 to an upstream Swift API element (renamed to snake_case). New conveniences require an explicit entry in §12 (deviations register) with justification.
- **INV-6 (Version skew fails closed):** Protocol handshake mismatches abort startup with a clear error. Never best-effort parse across protocol versions.

---

## 2. System overview

```
┌─────────────────────────────────────────────────────────────┐
│ launchd (root)                                              │
│   └── AstrolabePyHost (Swift binary, LaunchDaemon)          │
│         • conforms to upstream `Astrolabe`                  │
│         • body = TreeSpecInterpreter(currentSpec)           │
│         • spawns + supervises Python host subprocess        │
│         • JSON-RPC over Unix domain socket (framed)         │
│                    ▲            │                           │
│        evaluate /  │            │  callback invocations,    │
│        env snapshot│            │  storage reads/writes     │
│                    │            ▼                           │
│   └── python <user_program>.py --astrolabe-host             │
│         • astrolabe-sdk runtime (asyncio)                   │
│         • evaluates Setup.body() → TreeSpec JSON            │
│         • dispatches callback tokens → user coroutines      │
└─────────────────────────────────────────────────────────────┘
```

Data flow per tick:

1. Upstream engine ticks (state change or poll interval).
2. `AstrolabePyHost.body` needs a tree: it sends `evaluate(env_snapshot, state_snapshot)` to the Python host.
3. Python host runs user `body()`, returns a `TreeSpec` (JSON).
4. The Swift shim materializes the spec into upstream declaration values (`Brew(...)`, `Pkg(...)`, `Customized(...)` proxies, etc.) inside `body`.
5. The upstream engine diffs/reconciles as normal. When a proxied callback must run (`Customized.mount`, `.preInstall`, `on_change`, ...), the shim sends `invoke(token, args)` and awaits the result.

The upstream engine never knows Python exists. All integration is through public upstream API surface (`Astrolabe` protocol, declaration initializers, modifiers, `Customized`).

---

## 3. Repository layout

Monorepo, two toolchains:

```
astrolabe-py/
├── protocol/
│   ├── schema/                  # JSON Schema files, versioned (v1/)
│   │   ├── treespec.schema.json
│   │   ├── rpc.schema.json
│   │   └── identity.md          # normative identity-input serialization rules
│   └── PROTOCOL.md              # framing, methods, error codes, handshake
├── swift-host/
│   ├── Package.swift            # depends on upstream Astrolabe via SPM
│   └── Sources/AstrolabePyHost/
│       ├── main.swift           # Astrolabe-conforming entry point
│       ├── TreeSpecInterpreter.swift
│       ├── CallbackProxy.swift  # Customized-backed proxy nodes
│       ├── RPC/                 # socket server, framing, codecs
│       └── Subprocess.swift     # python process supervision
├── python/
│   ├── pyproject.toml           # uv-managed; package name: astrolabe-sdk
│   └── src/astrolabe/
│       ├── __init__.py          # public API re-exports
│       ├── setup.py_            # Setup base class, run()
│       ├── declarations.py      # Brew, Pkg, Sys, LaunchAgent, LaunchDaemon, Customized, Group, Anchor
│       ├── modifiers.py         # chaining mixin + modifier records
│       ├── state.py             # State, Storage, Environment descriptors
│       ├── treespec.py          # dataclasses ↔ JSON serialization
│       ├── runtime/
│       │   ├── host.py          # asyncio RPC server loop
│       │   ├── registry.py      # callback token registry
│       │   └── rpc.py           # framing, codecs, error mapping
│       ├── storage_client.py    # AstrolabeUtils analog (read/write via RPC or standalone)
│       └── cli.py               # install/uninstall/status passthrough
├── tests/
│   ├── conformance/             # golden TreeSpec fixtures shared by both sides
│   ├── python/                  # pytest unit tests
│   └── swift/                   # XCTest for interpreter + RPC
├── examples/                    # ports of upstream Examples/
└── Taskfile.yml
```

Rules:

- `protocol/` is the shared contract. Both toolchains generate/validate against it in CI. Schema changes bump `PROTOCOL_VERSION`.
- Python packaging with `uv`; the Swift host binary ships inside platform wheels (`macosx_15_0_arm64`, `macosx_15_0_x86_64`) under `astrolabe/_bin/astrolabe-pyhost`.

---

## 4. Wire protocol

### 4.1 Transport and framing

- Unix domain socket at `/var/run/astrolabe/py-host.sock` (root-owned, `0600`), path passed to the Python subprocess via `ASTROLABE_SOCKET` env var.
- Framing: 4-byte big-endian length prefix + UTF-8 JSON payload. No newline-delimited JSON (payloads may contain shell output).
- JSON-RPC 2.0 semantics (id, method, params, result, error), bidirectional: both sides may originate requests.
- Concurrency: multiple in-flight requests allowed; ids are per-direction monotonically increasing integers.

### 4.2 Handshake

First message after connect, Swift → Python:

```json
{"method": "hello", "params": {"protocol_version": 1, "host_version": "0.1.0", "upstream_version": "0.4.0", "capabilities": ["telemetry", "self_update"]}}
```

Python responds with its `protocol_version` and `sdk_version`. On mismatch of `protocol_version`, both sides log and exit non-zero (INV-6). After handshake, Python sends `configure` (see §8.1) exactly once.

### 4.3 Methods — Swift → Python

| Method | Params | Result | Notes |
|---|---|---|---|
| `evaluate` | `env: {key: value}`, `tick_id: int` | `TreeSpec` | Timeout 5s default (configurable). Timeout → engine keeps previous tree, logs. |
| `invoke` | `token: str`, `kind: enum`, `args: object`, `deadline_ms: int` | `{"ok": true, "value": any}` or structured error | Executes a registered callback. `kind` ∈ mount, check, unmount, pre_install, post_install, pre_uninstall, task, on_change, on_start, on_exit, dialog_button, pre_update, post_update, on_fail. |
| `storage_changed` | `key`, `value` | ack | Push notification when Swift-side `@Storage` changes (e.g. via AstrolabeUtils from another process). |
| `shutdown` | `reason` | ack | Mirrors `onExit` timing; Python must return promptly. |

### 4.4 Methods — Python → Swift

| Method | Params | Result | Notes |
|---|---|---|---|
| `configure` | see §8.1 | ack | Once, post-handshake, pre-first-evaluate. |
| `state_changed` | `{}` | ack | Signals a `@State` mutation occurred inside a callback; Swift schedules the next tick (mirrors upstream StateNotifier). |
| `storage_read` | `key`, `type_hint` | `value \| null` | Reads Swift persistence (single source of truth; interops with AstrolabeUtils). |
| `storage_write` | `key`, `value` | ack | Triggers tick like upstream `@Storage` mutation. |
| `log` | `level`, `message`, `fields` | ack | Routed into host logging / telemetry. |

### 4.5 Error model

Structured errors: `{code, message, data}`. Reserved codes:

- `1xx` protocol (framing, schema validation, version)
- `2xx` evaluation (user exception in `body` — includes traceback in `data.traceback`)
- `3xx` callback (user exception, timeout, unknown token)
- `4xx` storage

A `2xx` during `evaluate` must map to "keep previous tree + surface error via host logging/telemetry", never to tearing down mounted nodes. A `3xx` from a `mount` invoke maps to the same failure path as a thrown Swift closure (upstream logs mount failure; drift loop retries).

---

## 5. TreeSpec — the serialized declaration tree

### 5.1 Shape

```json
{
  "version": 1,
  "root": {
    "type": "group",
    "children": [
      {"type": "brew", "payload": {"name": "wget", "pkg_type": "formula"}, "modifiers": [...]},
      {"type": "pkg", "payload": {"source": {"kind": "catalog", "id": "homebrew"}}, "modifiers": []},
      {"type": "customized", "payload": {"id": "disable-spotlight"},
       "callbacks": {"mount": "cb:3", "check": "cb:4", "unmount": "cb:5"}, "modifiers": []}
    ],
    "modifiers": [{"kind": "environment", "keypath": "gitHubToken", "value": "..."}]
  }
}
```

### 5.2 Node types (v1 surface — mirrors upstream table)

| type | payload fields | callbacks |
|---|---|---|
| `brew` | `name`, `pkg_type` (formula/cask) | hooks only |
| `pkg` | `source` (catalog / github{repo, version{kind, value}} / custom), `allow_untrusted` | hooks only |
| `sys` | `setting` (tagged union, e.g. `{kind: "hostname", value: "dev-mac"}`) | — |
| `jamf` | `setting` (tagged union) | — |
| `launch_daemon` / `launch_agent` | `label`, `program`, plist config accumulated from modifiers (`run_at_load`, `keep_alive`, `standard_out_path`, `environment_variables`, `activate`, ...) | hooks only |
| `customized` | `id` | `mount`, `check`, `unmount` (unmount optional) |
| `anchor` | — | via modifiers (`on_change`) |
| `group` | `children` | — |

Conditionals and loops in Python `body` are resolved at evaluation time — the spec contains only concrete leaves, exactly like an evaluated Swift result-builder tree.

### 5.3 Modifiers as data

Modifiers serialize as an ordered list on each node; order is significant and must match Swift application order. Two categories:

- **Config modifiers** (pure data): `loop_interval`, `allow_untrusted`, `environment` override, launchd plist settings, `priority`.
- **Callback modifiers** (token-bearing): `pre_install`, `post_install`, `pre_uninstall`, `task`, `on_change` (carries observed keypath + token), `dialog` (carries text + button tokens + a `$state` binding reference).

Group-level modifiers propagate exactly as upstream (`Group{...}.keep_alive()` applies to children). The **Swift shim performs propagation by applying the real upstream modifier to the materialized group**, never by pre-flattening in Python — propagation semantics stay upstream-owned (INV-1/INV-5).

### 5.4 Identity rules (normative, see `protocol/schema/identity.md`)

- Identity input = canonical JSON of `{type, payload}` with sorted keys, no whitespace, UTF-8. Modifiers participate only where upstream includes them in identity (to be confirmed against upstream source — see OQ-1).
- `customized` identity = its `id` string alone, matching upstream ("Keep id stable").
- Callback tokens, dialog text, and hook presence are excluded (INV-4).
- The Swift shim feeds identity input into whatever upstream exposes; if upstream derives identity internally from node values, the shim's job reduces to constructing payload-equivalent nodes and parity is verified by conformance tests (§10).

---

## 6. Python public API

Mirrors Swift ergonomics under Python idioms. Full example (port of upstream README example):

```python
from astrolabe import (
    Astrolabe, Setup, Brew, Pkg, Customized, LaunchAgent,
    Environment, State, Storage, catalog, github, run,
)


class MySetup(Astrolabe):
    is_enrolled = Environment("isEnrolled")
    show_welcome = State(default=True)
    onboarded = Storage("hasCompletedOnboarding", default=False)

    poll_interval = 10.0
    daemon_mode = True

    def body(self) -> Setup:
        yield Pkg(catalog.command_line_tools)
        yield Pkg(catalog.homebrew)
        yield Brew("wget")

        if self.is_enrolled:
            yield Brew("git-lfs")
            yield Brew("firefox", type="cask")
            yield Pkg(github("org/internal-tool"))

            yield (
                LaunchAgent("com.example.myagent", program="/usr/local/bin/myagent")
                .run_at_load()
                .keep_alive()
                .activate()
            )

    async def on_start(self) -> None: ...
    def on_exit(self) -> None: ...


if __name__ == "__main__":
    run(MySetup)
```

API decisions (each is a task-level acceptance criterion):

- **`body()` is a generator** yielding declarations. This is the Python analog of a result builder: conditionals/loops compose naturally, and nesting uses `Group(children=[...])` or a `with group(...)` context manager (context manager form is a §12 deviation — approved, since Python lacks trailing-closure builders).
- **Declarations are frozen dataclass-like values**; modifier methods return new values (chaining, no mutation) so a declaration can be shared/reused as in Swift.
- **Callbacks accept both sync and async callables**; the runtime wraps sync in a thread executor. `Customized(id, mount=..., check=..., unmount=None)` maps positionally to the Swift trailing-closure form.
- **State descriptors:**
  - `Environment(key)` — read-only; raises if read outside an evaluation/callback context.
  - `State(default)` — in-memory, per-process; setting it fires `state_changed`.
  - `Storage(key, default)` — reads/writes proxy to Swift persistence via RPC (`storage_read`/`storage_write`); values must be JSON-serializable (Codable analog).
- **Typing:** full type hints, `py.typed` marker; `Setup = Iterator[Declaration]` alias.
- **Reusable components:** any object with a `body()` generator can be yielded and is flattened by the SDK before serialization (`DevTools()` example ports directly).

Custom commands (upstream §Custom Commands): v1 exposes `astrolabe.cli.command(...)` registering argparse subcommands that run **in the Python process without contacting the engine**, using `StorageClient` for read-only state — mirroring upstream's "framework takes no action" contract. Parity for `AstrolabeState.payloads()` requires a read-only accessor; see OQ-3.

Self-update and telemetry are configured as class attributes (`update = UpdateConfiguration(github("acme/mysetup")).interval(hours=1)...`, `telemetry = SignozTelemetry(...)`) and shipped in `configure`; execution is entirely Swift-side. `pre_update`/`post_update`/`on_fail` hooks are callback tokens.

---

## 7. Python runtime host

- Single asyncio event loop. RPC server (responding to Swift) and RPC client (originating to Swift) share one connection.
- **Callback registry:** tokens are `cb:<n>` assigned during tree serialization. On each `evaluate`, a fresh registry generation is created; tokens from prior generations remain valid until the Swift shim confirms the new tree is active (two-generation retention), because in-flight invokes may reference the old tree. Unknown token → error `301`.
- **Evaluation context:** a contextvar holding the env/state snapshot for the current `evaluate`, backing `Environment` reads. Reading `Environment` inside a callback uses the latest snapshot pushed by Swift.
- **Cancellation:** `invoke` carries `deadline_ms`; the runtime wraps user coroutines in `asyncio.wait_for`. Timeout returns error `302`; Swift treats it as a failed mount/check per upstream failure semantics.
- **Crash behavior:** if the Python process dies, the Swift host supervises: exponential backoff restart, re-handshake, re-`configure`, forced re-`evaluate`. Mounted state is unaffected (it lives in Swift persistence) — the tree simply re-converges. `@State` is lost on Python restart, matching upstream's "resets on daemon restart" semantics one level down; document this loudly.

---

## 8. Swift host shim (`AstrolabePyHost`)

The only Swift we write. Approximate size target: small; it must not grow engine features.

### 8.1 Startup and `configure`

`main.swift` declares `@main struct PyHost: Astrolabe`. Values that upstream requires as static/init-time config (`pollInterval`, `daemonMode`, `version`, `update`, `telemetry`, custom command names) arrive from Python before engine start:

1. Host process starts (via launchd or `sudo` first-run).
2. Spawns Python (`interpreter_path script_path --astrolabe-host`), both recorded at install time (§9).
3. Waits for handshake + `configure` (timeout → exit non-zero, launchd restarts).
4. Applies config, then enters the normal upstream startup sequence (root check → daemon resolution → persistence → `onStart` proxy → seed providers → first tick).

`configure` payload: `{poll_interval, daemon_mode, version, update?, telemetry?, commands: [...names/flags...], on_start_token?, on_exit_token?}`.

### 8.2 TreeSpecInterpreter

Maps validated TreeSpec JSON → upstream declaration values inside `body`. Requirements:

- Exhaustive mapping for every §5.2 node type and §5.3 modifier; unknown `type`/`kind` → hard evaluation error (fail closed, keep previous tree).
- Hook and closure sites are filled with thin closures that call `invoke(token, kind, args)` and translate structured errors into thrown Swift errors.
- `customized` nodes materialize as upstream `Customized(id:mount:check:unmount:)` with proxy closures. `check` proxies must coerce the Python return to Bool strictly (non-bool → error, not truthiness).
- Dialog modifier: `isPresented` binding bridges to a Python `State` — Swift writes the dismissal back via a dedicated `invoke(kind: "state_write")`... **No.** Keep v1 simpler: dialog binding is represented by a named state key; dismissal flows as `invoke(kind: "on_change")` against that key. Record final call in OQ-4.

### 8.3 Subprocess supervision

- Spawn with clean env + `ASTROLABE_SOCKET`; capture stdout/stderr into host logging.
- Restart policy: backoff 1s → 60s cap; counter resets after 10 min healthy.
- On `onExit` (SIGTERM path), send `shutdown`, wait ≤ 2s, then SIGTERM the child.

---

## 9. Install / CLI flow

`sudo python mysetup.py` (via `run()`):

1. SDK locates bundled `astrolabe-pyhost` binary in the wheel.
2. Writes an install manifest to `/Library/Application Support/Astrolabe/py/<label>.json`: `{interpreter: sys.executable, script: abspath, argv, sdk_version}`.
3. Execs the host binary with `install-daemon` semantics — the host then owns the upstream daemon-mode flow (install plist pointing at the **host binary**, bootstrap, exit). Re-runs are no-ops exactly as upstream.
4. `uninstall-daemon`, `install-daemon --force`, `update-status` pass through to the host binary unchanged.

Consequence: launchd runs the Swift host; the host reads the manifest and spawns the recorded interpreter/script. Moving the venv or script invalidates the manifest → host logs a clear error and exits (launchd throttles); `run()` re-executed by the user repairs the manifest (mirrors upstream binary-moved re-bootstrap behavior).

---

## 10. Testing strategy

- **Conformance (highest value):** golden-file suite in `tests/conformance/`. Each case = a Python `body` + expected TreeSpec JSON + a Swift XCTest that materializes the spec and asserts the resulting upstream node identities match a Swift-authored equivalent `body`. This is the executable proof of INV-2/INV-5. Every new node type or modifier requires a conformance case.
- **Protocol:** schema validation both directions in CI; fuzz the framing layer (truncated frames, oversized, invalid UTF-8).
- **Python unit:** descriptors, generator flattening, modifier immutability/ordering, registry generations, timeout/cancellation.
- **Swift unit:** interpreter exhaustiveness (a test that reflects over schema node kinds and asserts a mapping exists), subprocess restart/backoff, keep-previous-tree on evaluate failure.
- **End-to-end (manual/CI-mac):** BasicSetup example against a real macOS runner: install daemon, verify brew formula converges, kill Python process, verify recovery, uninstall.

---

## 11. Implementation plan — parent tasks

Each parent task lists child tasks with acceptance criteria (AC). Order respects dependencies; P1/P2 can proceed in parallel after P0.

### P0 — Protocol foundation
Deliverable: `protocol/` complete and CI-validated.
- **P0.1** Write `PROTOCOL.md`: framing, handshake, method tables (§4), error codes.
  AC: every method in §4 documented with request/response examples; version bump procedure defined.
- **P0.2** Author `treespec.schema.json` + `rpc.schema.json` covering §5 in full.
  AC: all upstream README examples expressible; schemas validate the golden fixtures; CI job validates fixtures against schemas.
- **P0.3** Write `identity.md` after auditing upstream identity derivation in `Sources/` (resolves OQ-1).
  AC: normative canonical-JSON rules; per-node-type identity field list cross-referenced to upstream source lines/commit.

### P1 — Swift host shim
Depends: P0.
- **P1.1** SPM package depending on upstream Astrolabe; `@main` skeleton, socket server, framing codec, handshake.
  AC: handshake round-trip test; version mismatch exits non-zero.
- **P1.2** `TreeSpecInterpreter` for pure-data nodes (`brew`, `pkg`, `sys`, `jamf`, `launch_*`, `group`, `anchor`) + config modifiers.
  AC: exhaustiveness test (§10); conformance fixtures for each node type pass.
- **P1.3** `CallbackProxy`: `customized` + hook/callback modifiers → `invoke` bridging; strict Bool coercion; structured error → thrown error mapping.
  AC: XCTest with a mock Python endpoint covering success, user-exception, timeout, unknown-token for each `kind`.
- **P1.4** `configure` application (poll interval, daemon mode, version, telemetry, update, on_start/on_exit proxies).
  AC: engine does not start before `configure`; each field observably applied.
- **P1.5** Subprocess supervision + evaluate-failure semantics (keep previous tree).
  AC: kill-child test recovers within backoff budget; evaluate timeout leaves prior tree mounted.

### P2 — Python SDK core (authoring)
Depends: P0. No runtime/RPC needed.
- **P2.1** Declaration dataclasses + payload serialization for all §5.2 types.
  AC: round-trip serialize → schema-validate for every type; frozen/immutable verified.
- **P2.2** Modifier system: chaining returns new values; ordered serialization; group propagation left to Swift (only serialized on the group node).
  AC: order-preservation tests; reuse-after-modify test (original unchanged).
- **P2.3** `body()` generator protocol + component flattening (`Setup` sub-objects).
  AC: upstream `DevTools` example ports and produces expected fixture.
- **P2.4** Callback token assignment during serialization (deterministic within a tree, excluded from payload).
  AC: identical `body` output twice yields identical TreeSpec except token generation counter.

### P3 — Python runtime host
Depends: P0, P2.
- **P3.1** asyncio RPC layer (framing, bidirectional requests, deadlines).
  AC: fuzz tests from §10 pass; concurrent in-flight invokes resolve correctly.
- **P3.2** `evaluate` handler: contextvar snapshot, generator evaluation, error `2xx` with traceback.
  AC: user exception in body returns structured error, process survives.
- **P3.3** Callback dispatch: registry generations (two-generation retention), sync-callable wrapping, `wait_for` timeouts.
  AC: in-flight invoke against previous generation succeeds during tree swap; timeout returns `302`.
- **P3.4** `run()` entry point wiring host mode vs CLI mode.
  AC: `python mysetup.py --astrolabe-host` serves; without flag, install flow (P5) invoked.

### P4 — State system
Depends: P3, P1.4.
- **P4.1** `Environment` descriptor bound to evaluation/callback context.
  AC: read outside context raises; conditional-body conformance fixture (enrollment example) passes.
- **P4.2** `State` descriptor + `state_changed` notification; document restart semantics.
  AC: mutation inside a callback triggers a Swift tick in integration test.
- **P4.3** `Storage` descriptor over `storage_read`/`storage_write`; `storage_client.py` standalone analog of AstrolabeUtils.
  AC: value written from Python readable via upstream AstrolabeUtils on the same machine (interop test), and vice versa via `storage_changed`.

### P5 — Packaging, install flow, CLI
Depends: P1, P3.
- **P5.1** Wheel build embedding per-arch host binary; uv-based build in CI.
  AC: `uv add astrolabe-sdk` on arm64 and x86_64 macOS yields a runnable host binary; binary codesigned (see OQ-2).
- **P5.2** Install manifest + daemon install/uninstall/force passthrough (§9).
  AC: E2E: install, reboot-simulated restart (launchd kickstart), converge, uninstall leaves no plists/sockets/manifests.
- **P5.3** Custom command registration (argparse, engine-untouched) + `update-status` passthrough.
  AC: registered command runs with no socket present; `--help` lists subcommands.
- **P5.4** Self-update + telemetry config passthrough with hook tokens.
  AC: configure payload conformance fixture; hooks invoked in a mocked update cycle.

### P6 — Conformance suite and hardening
Depends: all above; ongoing.
- **P6.1** Port all four upstream `Examples/` to Python with golden fixtures.
- **P6.2** Failure-mode matrix tests: python crash mid-mount, evaluate timeout, protocol desync, manifest drift.
- **P6.3** Docs: README, API reference (mkdocs), migration table Swift API → Python API (must cover 100% of the upstream README surface or link a §12 entry).
  AC for P6 overall: CI green on macOS runner; migration table has no unmapped upstream API without a deviations entry.

---

## 12. Deviations register

Intentional departures from a literal binding. Additions require justification and a conformance note.

| ID | Deviation | Justification |
|---|---|---|
| D-1 | `body()` is a generator, not a result builder | No Python equivalent; observationally identical tree. |
| D-2 | `with group(...)` context manager sugar | Ergonomics; serializes to the same `group` node. |
| D-3 | `@State` lost on Python-process restart (not only daemon restart) | Process boundary; documented. |
| D-4 | Custom commands execute in Python, not in the host binary's argv surface | Upstream contract is "framework takes no action" — preserved. |

## 13. Open questions (resolve before or during the referenced task)

- **OQ-1 (blocks P0.3):** exact upstream identity derivation — which fields/modifiers participate per node type. Requires reading `Sources/` (NodeIdentity); README implies content-based identity of leaves.
- **OQ-2 (blocks P5.1):** codesigning/notarization story for the embedded host binary distributed in wheels; whether a Team ID requirement conflicts with open-source distribution.
- **OQ-3 (P5.3):** is there a supported read path for `AstrolabeState.payloads()` from another process, or is payload state private to the daemon (only `@Storage` exposed via AstrolabeUtils)? Determines whether Python `status`-style commands can show installed payloads.
- **OQ-4 (P1.3):** dialog `isPresented` binding bridge design — named-state-key approach vs dedicated `state_write` invoke kind.
- **OQ-5:** custom `StateProvider` support from Python (poll a Python coroutine as an environment source). Proposed: out of scope for v1; revisit after P4.

