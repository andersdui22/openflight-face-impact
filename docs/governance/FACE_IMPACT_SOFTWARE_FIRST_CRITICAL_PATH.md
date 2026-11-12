# OpenFlight Face Impact — software-first critical path (approved 2026-11-11)

## Decision and scope

The user approved prioritizing a **working end-to-end Windows Face Impact application** over serial micro-hardening. Continue development in coherent functional batches; defer physical ELP OV9281 testing and calibration until all software Gates are as complete as possible. Project Law V1 remains in force: no silent Gate closure, merges, releases or changes to upstream OpenFlight / ConnectorNext. ConnectorNext remains read-only. One USB ELP camera only; no MLM2PRO integration.

## What the existing repository actually provides

- React/Electron dashboard already contains six Face Impact tiles, synthetic impact visualization, demo history, camera preview and advanced developer diagnostics.
- Python synthetic geometry and offline capture/batch/temporal/export components exist, but the unmocked **positive** image-to-export regression remains outstanding.
- Socket.IO currently provides a synthetic Face Impact demo and synthetic motion diagnostics, not a validated physical shot-to-impact event.
- Electron already supports a portable `dist/index.html` UI. The existing code explicitly says hardware/backend features remain unavailable until a supported service is connected; **a complete self-contained Windows application is not yet established**.
- Existing OpenFlight legacy views and radar-specific functionality are present; they are not evidence of Face Impact readiness.

## Functional batches — deliverables and exit evidence

### Batch A — Complete offline synthetic analysis (Gates 20–24)
1. Build one reproducible *unmocked* synthetic image fixture with consistent camera calibration, ball contour, face landmarks, known geometry, frame identity and timestamps.
2. Exercise real `assess_offline_capture_batch` → `prepare_offline_impact_handoff` → `export_offline_impact_evidence` and assert a **synthetically accepted** impact with coordinates, region, shot/session/frame provenance, and `physically_validated=False`.
3. Keep paired rejection tests for ambiguity, missing evidence, bad timestamps, altered capture and multiple candidate impacts.
4. If synthetic rasterization cannot satisfy the existing image/pose/ball constraints, document the precise blocker; do not mock geometry or weaken acceptance checks to force green.

### Batch B — One coherent Face Impact application flow (software-only)
1. Define one versioned, typed **offline result event** between Python and React; distinguish accepted synthetic, rejected, unavailable and later measured results.
2. Connect actual offline processing outputs to dashboard state, impact marker, shot list and replay selection. Preserve source/capture identity and avoid double-counting.
3. Replace misleading placeholder states with explicit offline/demo/connected statuses. Keep pixel proximity inside advanced diagnostics, not the main impact workflow.
4. Test end-to-end event delivery, reconnect, duplicate events, stale sessions and rejection coordinate suppression.

### Batch C — ELP-only capture service and offline replay (software-only)
1. Implement/verify one Windows USB camera owner, enumerated camera selection, bounded frame buffer, trigger capture and exposure/FPS configuration with explicit error states.
2. Provide a deterministic **recorded/synthetic frame replay mode** that exercises the same processing interface without requiring camera hardware.
3. Ensure camera failure, unplug/replug and no-device states do not masquerade as measured impact; hardware-specific outcomes remain unverified.

### Batch D — Windows launch and packaging
1. Produce a launcher that starts the required Python service and Electron renderer without a terminal, with startup readiness and graceful shutdown.
2. Build and smoke-test a Windows artifact from the real repository; verify packaged resource paths, backend connectivity, camera permissions and failure presentation.
3. Obtain an **authentic screenshot from a running application** for UI-changing PR checks. Never use a conceptual rendering as screenshot evidence.
4. Distinguish *buildable Windows bundle* from *physically validated face-impact release*.

### Batch E — Physical validation, deliberately deferred
Camera mounting, real clubface/ball visibility, exposure/FPS, impact-time identification, coordinate calibration, repeatability, accuracy and uncertainty. These cannot be signed off with synthetic data.

## Working rules

- Prefer one integrated feature batch plus its tests and handoff update to multiple defensive micro-commits.
- Fix small validation bugs only when they block a functional batch or permit misleading/unsafe output.
- Verify exact-SHA CI, report queued/cancelled/failed checks separately; do not infer green from older commits.
- Continue Gates 25–35 only within the authorized governance process; do not treat this priority decision as Gate closure or merge authorization.
- Keep an explicit distinction between implemented, tested, running on Windows, and physically verified.

## Immediate next engineering target

**Batch A positive unmocked synthetic image-to-export path**, followed by **Batch B offline result-to-dashboard integration**. The work is not complete merely because the synthetic demo can draw an impact dot.
