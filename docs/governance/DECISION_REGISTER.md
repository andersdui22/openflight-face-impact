# Face Impact architecture decisions

## 2026-11-25 — Media Foundation diagnostic provider

**Approved by the project owner** after PR #51, baseline
`b8f54dddbc75d9624a1a4fccc4dcfbe03c801df5`.

Use one x64 Media Foundation Source Reader DLL behind the existing Python
camera owner. Enumerate native symbolic links and activate the single exact
match. Reject a missing or ambiguous link. Do not map to a DirectShow or OpenCV
index. Use asynchronous per-sample callbacks and bounded waits in the owner.
Preserve original sample bytes and provenance alongside the existing analysis
raster and ring. Native timestamps are stream sample evidence, not sensor
exposure evidence. The app opens no device until explicit operator activation.

The provider supports diagnostic preview, controls and manual capture only.
It does not alter calibration validity, timing acceptance, measured output,
gate status or release authorization. Physical camera results remain
unverified until the device and driver are tested against independent evidence.

## 2026-11-26 — Decide recording windows at trigger time

Under the existing Gates 25–28 diagnostics authorization after draft PR
#53 (`88b40aec68b357f164b99d60c3214d842aac6be5`), retain one acquisition
owner and one ring. The selected native mode determines a bounded history.
Manual trigger requests choose pre/post counts or nominal durations within
that budget. Retain native payloads and stream diagnostic ZIPs through the
existing format. Separate driver media time, native callback QPC, host
arrival and processing observations. Keep sensor and drop metrics unknown
without evidence. See the [recording and timing evidence](../evidence/MDP_V1_2_GATES25_28_MEDIA_FOUNDATION.md).
