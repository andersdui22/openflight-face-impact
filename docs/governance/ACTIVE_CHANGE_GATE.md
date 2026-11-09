# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 26

Title: Controlled physical ELP OV9281 acquisition on Windows
State: Active. Operator evidence pending.
Approval: Anders explicitly approved the physical procedure on 2026-11-09.
Project Law: V1.
Branch: `gate26/elp-operator-test`.
Base: Gate 25 `4bcb6d311949aa8c3763c957538b419b61f67200` (eight workflows successful).

## Scope and acceptance

Follow [Gate 26 ELP operator test](GATE26_ELP_OPERATOR_TEST.md). Use the
existing launcher, USB adapter, camera tab and loopback status endpoint.
Allowed changes cover the operator runbook, a read-only status sampler and
governance records. Obtain 60 seconds of evidence at the existing requested
mode and verify one restart. Report driver FPS and host-arrival FPS separately.

Stop on incorrect camera, unavailable preview, stalled stream or failed
restart. Preserve evidence and diagnose before continuing. Driver changes,
golf shots, calibration, impact accuracy, Golden, merge and release are outside
this gate.
