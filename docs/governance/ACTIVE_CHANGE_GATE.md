# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 29

Title: Synthetic ball 3D position from angular silhouette size
State: Approved by Anders on 2026-11-09. Closeout requires same-SHA CI in draft PR #29.
Project Law: V1.
Branch: `gate29/synthetic-ball-silhouette-range`.
Base: Gate 28 `60a4232463aed9352cfe7a631394ef6ff26a166f` (seven workflows successful).

## Scope and acceptance

Follow [Gate 29 synthetic ball range](GATE29_SYNTHETIC_BALL_RANGE.md).
Use the existing angular-size relation and Gate 28 optical rays. Allow an
offline sphere centre estimate, focused synthetic tests and governance
documentation. Recover known centres and reject weak or inconsistent rim
observations. Verify final commit CI.

Stop for physical capture, hardware evidence, new dependencies or expansion
into detection, clubface pose, contact, calibration or runtime integration.
