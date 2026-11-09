# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 25

Title: Windows desktop runtime and hardware-free camera test preparation
State: Approved by Anders on 2026-11-09. Closeout requires final same-SHA CI
and the evidence recorded in draft PR #25.
Project Law: V1.
Branch: `gate25/windows-desktop-runtime`.
Base: Gate 24 `e022c2f2348e80d29e4ff3e627669c3dcfa8c645` (six required workflows successful).

## Scope and acceptance

See [Gate 25 Windows desktop runtime](GATE25_WINDOWS_DESKTOP_RUNTIME.md).
Allowed files are the Windows tests, existing Windows bootstrap workflow,
and governance/runbook. A minimal change in the existing launcher or Electron
entry point is allowed only if a reproduced failure requires it. Reuse the
existing app and dependencies. Verify the Electron renderer, Python synthetic
result, camera disabled, window close and restart on the same port.

No physical camera, driver changes, measurements, Golden baseline, merge,
release or packaging.
