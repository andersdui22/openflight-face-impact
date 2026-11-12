# Offline capture preflight — software-only

The new opt-in `preflight_offline_capture` composes frame-level and capture-wide
quality validation with SHA-256 capture provenance. `require_matching_preflight`
rejects any later mutation of frame bytes, timing, exposure/gain or capture identity.

This component is intentionally **not** wired into the legacy synthetic impact
producer: that producer's existing blank-frame rejection fixtures must remain
valid, and an offline quality threshold is not a physical camera calibration.
Integration into a real ELP acquisition boundary requires a separately scoped
Gate acceptance test and physical validation later.

No real camera, clubface contact, accuracy, event emission, merge or release
is claimed. Gates 20–24 remain open pending outstanding evidence.
