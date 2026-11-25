# Gates 25 and 28 — Windows USB fixture integration

The approved starting point is draft PR #45 at
`d9f3583c17c3a45ba24ef7a24dfecd0d53872500`. This change tests the single
Windows USB reader and the existing dashboard under controlled software
conditions. Project Law V1 and the approved MDP V1.2 remain in effect.

The test launcher injects a camera factory into the existing adapter. It uses
the real reader thread, triggered ring, Flask status and JPEG routes, and
React preview. The fixture advertises a 640×400 negotiation and delivers 96×64
pixels. On restart it delivers a distinct 80×48 raster. The old handle must be
released before reopening. The stored 96×64 optics profile has unknown mode
identity before restart and incompatible dimensions afterward. Neither state
establishes physical calibration. The capture runs through existing preflight
and is rejected because its timestamps are host-arrival aliases.

Playwright covers disconnection, stale-frame suppression, restart, format
failure, calibration state and the absence of measured impact. The Windows
workflow also freezes the test launcher as a separate executable and uses it
with the portable Electron renderer. The normal Windows download still stages
the ordinary mock backend. Existing packaged lifecycle and archive regressions
run before the separate fixture smoke.

The result is software evidence for the approved slice of Gates 25 and 28.
Physical ELP acquisition, unplug/replug behavior, exposure and gain, timestamp
independence, geometry, contact time, accuracy and formal gate acceptance
remain pending. Use the PR's final commit and Actions run for test provenance.
