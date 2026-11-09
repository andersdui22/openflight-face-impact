# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 31

Title: Synthetic image observation to Face Impact contact
State: Approved by Anders on 2026-11-09. Closeout requires same-SHA CI in a draft PR.
Project Law: V1.
Branch: `gate31/synthetic-observed-impact`.
Base: Gate 30 `3f91831bd62bd208b131559aa19cac56c41f85f5` (seven workflows successful).

## Scope and acceptance

Follow [Gate 31 synthetic observed impact](GATE31_SYNTHETIC_OBSERVED_IMPACT.md).
Compose existing calibrated rays, ball centre, face pose and finite face
contact for one supplied synthetic candidate frame. Allow one offline
orchestration function, independent known-geometry tests and governance
documentation. Recover signed impact coordinates in millimetres and reject
non-tangency, outside-face contact and invalid observations without coordinates.
Verify final commit CI on the draft PR.

Stop for physical capture, new dependencies, automatic detection, contact
frame timing, runtime/UI integration or physical accuracy claims. Gate 26
physical testing remains deferred.
