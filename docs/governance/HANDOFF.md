# BATCH A — LABELLED REFERENCE MARKER ASSOCIATION (2026-11-12)

- Added fail-closed association from image-extracted **unlabelled** bright marker centres to separately trusted **labelled reference pixels**, with global one-to-one assignment, maximum per-point displacement and best-versus-runner-up ambiguity margin. Limited exhaustive matching to <=8 points; no guessed left-to-right label ordering.
- Added positive permuted-reference and negative wrong-reference/ambiguous correspondence raster tests. Association returns immutable labelled image pixels for downstream pose only when constraints pass.
- **Still missing** actual trusted reference acquisition, automated face geometry/pose integration, camera measurements and full browser E2E. This is a controlled offline preparatory component, not unmarked clubface detection.
- Exact SHA CI pending. Gates 20–24 OPEN; physical tests deferred; no merge/release.

---

# BATCH A — EXPERIMENTAL IMAGE-DERIVED FIDUCIAL OBSERVATIONS (2026-11-12)

- Added `experimental_face_markers.py`: controlled grayscale image -> thresholded, area/circularity/border-validated bright-marker centres, with exact count enforcement and immutable unlabelled pixel observations. Raster regression tests cover four observed points, missing/extra markers and unsupported images.
- This is a **preparatory image-observation primitive only**. The points have no established correspondence to face coordinates and are not fed into pose/impact estimation. No claim of automatic unmarked clubface detection or physical validity.
- PR Checks failure investigated: genuine screenshot absent from PR description. Do not fabricate screenshot. Exact SHA CI pending.
- Gates 20–24 OPEN; physical ELP tests deferred.

---

# BATCH A — OFFLINE EVIDENCE BOUNDARY HARDENING (2026-11-12)

- Strengthened the Python Socket.IO transport boundary: reject missing/whitespace/oversized shot and session identifiers, missing/oversized reasons, nonboolean acceptance, and noncallable emitter before any event publication. Added parameterized negative contract tests.
- Diagnosed PR Checks failure on `2074790c`: PR description lacks a real UI screenshot; the required headings and other checks passed. Do not bypass by inventing screenshots; capture authentic browser/Electron evidence in a later UI test.
- Exact-SHA CI for this commit must still be reviewed. Physical camera validation remains deferred; Gates 20–24 OPEN.

---

# AUTONOMOUS LARGE-BATCH DEVELOPMENT DIRECTIVE — 2026-11-12

User explicitly requested the largest practical autonomous development cycles. Prioritize complete functional slices and batch tests over micro-edits. The software-first batch sequence and acceptance conditions are recorded in `docs/governance/SOFTWARE_FIRST_AUTONOMOUS_DELIVERY_PLAN.md`. No change to Project Law V1 approval boundaries, no merges/releases, no physical tests yet.

---

# BATCH B — FRONTEND REGRESSION HARDENING (2026-11-12)

- Removed brittle exact React SSR whitespace-comment assertion from offline socket-to-review contract test. Added mixed accepted/rejected history test: latest rejected shot must not inherit an earlier accepted impact marker.
- Exact SHA `336bedd9` CI was still running at inspection; PR Checks failed. This change is not evidence of a completed browser/network end-to-end run.
- Next: verify exact SHA CI and add a controlled, server-owned synthetic replay path for true browser integration. Gates 20–24 OPEN; physical tests deferred.

---

# BATCH B — SOCKET EVENT TO REACT VIEW CONTRACT (2026-11-12)

- Extracted the actual `offline_impact_evidence` Socket.IO listener ingestion to a shared typed handler, used by production listener and new contract tests.
- Tests exercise event payload -> strict runtime validation -> Zustand history -> server-rendered React review, accepted marker, rejected no-marker, and forged physical-validation rejection. This is **not** a live browser-to-Python network E2E test.
- Python real Socket.IO test and accepted raster emission tests are in preceding commits, pending CI. This adds UI side coverage without claiming live ELP or physical measurement.
- Gates 20–24 OPEN; no merge/release; camera tests deferred.

---

# BATCH B — IN-PROCESS REAL FLASK-SOCKETIO DELIVERY (2026-11-12)

- Extended positive unmocked synthetic raster integration to instantiate a real Flask-SocketIO test client, send the completed typed offline handoff through `server.publish_completed_offline_impact`, and assert the delivered `offline_impact_evidence` payload matches the independently asserted runner payload.
- This tests the real Python server transport and targeted socket delivery in-process. It does **not** launch the React browser, automatically process ELP frames, or establish physical accuracy.
- Exact SHA `dd4ed35a` workflows queued at review; new commit CI pending. Gates 20–24 OPEN; physical tests deferred; no merges/releases.

---

# BATCH B — POSITIVE UNMOCKED RASTER TO SOCKET EMISSION REGRESSION (2026-11-12)

- Extended previously proven positive synthetic raster geometry fixture to invoke `analyze_and_publish_offline_capture` directly, repeating real image extraction, batch assessment, temporal selection, safe export and recipient-targeted event publication.
- Assert accepted x/y, face region, shot/session/frame identity, physically unvalidated metadata, and exactly one `offline_impact_evidence` emission. No mocked geometry calculations. This tests the Python-to-Socket.IO emission contract, **not an actual running browser/socket connection**.
- Physical ELP camera tests, automatic server capture callback, actual face landmark detection and browser transport integration remain deferred/open.
- Exact SHA `e59f99de`: Foundation, Pylint, Documentation and Windows USB camera passed; Tests and UI still running at review; PR Checks failed. New commit CI must be checked before acceptance.

---

# BATCH B — ACTUAL OFFLINE ANALYSIS TO EVENT ORCHESTRATION (2026-11-12)

- Added `analyze_and_publish_offline_capture` trusted Python entry point: unmocked captured-frame assessment, fingerprint-bound audit, temporal handoff, and targeted Socket.IO event publishing. It validates recipient/emitter before expensive analysis and aborts on errors without a fabricated impact.
- Added unmocked two-frame raster integration regression asserting a **rejected** synthetic result arrives as `offline_impact_evidence` with shot/session identity and no coordinates; and missing-recipient no-emission test.
- Existing earlier positive raster-to-export regression covers accepted synthetic geometry, but **a single accepted image-to-socket-to-browser regression is not yet demonstrated**.
- This runner is not wired into a live camera or automatic server capture callback. Explicit synthetic face landmarks remain supplied inputs. No physical measurements, merges, or releases.
- Previous exact SHA `d46ae6ad` CI still running at start of this batch. Verify new SHA CI; Gates 20–24 OPEN.

---

# CI REGRESSION REPAIR — SSR ZUSTAND SNAPSHOT (2026-11-12)

- Investigated exact SHA `f7dede01` CI: Python Tests, Pylint, Documentation, Windows USB camera and UI browser E2E passed. UI format failed (existing Prettier drift), and Foundation ui-unit-linux failed 3 new `OfflineImpactReview` tests (275 others passed).
- Cause: server-side `renderToStaticMarkup` uses Zustand's initial server snapshot, not a mutated client store; tests incorrectly expected injected runtime state to appear in SSR. Added explicit optional evidence injection to the review component and passed the validated store entries from the three tests. Normal production rendering still subscribes to the live store. This is a testability seam, not a bypass of the runtime transport validator.
- CI for this repair must be checked at its new exact SHA. PR Checks still failing, format not yet repaired, Gates 20–24 OPEN.

---

# BATCH B — SERVER-SIDE OFFLINE RESULT PUBLICATION SEAM (2026-11-12)

- Added `publish_offline_impact_handoff`: accepts only a typed `OfflineImpactHandoff`, serializes via schema-v1 offline evidence, and emits `offline_impact_evidence` to one explicit Socket.IO recipient. Added server adapter `publish_completed_offline_impact` and publisher contract tests.
- **Not yet automatic:** the offline capture/assessment producer still must call this server-side adapter when a capture is completed. No client-originated socket handler was added; clients cannot claim a physical measurement through this path.
- This is a genuine backend emission seam compatible with the React listener, but it is not proof of a fully integrated shot capture-to-dashboard run. CI for this commit pending; Gates 20–24 OPEN, no physical tests, merge or release.

---

# BATCH B — OFFLINE IMPACT VISUAL REVIEW (2026-11-12)

- Replaced text-only offline synthetic history with `OfflineImpactReview`, using `FaceImpactView` for accepted evidence, selectable shot history, and clear rejection messages. New component tests cover accepted marker, rejected no-marker, and accepted point outside illustrative outline.
- **Important:** face outline is explicitly illustrative and uncalibrated. The marker is a display of an accepted *synthetic offline result*, not a measured camera contact; no physical accuracy claim. The existing main Face Impact demo remains separate.
- Python still does not emit the new `offline_impact_evidence` event from actual offline captures. The UI subscription and review can consume such events once the backend is wired.
- Exact SHA `8aa9fd4b` CI pending at review; PR Checks failed. Gates 20–24 OPEN; physical tests deferred; no merge/release.

---

# BATCH B — FRONTEND OFFLINE EVIDENCE EVENT INGESTION (2026-11-12)

- Added bounded Zustand store `useOfflineImpactStore` and tests for validated event ingestion, immutable shot deduplication, session rollover and rejected evidence. Source must be versioned `offline_synthetic_analysis` and explicitly physically unvalidated.
- Socket.IO frontend now listens for `offline_impact_evidence` and clears offline history on server `session_cleared`. Disconnect does not falsely delete previously received offline history.
- Dashboard includes a separate, clearly marked **OFFLINE SYNTHETIC RESULTS — NOT CAMERA MEASUREMENTS** section with accepted/rejected counts, latest result and shot history. This does not alter legacy shot count or fabricate camera measurements.
- **Critical limitation:** Backend does not yet emit this event from an actual offline capture. It is an ingestion contract and display path, not a completed Python-to-UI end-to-end feature. Main clubface marker remains synthetic demo until linked to real offline evidence.
- Exact SHA `39ba87e4` CI pending at review. Gates 20–24 OPEN; no physical tests, merges or releases.

---

# BATCH B — VERSIONED PYTHON / REACT OFFLINE RESULT CONTRACT (2026-11-12)

- Introduced `serialize_offline_impact_evidence` with explicit schema v1, source `offline_synthetic_analysis`, shot/session/frame provenance, finite coordinate validation and strict `physically_validated=False`.
- Added Python JSON serialization and rejection tests; rejected evidence cannot carry a frame index or impact coordinates.
- Added matching React discriminated-union type and fail-closed runtime validator for future event ingestion. **No Socket.IO emission, UI ingestion, session persistence or physical measurement is claimed yet.**
- Existing synthetic demo event is separate from this offline export contract. Next functional batch must wire actual offline handoff outputs into a real backend event and dashboard state without treating them as measured.
- Exact SHA `0d2c2219` CI was pending at review, PR Checks still failing; do not infer green. Gates 20–24 OPEN; physical tests deferred; no merge/release.

---

# BATCH A CI RECONCILIATION — REAL BROWSER FAILURES (2026-11-12)

- Reviewed exact SHA `ec95a5dd`: Python Tests, Pylint and Documentation passed; UI lint/build passed, but UI format and two browser E2E tests failed; Windows camera and foundation still queued at review. PR Checks still failed.
- Both browser failures were caused by a stale assertion demanding eight `not measured` metric labels. The eighth tile is intentionally a session shot count with `session shots` label. Updated both E2E assertions to target the eight metric sublabels and require seven `not measured` plus one `session shots`, preserving the invariant that no fabricated camera measurement appears.
- Prettier format job independently reports eight unformatted UI source files; this commit does not claim to fix that formatting gate. PR screenshot evidence must still be resolved with authentic running-app capture.
- The newly added unmocked positive raster-to-export test was part of the successful Python Tests workflow, but a separate foundation run was pending at review. Gates 20–24 OPEN. No physical tests, merges or releases.

---

# BATCH A — FIRST POSITIVE UNMOCKED RASTER-TO-EXPORT REGRESSION (2026-11-12)

- Added `tests/test_offline_positive_synthetic_image_export.py`: deterministic projected sphere silhouette rasterized into an actual grayscale `CameraFrame`, with projected six-point synthetic clubface landmarks and calibrated distortion. The test passes the genuine contour extractor, batch assessor, temporal selection and impact exporter without mocks, asserting explicit shot/session/frame identity, expected toe/high impact and `physically_validated=False`.
- The blank frame is the negative control; the disk frame is the positive candidate. Rasterization quantizes pixels, so synthetic contact tolerance is explicitly 5 mm; this is **not** a claim of 5 mm measured accuracy.
- Test added to GitHub but **CI not yet verified**. If it fails, inspect the actual failure and correct fixture geometry or document the blocker; do not weaken checks solely to manufacture acceptance.
- Gates 20–24 remain OPEN pending CI and all acceptance evidence. No physical tests, merges or releases.

---

# USER-APPROVED SOFTWARE-FIRST CRITICAL PATH (2026-11-11)

- User explicitly approved changing development priority from serial micro-hardening to larger functional batches and deferring camera-specific fine-tuning to physical tests.
- New canonical execution guide: `docs/governance/FACE_IMPACT_SOFTWARE_FIRST_CRITICAL_PATH.md`. Batches A (positive unmocked offline synthetic export), B (Python result to UI/session), C (ELP-only capture/replay), D (Windows launcher/package), E (physical validation deferred).
- Audited actual `ui/electron/main.js`, `ui/package.json`, `ui/src/App.tsx`, `ui/src/services/socketService.ts`: existing Electron portable UI is **not** proof of a bundled Python backend; synthetic demo is **not** a measured impact. Do not claim complete EXE or physical accuracy.
- Exact SHA `9136ba07`: Tests, Foundation, Pylint, Documentation, Windows USB camera passed; UI still in progress, PR Checks failed on authentic screenshot requirement at review.
- No Gate closed; no physical tests, merge or release.

---

# PHASE 5 REJECTED-RESULT FIELD ISOLATION (2026-11-11)

- Reconciled React Socket.IO result validation with Python `SyntheticImpactResult` invariants: accepted synthetic impacts cannot also contain a rejection reason; rejected impacts cannot expose horizontal/vertical regions, in addition to coordinates. Added regressions for both contradictory payload classes.
- This prevents misleading display state at the transport boundary, but does not resolve the P0 positive unmocked image-to-export integration test or physical validation.
- CI for exact SHA `e9598c50` was queued/in progress at review. Do not infer passing results. PR Checks screenshot requirement remains outstanding.
- Gates 20–24 OPEN. No physical tests, merges or releases.

---

# PHASE 5 HANDOFF REGRESSION COVERAGE AND ACCEPTANCE RECONCILIATION (2026-11-11)

- Extended the unmocked synthetic-image capture handoff tests to reject over-budget frame batches and reordered frame captures even when frame count and identities otherwise match. This verifies both bounded processing and capture fingerprint provenance.
- Reconfirmed the canonical Phase 5 gap audit's P0 **positive** image-to-export synthetic success path remains open. No synthetic acceptance result has been fabricated to satisfy the test.
- Exact SHA `a38cc9f9` workflows were queued/in progress at review. No CI success is inferred from earlier SHAs. PR screenshot requirement remains unresolved.
- Gates 20–24 OPEN. Physical ELP validation postponed; no merge/release.

---

# PHASE 5 OFFLINE HANDOFF FRAME IDENTITY INTEGRITY (2026-11-11)

- Audited the genuine `prepare_offline_impact_handoff` chain against the Phase 5 acceptance gap document. Added early rejection of empty/oversized assessed frame batches, duplicated frame identities and out-of-capture indices before audit/timing/export. This prevents ambiguous or fabricated frame identities from reaching evidence export.
- Added unmocked integration regressions for duplicated, out-of-range and empty assessed frame tuples using the existing real synthetic-image capture fixture. They exercise rejection, not a positive accepted synthetic impact.
- Positive unmocked image-to-export accepted impact remains a P0 acceptance gap; do not claim it is completed. The earlier exact SHA `1d29bc67` passed Tests, Face Impact foundation, Pylint, Documentation and Windows USB camera checks. Later SHA `394717a1` still had pending workflows at last review, PR Checks failed on missing genuine screenshot. New SHA CI must be checked.
- Gates 20–24 OPEN, hardware testing deferred, no merges/releases.

---

# PHASE 5 SYNTHETIC RESPONSE CONTRACT HARDENING (2026-11-11)

- Extended React synthetic Socket.IO response contract to require nonempty case/label identifiers, nonempty error text, and to forbid impact data attached to a failed response.
- Rejected self-intersecting face outlines in the response guard, in addition to existing finite-coordinate, nonzero-area, bounded-vertex and point-inside-face checks.
- Added negative tests for malformed error payloads, missing labels and crossing polygons. No change to physically unverified status.
- Prior exact SHA `1d29bc67` had successful `Tests`, `Face Impact foundation`, `Pylint`, `Documentation`, and `Face Impact Windows USB camera` workflows; `UI` was still in progress and `PR Checks` failed due to missing authentic UI screenshot. The new SHA requires independent CI validation.
- The P0 positive unmocked synthetic image-to-batch-to-export integration test remains **outstanding**. This contract hardening is not a substitute for that Gate acceptance requirement.
- Gates 20–24 OPEN; no physical testing, merges or releases.

---

# PHASE 5 SOCKET PAYLOAD IMPACT-BOUNDARY VALIDATION (2026-11-11)

- Strengthened `isSyntheticFaceImpactResponse` at the network boundary: rejects degenerate zero-area and oversized polygons, non-finite coordinates and successful impact points outside the supplied face polygon. Existing `FaceImpactView` fail-closed checks remain independent defense in depth.
- Extended synthetic backend contract tests for collinear face vertices, outside impact and NaN coordinates. This is **synthetic** geometry validation only; physical contact remains unverified.
- At the time of review, exact SHA `1d29bc67` Documentation succeeded, PR Checks failed due to missing genuine screenshot, and remaining CI workflows were still running. Verify new exact SHA before Gate decisions.
- Gates 20–24 OPEN; no hardware tests, merges, releases.

---

# PHASE 5 UI REGRESSION TEST FIX (2026-11-11)

- Investigated failed `Face Impact foundation` job for SHA `f5feff11` using the actual GitHub Actions log. `SyntheticMotionDiagnostics.test.tsx` still failed: regex omitted the literal space between 'frame' and React's `<!-- -->` SSR separator. Updated both assertions to normalize React SSR comment separators before asserting exact user-visible text. This is a test-only correction; no application runtime behavior changed.
- CI for `05880cf0` was still in progress at review. PR Checks still fail on the genuine missing running-UI screenshot requirement, not something to bypass.
- Gates 20–24 OPEN; physical testing deferred; no merges/releases.

---

# PHASE 5 FACE VIEW TYPE SAFETY AND DEGENERATE OUTLINE GUARD (2026-11-11)

- Reviewed `FaceImpactView` after prior commit `f5feff11`. Corrected discriminated-union narrowing before accessing `x_mm`/`y_mm` for rejected statuses, preventing a TypeScript compile regression.
- Strengthened synthetic face outline validity with a bounded vertex count and nonzero shoelace area. Added zero-area outline regression; invalid outlines cannot display an impact marker. This is a frontend guard, not proof of physical accuracy.
- Exact-SHA CI on `f5feff11` was still running when checked; Documentation succeeded and PR Checks failed because real UI screenshot evidence is outstanding. New commit CI must be verified.
- Gates 20–24 remain OPEN. No hardware tests, merge, or release.

---

# PHASE 5 IMPACT-FIRST FACE VISUALIZATION HARDENING (2026-11-11)

- Updated the existing `FaceImpactView` (not a competing UI) to draw subtle face-center guides for synthetic impact interpretation.
- Added fail-closed UI checks: a synthetic impact marker is not drawn if its coordinates are non-finite, the supplied polygon is malformed (fewer than 3 points or non-finite), or the impact lies outside the polygon boundary. Boundary points are accepted. This is a display safety check, not a replacement for backend geometry validation or physical clubface recognition.
- Added React SSR regression tests for center guides, outside-face point and invalid polygon. CI on the new exact SHA is required before any acceptance claim.
- Prior exact SHA `5eb1e7cb`: Documentation and Windows USB camera workflows succeeded; other workflows were still running at review. PR Checks remained red because actual UI screenshots are not yet supplied; PR #45 description was updated accurately without bypassing that requirement.
- Gates 20–24 remain OPEN; all hardware tests deferred, no merge/release.

---

# PHASE 5 IMPACT-FIRST DASHBOARD AND UI CI REPAIR (2026-11-11)

- User confirmed image-space ball/face separation is a developer diagnostic, **not** a primary user-facing feature. Moved `SyntheticMotionDiagnostics` behind a collapsed **Advanced diagnostics** disclosure in the existing dashboard. The main impact face visualization and existing demo controls remain visible and unchanged; do not pretend the current synthetic demo is a measured impact.
- Audited exact SHA `d4be4e4c` CI: Foundation `ui-unit-linux` failed in `SyntheticMotionDiagnostics.test.tsx` because React server rendering inserts `<!-- -->` between adjacent text and numeric values; test asserted a literal continuous string. Repaired assertions to accept React's SSR separator without weakening runtime validation.
- PR Checks failure at `d4be4e4c` is PR-description completeness, not an application test failure; requires separate PR metadata remediation. Other CI workflows may still be pending. Verify all checks for this new SHA.
- No physical ELP tests, upstream modifications, merges, releases, or Gate closure. Gates 20–24 OPEN; continue impact-first development and software-only tests.

---

# PHASE 5 SYNTHETIC MOTION FRAME INSPECTION (2026-11-11)

- Added selectable observed-frame controls and explicit per-frame pixel separation/sensor timestamp to the existing React diagnostics panel. This is **metadata inspection**, not photographic frame replay or measured impact.
- Removed obsolete commented duplicate TypeScript payload declaration; retained shared typed contract and fail-closed checks.
- Extended UI render regression to cover frame controls and selected-frame readout. New exact-SHA CI must be verified; Gates 20–24 OPEN, no physical tests/merge/release.

---

# PHASE 5 SYNTHETIC MOTION DASHBOARD AND SOCKET HANDOFF (2026-11-11)

- Active repository: `andersdui22/openflight-face-impact`; branch `mdp-v1.2/phase5-gates20-24-parallel`; draft PR #45. Latest reviewed implementation SHA before this handoff update: `c9ddf590b4be1d5dc68bbc5827c9e4ead4b1d73a`.
- Gates 20–24 remain **OPEN**. All 35 Gates should be developed software-first, deferring ELP OV9281 physical tests until no further meaningful software-only progress is possible. No upstream OpenFlight or ConnectorNext changes; no merge or release without separate authorization.
- Added real synthetic image sequence → dual-object observation → image-space proximity → temporal trend → safe JSON UI payload in `offline_motion_analysis_pipeline.py`. This never confirms physical contact, real impact coordinates, or calibrated uncertainty.
- Corrected three synthetic motion test fixtures so the moving ball and static face share the same vertical image region (`dfac4316`). The synthetic scene remains only a fixture; CI must establish test pass.
- Added `SyntheticMotionDiagnostics` panel to existing React/Electron dashboard (`44c6ea0f`), with distance plot and explicit non-measurement labels. The design illustration shown in conversation is **not** a screenshot of the actual UI and includes features not yet implemented.
- Added React Socket.IO listener, strict synthetic payload validation, Zustand state, and disconnect clearing (`c092e47c`). Do not render invalid or physical-contact-claiming data.
- Added explicit, user-triggered `request_synthetic_motion_demo` Flask-SocketIO handler and Python-generated grayscale fixture through the real analysis pipeline, emitting `synthetic_motion_diagnostics` to the requesting client only (`c41cc211`). UI has Load/Reload synthetic motion demo buttons. This is **not** automatic ELP camera analysis.
- Added Flask-SocketIO integration tests for event payload, session isolation and no unsolicited emission, plus a technical handoff document at `docs/governance/PHASE5_SYNTHETIC_SOCKET_HANDOFF.md` (`c9ddf590`).
- **CI status:** Recent exact-SHA workflows were queued/in progress when checked. No all-green claim is made for `c9ddf590` or this handoff commit. Check exact-SHA Tests, UI, Pylint, Foundation, Documentation, PR Checks and Windows USB camera workflow where applicable. Fix failures before proposing Gate closeout.
- **Next work:** run and inspect actual CI failures; correct any synthetic pipeline/Socket.IO regression; verify React build and complete end-to-end request→Python→Socket.IO→React test; then implement image replay within existing dashboard without falsely implying physical measurements. Reconcile canonical approved MDP V1.2 acceptance criteria before Gate closure.

---

# PHASE 5 SOFTWARE-ONLY ACCEPTANCE GAP AUDIT (2026-11-11)

- Added `docs/governance/MDP_V1_2_PHASE5_SOFTWARE_ACCEPTANCE_GAP_AUDIT.md` with explicit Gate 20–24 evidence, remaining P0/P1 software gaps and hardware-deferred acceptance.
- `fa0972cc` CI queued at audit time. Prior `d99ea571` exact-SHA six workflows SUCCESS; not transferable to newer commits.
- Gates 20–24 remain OPEN; canonical approved MDP V1.2 acceptance criteria still absent in inspected repository. No merge/release/physical tests.

---

# PHASE 5 GATES 20–24 AUDITED OFFLINE HANDOFF INTEGRATION (2026-11-11)

- Exact-SHA `d99ea571`: all six CI workflows SUCCESS.
- Added `offline_impact_handoff.py`: composes existing audited capture batch, independent host/sensor timing checks, unique synthetic frame selection and fail-closed impact export. Reaudits batch before export to reject stale or tampered audit counts.
- Added unmocked synthetic image integration tests for rejected candidate geometry, invalid timing, tampered audit and wrong input type. This tests the actual contour-to-batch-to-handoff rejection path; it does NOT demonstrate successful physical impact detection or contact timing.
- Gates 20–24 remain OPEN pending software acceptance audit; physical tests deferred. No merge/release. Verify new SHA CI.

---

# PHASE 5 GATES 23/24 OFFLINE IMPACT EVIDENCE HANDOFF (2026-11-11)

- Verified `8fee97fe` exact-SHA CI: all six workflows SUCCESS.
- Added typed `offline_impact_evidence.py` export for selected **synthetic-only** impact coordinates. Preserves shot/session/frame and rejects coordinate disclosure if timing or uniqueness gates fail. Physical validation remains false; uncertainty remains unknown. Cross-checks selected accepted indices against provided candidate batch.
- Tests: accepted synthetic coordinates, ambiguous and invalid-timing fail-closed, mismatched selection, forbidden physical claims and rejected coordinates, invalid input.
- No real contact instant, camera hardware tests, merge or release. Gates 20–24 OPEN; new SHA CI pending.

---

# PHASE 5 GATES 22/24 COMBINED OFFLINE TEMPORAL EVIDENCE (2026-11-11)

- Added `offline_temporal_evidence.py` to compose existing strict frame-spacing validation with existing unique synthetic geometry frame selector. Only an unambiguous synthetic candidate **and** valid bounded timing can pass the offline analysis gate; no physical contact claim.
- Tests cover positive synthetic candidate, invalid timing despite unique geometry, ambiguous candidates, out-of-capture indices, and impossible evidence mutations.
- Previous `9e270c40` CI was running when inspected; previous UI E2E rerun also running. New SHA CI must be checked. No merge/release or physical tests; Gates 20–24 remain OPEN.

---

# PHASE 5 GATE 22 OFFLINE FRAME SPACING QUALITY (2026-11-11)

- Verified `7949276b` Python Tests, Pylint, Foundation, Documentation and PR Checks SUCCESS; UI E2E failed before execution because runner could not resolve Ubuntu apt mirror; rerun requested, E2E pending.
- Added `offline_frame_spacing.py`: bounded offline diagnostic for sensor-clock and host-clock inter-frame gaps, using existing strict trigger timing validator. Both clocks remain separate. Rejection preserves explicit reasons; no frame ranking, physical FPS certification, exposure synchronization or contact inference.
- Tests cover positive synthetic clock intervals, independent gap limits, invalid trigger timing, invalid limits, and forbidden physical-contact claims.
- No camera ownership changes, no physical tests, no merge/release. Gates 20–24 OPEN. Verify CI at new SHA.

---

# PHASE 5 GATE 21 ROBUSTNESS: HOLES AND MALFORMED THRESHOLDS (2026-11-11)

- Verified `48c0c3b5` exact-SHA CI: all six workflows SUCCESS, including the unmocked synthetic image-to-pose regression.
- Hardened optional synthetic perspective quadrilateral extraction against filled-contour **interior holes** and malformed/non-numeric/boolean acceptance thresholds. A bright outline with dark interior must not be accepted as a filled face candidate.
- Added negative regression tests for interior holes, malformed area/fill thresholds and wrong calibration dimensions. Existing rectangle mode, camera ownership, and real pose solver remain unchanged.
- No claim of real clubface detection or physical impact; Gates 20–24 remain OPEN; physical tests deferred; no merge/release. Verify CI on new SHA.

---

# PHASE 5 GATE 21 UNMOCKED SYNTHETIC PERSPECTIVE POSE REGRESSION (2026-11-11)

- Verified exact-SHA `3dd6f5ca`: all six GitHub Actions workflows SUCCESS.
- Added end-to-end **unmocked** synthetic regression: render a tilted planar quadrilateral from known metric pose using OpenCV camera projection, place it in a correctly bracketed two-frame capture, extract its image corners through the new quadrilateral mode, and solve with the existing real IPPE pose estimator. Assert reprojection RMS and metric translation/rotation within tolerances that account for integer rasterization.
- This is simulated image-domain evidence only, not real clubface recognition, hardware calibration or contact timing. Gate 21 remains OPEN pending real-world evidence and further robustness; all physical tests deferred until all Gates are software-complete.
- New SHA CI still requires verification. No merge or release.

---

# PHASE 5 GATE 21 QUADRILATERAL-TO-EXISTING-POSE BRIDGE (2026-11-11)

- Verified exact-SHA `d410c78b` and `c3652a5e` CI: all six workflows SUCCESS for both.
- Added explicit `observation_mode=\"quadrilateral\"` to existing `estimate_capture_synthetic_face_pose`, retaining `rectangle` default and rejecting unsupported modes. Reuses the existing quadrilateral image extractor and planar PnP solver, no duplicate solver or camera owner.
- Added isolated synthetic wiring test (spy solver) and unsupported-mode rejection. No claim of unmocked positive perspective pose accuracy or physical clubface identity. Gates 20–24 OPEN. Hardware tests deferred; no merge/release.
- New SHA CI must be verified independently.

---

# PHASE 5 GATE 21 SYNTHETIC PERSPECTIVE QUADRILATERAL (2026-11-11)

- Preserved existing strict axis-aligned rectangular fixture proposal and pose solver unchanged. Added **optional** `synthetic_face_quadrilateral.py` to extract four ordered image corners from a single isolated convex bright perspective quadrilateral in an offline captured frame.
- Fail-closed checks: exactly one connected contour, size, convex four-vertex polygon, border margin, fill and upright synthetic ordering. Shot/session/frame provenance retained through existing immutable observation model. Regression tests cover perspective synthetic positive, blank/multiple objects, circle, border, wrong frame and threshold.
- Explicit limitation: a bright quadrilateral does not identify a real clubface. Corner ordering is only a synthetic upright convention, not arbitrary rotation, handedness or physical contact. No automatic real-world pose/contact claims. Existing camera owner and geometry solver unchanged.
- Earlier `d410c78b` PR Checks and Documentation passed; remaining CI pending at observation time. Verify CI at new SHA. No merge/release; physical tests and screenshots deferred.

---

# PHASE 5 CI TEST-FIX: TRIGGER BRACKETING (2026-11-11)

- Read exact-SHA CI at `a1d87ce8ab03be1391663874b1caac3ec3956dd8`: PR Checks, Documentation, Pylint, UI, Foundation SUCCESS; Python 3.11 Tests FAILURE: 7 new tests failed because their single-frame synthetic captures violated the pre/post trigger timing contract. Python 3.10/3.12 jobs cancelled.
- Fixed **test fixtures only**: two strictly monotonic synthetic frames, pre-trigger count 1, trigger host timestamp bracketed between frames. No weakening of `validate_candidate_frame_index`, camera timing, pose solver or image provenance.
- Recheck new exact SHA CI; Gates 20–24 remain OPEN; no physical tests, merge or release.

---

# PHASE 5 GATE 21 SYNTHETIC CAPTURE-TO-POSE COMPOSITION (2026-11-11)

- Audited existing selected-frame synthetic corner extractor and `estimate_synthetic_face_pose` planar PnP contract before implementation. Added `estimate_capture_synthetic_face_pose` as a thin provenance-preserving bridge, **not** a duplicate pose solver or camera reader.
- Tests verify selected-frame image-derived pixels reach the existing solver, rejection before solver on missing image evidence, propagation of ambiguous pose rejection and invalid frame identity. The positive wiring test spies on the solver; it is **not** an unmocked physical or positive pose-accuracy test.
- Rectangle fixture is synthetic only; real clubface landmark identity, arbitrary perspective corner extraction and contact instant remain unverified. No physical tests until all 35 Gates developed software-first; no merge/release.
- CI on the exact new SHA remains to be verified.

---

# PHASE 5 GATE 21 IMAGE-DERIVED SYNTHETIC LANDMARK PROVENANCE (2026-11-11)

- Audited existing Gate 08/10 synthetic IR face-region proposal, Gate 22 selected-frame image validator and Gate 21 supplied-landmark pose solver. Reused the strict rectangular detector rather than creating a competing clubface detector or camera owner.
- New `synthetic_face_pixel_observation.py` extracts four ordered corner pixels from the **selected buffered image** and binds shot/session/frame identity, with defensive immutable pixel copy. Tests cover valid rectangle, no/ambiguous rectangles, frame/dimension mismatch and invalid provenance.
- This is a synthetic axis-aligned rectangle fixture ONLY; the pixel corner order is not proof of real clubface identity, handedness, perspective shape, physical face geometry or contact. The existing pose solver remains unchanged; end-to-end real-world observation still OPEN.
- All 35 Gates software-first, physical testing and user screenshots deferred; no merge/release. CI must be checked at the new exact SHA.

---

# PHASE 5 GATE 22/24 OFFLINE FRAME EVIDENCE SELECTION (2026-11-11)

- Audited Phase 5 HANDOFF, current scope matrix, existing `synthetic_frame_candidates.py`, `offline_capture_batch.py`, `synthetic_impact_quality.py`, and tests before implementation. The previous batch already assesses explicit frames; do not duplicate capture, geometry or pose solvers.
- Added isolated `offline_frame_selection.py`: a bounded, deterministic, fail-closed **unique synthetic geometry** selector consuming existing assessed frames. Exactly one accepted synthetic geometry frame yields a synthetic candidate; zero yields no selection; multiple yield an ambiguous result with **no** selected frame. Reject duplicate/malformed identities and inconsistent quality. No physical contact inference, timing, frame ranking, image-derived clubface landmarks or uncertainty estimate.
- Added hardware-free tests for unique/none/ambiguous outcomes, input limits, contradictory quality, duplicate IDs and forbidden physical validation claims. This is a new software capability, not final Gate 22 or 24 acceptance.
- All physical ELP tests and user-supplied screenshots remain deferred until all 35 Gates are developed as far as possible without hardware. No merge/release. Exact-new-SHA CI must be checked; do not inherit previous passing CI.

---

# PHASE 5 GATES 20–24 SOFTWARE EVIDENCE REVIEW (2026-11-11)

- Read-only PR #45 audit at exact SHA `925c1a3f3248c0112ff7708356117fde20b0a9d0`: Tests, Foundation, UI, Pylint and Documentation all SUCCESS; PR Checks FAILURE (PR metadata). Positive rendered-image integration is in the passing test suite; this does not prove physical accuracy.
- Reconciled stale Phase 5 scope status and recorded per-Gate implemented offline evidence, concrete missing software and separately deferred physical work in `MDP_V1_2_PHASE5_GATES20_24_PARALLEL_SCOPE.md`. Gates 20–24 remain OPEN. In particular, image-derived clubface landmark extraction and contact-frame selection remain absent; supplied face pixels and manually chosen frames must not be described as measured detections.
- Canonical approved MDP V1.2 acceptance text not verified in repository. No final Gate closure without reconciliation. All physical tests postponed until all 35 Gates are developed as far as possible without hardware. No merge/release.
- This documentation change requires its own new-SHA CI verification; previous successful CI belongs only to the audited SHA.

---

# PHASE 5 CI REPAIR AND TEST BOUNDARY (2026-11-11)

- Read-only audit exact SHA `b81b14e128fbfde8c83ac685da9a35f4f6fdb87d`: Tests FAILURE (Python 3.11: 2751 passed, 1 failed, 7 skipped; 3.10 and 3.12 cancelled), Foundation/Pylint/UI/Documentation SUCCESS; PR Checks FAILURE.
- Root cause: test `test_rejects_accepted_result_missing_coordinates` attempted `dataclasses.replace(..., x_mm=None)` and expected aggregate-audit rejection, but `SyntheticImpactResult.__post_init__` correctly fails closed at construction. Updated test to assert the earliest model-validation boundary. No production geometry logic changed.
- Positive unmocked rendered-image integration test was not listed among failed tests on Python 3.11; this does not establish hardware accuracy or all-version CI success. New SHA CI pending.
- All physical tests remain postponed until all 35 Gates are as complete as possible without hardware. Gates 20–24 OPEN. No merges/releases.

---

# PHASE 5 GATES 20–24 POSITIVE RENDERED-IMAGE INTEGRATION (2026-11-11)

- Read-only audit PR #45 exact SHA `81effe47bfe20c9111b5d65bfc9e101e1b536016`: Documentation SUCCESS; Tests, Pylint, Foundation, UI IN PROGRESS; PR Checks FAILURE.
- Added a positive **unmocked** synthetic image-to-contact regression: render a 720-sample sphere silhouette to an actual uint8 frame; use OpenCV contour extraction, calibrated rays, sphere cone estimation, projected face landmark pose, contact geometry, quality assessment and batch audit. Verify known 12mm toe / 5mm high synthetic contact within 5mm tolerance; no physical accuracy claim.
- The test is committed but **not yet confirmed passing**. If CI fails, diagnose exact test failure and correct within scope. No physical ELP camera or live shots until all 35 Gates are developed as far as possible. Gates 20–24 OPEN; no merge/release.

---

# PHASE 5 GATES 20–24 INTEGRATED OFFLINE BATCH ENTRY POINT (2026-11-11)

- Read-only audit PR #45 exact SHA `b32f84f0bb2100e8813e12a0b3880893001e2231`: Documentation SUCCESS; Tests, UI, Pylint, Foundation IN PROGRESS; PR Checks FAILURE.
- Added `assess_offline_capture_batch`, one explicit bounded offline API that composes selected-frame contour extraction, synthetic face observations, per-frame impact/quality and a validated aggregate evidence audit. No physical contact frame selection, accuracy claims or camera acquisition.
- Integration regression tests cover two independently rejected selected frames (blank vs real disk with degenerate face pixels), batch counts, fail-closed status, duplicate frame and resource limit. Positive full image-to-contact acceptance remains an explicit outstanding item.
- All hardware-dependent testing postponed until all 35 Gates are developed as far as possible without hardware. Gates 20–24 OPEN; no merges/releases. New SHA CI pending.

---

# PHASE 5 GATE 24 BATCH AUDIT HARDENING (2026-11-11)

- Read-only audit PR #45 exact SHA `2c247dc262e08c7100a25fcc65a4364617b26d24`: five technical workflows SUCCESS, PR Checks FAILURE.
- Hardened offline aggregate audit against malformed nested assessment types, negative/boolean frame identities and accepted impact results missing coordinates or regions. Added focused regression cases.
- All physical calibration, camera capture and live golf shots explicitly postponed until all 35 Gates have been developed as far as possible without hardware. Gates 20–24 remain OPEN. No merges or releases. New SHA CI pending.

---

# PHASE 5 GATES 20–24 BATCH AUDIT AND REJECTION MATRIX (2026-11-11)

- Read-only audit PR #45 SHA `49c9f793375b7aa74f7572ebf54c47ad9ca5d652`: Documentation SUCCESS; Tests, Foundation, UI, Pylint IN PROGRESS; PR Checks FAILURE.
- Added `audit_synthetic_candidate_batch`: validates consistent synthetic status/quality, distinct frame IDs, rejection reasons and hidden rejected coordinates, and forbids physical accuracy claims. Summarizes all four status categories without selecting a physical contact frame. Offline tests cover four statuses and contradictory/invalid results.
- Positive end-to-end image-derived impact remains pending; this audit does not replace it. Gates 20–24 OPEN. No hardware tests, merges or releases. New SHA CI pending.

---

# PHASE 5 GATES 20–24 BATCH DEVELOPMENT: MULTI-FRAME OFFLINE ASSESSMENT (2026-11-11)

- Read-only audit PR #45 exact SHA `2f66f312ac08b50a94093b5e2991aa51f0e2e38e`: all five technical workflows SUCCESS (Tests, UI, Pylint, Foundation, Documentation); PR Checks FAILURE (PR metadata).
- New bounded pure `assess_synthetic_frame_candidates` evaluates multiple **explicit** frame candidates in one call. Each candidate retains its frame index and independently supplied face pixels, and receives an individual synthetic result plus quality report. No best-frame selection or physical contact timestamp inference.
- Strict input validation: bounded nonempty tuple, unique nonnegative integer indices, finite Nx2 face pixels copied to read-only arrays, positive integer maximum. Offline tests cover multiple different rejection stages, invalid frame, pixel aliasing, duplicate indices, malformed batches, invalid pixels and limits.
- Caller face metadata identity is internally tied to the corresponding frame index; this is not proof of actual face pixel origin. Successful full image-derived impact and physical accuracy remain unverified. Gates 20–24 OPEN; no hardware tests, merges, releases. New SHA CI pending.

---

# PHASE 5 GATE 24 FACE-FRAME IDENTITY QUALITY PROPAGATION (2026-11-11)

- Read-only audit PR #45 exact SHA `99a7fc0b4ddeb4d3940274af1e48de42068c44b0`: Documentation SUCCESS; Foundation, Tests, Pylint, UI IN PROGRESS; PR Checks FAILURE.
- Propagated optional `face_observation_frame_index` through the public quality wrapper to the underlying capture-impact function. Regression verifies mismatched face-frame metadata fails closed and quality carries the same rejection reason without coordinates or invented uncertainty.
- Metadata does not prove pixel origin. Physical contact and successful image-to-impact positive test still open. Gates 20–24 OPEN; no hardware tests, merges, releases. New SHA CI pending.

---

# PHASE 5 GATE 21/23 OPTIONAL FACE-FRAME IDENTITY GUARD (2026-11-11)

- Read-only audit PR #45 exact SHA `bdf5580dd05ecde77c88c92ee9d903e511ca3a4f`: Tests, Pylint, Foundation, Documentation SUCCESS; UI IN PROGRESS; PR Checks FAILURE.
- Added opt-in `face_observation_frame_index` to selected-frame synthetic impact calculation. If supplied, mismatched or boolean frame identity is rejected before contour processing and without impact coordinates. Existing callers remain unchanged.
- This is **metadata consistency only**, not proof that externally supplied face landmarks were detected from that frame. Positive image-to-contact integration and actual face feature extraction remain open. No physical tests, merge, release. New SHA CI pending.

---

# PHASE 5 GATE 24 SELECTED-FRAME POSITIVE CONTOUR / NEGATIVE FACE REGRESSION (2026-11-11)

- Read-only audit PR #45 exact SHA `ab6bbd2e690991169173e9563cca95c6a0ecef4f`: Documentation SUCCESS; Tests, Pylint, Foundation, UI IN PROGRESS; PR Checks FAILURE.
- Added actual synthetic grayscale disk frame integration test: selected-frame contour is extracted and passes the single-contour stage, while deliberately degenerate face landmarks must reject downstream geometry without publishing coordinates. Quality reason must match rejection.
- This is **not** the still-pending positive full impact result. The earlier accepted-quality regression mocks geometry. Face pixel provenance and physical contact remain unverified. Gates 20–24 OPEN; no hardware tests, merges, releases; new SHA CI pending.

---

# PHASE 5 GATE 24 ACCEPTED-RESULT COMPOSITION REGRESSION (2026-11-11)

- Read-only audit PR #45 exact SHA `756aa4cc56876e238d1be53e8aada3e02ef5cd61`: Documentation SUCCESS; Tests, Pylint, Foundation, UI IN PROGRESS; PR Checks FAILURE.
- Added isolated acceptance-path regression for `assess_capture_ball_synthetic_impact`: injected successful synthetic geometry is carried unchanged to the quality report, with physical validation False and uncertainty None. Existing real selected-frame negative integration test remains.
- This test **mocks the underlying geometry calculation**; it does not establish a successful camera-frame-to-contact end-to-end case. Such a case and face-observation provenance remain open. Gates 20–24 OPEN; no hardware tests, merges, releases. New SHA CI pending.

---

# PHASE 5 GATE 24 END-TO-END SYNTHETIC QUALITY COMPOSITION (2026-11-11)

- Read-only audit PR #45 exact SHA `ea34c998371f5d3bbfaa09defbd493ee497af62c`: Foundation, Pylint, Documentation SUCCESS; Tests and UI IN PROGRESS; PR Checks FAILURE.
- Added `assess_capture_ball_synthetic_impact` composing selected-frame bright contour, synthetic face impact and explicit quality assessment in one offline call. Integration test verifies absent ball produces no coordinates, carries rejection reason consistently and never invents physical validation or millimetre uncertainty.
- Face landmarks remain externally supplied; successful real-world impact, physical timing and accuracy unverified. Gates 20–24 OPEN. No hardware tests, merges or releases; new SHA CI pending.

---

# PHASE 5 GATE 24 SYNTHETIC QUALITY CONTRACT (2026-11-11)

- Read-only audit PR #45 exact SHA `60f558feab6425b9ec57890f13ba7f6f6c986ec4`: Documentation and Pylint SUCCESS; Tests, UI, Foundation IN PROGRESS; PR Checks FAILURE.
- Added pure `assess_synthetic_impact_quality` summary for accepted and rejected synthetic results. Accepted geometry is explicitly **not** physically validated; uncertainty in millimetres is `None`, never invented. Rejected results retain their explicit reason. Added offline tests for accepted, each rejection status, and invalid input.
- This is a reporting contract, not a validated statistical uncertainty estimator. Gates 20–24 OPEN; no hardware tests, merges or releases. New SHA CI pending.

---

# PHASE 5 GATES 20/22/23 CAPTURE-CONTOUR SYNTHETIC IMPACT COMPOSITION (2026-11-11)

- Read-only audit PR #45 exact SHA `719faa9a445cbb3ee84381f0ffb546a5b9b282a8`: Tests, Pylint, Foundation, Documentation SUCCESS; UI IN PROGRESS; PR Checks FAILURE.
- Added `calculate_capture_ball_synthetic_impact`, composing selected-frame image validation, image-derived contour, and existing synthetic observed-impact geometry with explicit matching frame identity. Offline negative integration tests reject absent contours and invalid frame indices without coordinates.
- Face landmark pixels remain caller-supplied and **are not independently proven to come from the same frame**. No physical impact timing, classification or accuracy established. Gates 20–24 OPEN; no hardware tests, merges or releases. New SHA CI pending.

---

# PHASE 5 GATES 20/22 SELECTED-FRAME CONTOUR PROVENANCE (2026-11-11)

- Read-only audit PR #45 exact SHA `8ca95cd1c817102a6ddebfdb7037f7f093dca3dc`: Tests, Pylint, Foundation and Documentation SUCCESS; UI IN PROGRESS; PR Checks FAILURE.
- Added `extract_capture_ball_contour`: validates a selected buffered frame and extracts a contour **from that frame's copied image**. Returns immutable contour with shot/session/frame identity, unlike independent caller-supplied pixels. Tests cover valid extraction, wrong frame, invalid capture identity/dimensions and ambiguous components.
- Does not identify the object as a golf ball, establish contact time, derive face landmarks, or publish a physical impact. Gates 20–24 OPEN. No hardware tests, merge or release; new SHA CI pending.

---

# PHASE 5 GATE 22 EXPLICIT OBSERVATION IDENTITY MODE (2026-11-11)

- Startup audit PR #45 exact SHA `885b5ce757f0daa1e0b4ebee9a2fa6c927bbad14`: Documentation SUCCESS; Tests, UI, Pylint, Foundation IN PROGRESS; PR Checks FAILURE.
- Added opt-in `require_observation_frame_identity=True` to the synthetic impact composition: rejects missing explicit observation index, while existing index consistency and timing checks reject mismatches. Preserves previous synthetic callers by default; added missing-index rejection and matching-index acceptance tests.
- This verifies only declared metadata consistency, **not** image-pixel provenance, contact instant or real impact accuracy. Gates 20–24 OPEN; no physical tests, merges or releases. New SHA CI pending.

---

# PHASE 5 GATE 21 LANDMARK BORDER QUALITY (2026-11-11)

- Read-only audit PR #45 head `dffc2efa8b2673d6eafd106f64918ed7901ab7c2`: Documentation and Pylint SUCCESS; Tests, Foundation and UI IN PROGRESS; PR Checks FAILURE.
- Added optional, explicitly bounded image-edge margin to existing planar face landmark pose estimator. Calibrated pixels within the excluded border now reject before pose estimation. Preserves default behavior and existing camera ownership; synthetic acceptance, rejection and invalid-parameter tests added.
- This is a supplied-landmark observation-quality check, **not automatic clubface landmark extraction** or physical accuracy evidence. Gates 20–24 OPEN; no physical tests, merge or release. New SHA CI pending.

---

# PHASE 5 GATE 20 OPTIONAL SILHOUETTE CIRCULARITY (2026-11-11)

- Exact-SHA startup audit of PR #45 `32003d727ab6254146187dfe192e6531e9688715`: Tests, Pylint, Foundation, UI and Documentation SUCCESS; PR Checks FAILURE.
- Added explicit optional `min_circularity` threshold (0..1) to the existing bright-contour extractor, forwarded by contour-to-ball-range composition. Rejects elongated candidates using OpenCV area/perimeter, with offline disk, elongated shape and invalid-threshold tests. Default zero preserves prior synthetic callers.
- Circularity is a shape heuristic, not golf-ball identification or physical accuracy. Gates 20–24 OPEN; no hardware tests, merges, releases. New SHA CI pending.

---

# PHASE 5 GATE 20 OFFLINE CONTOUR-TO-SPHERE COMPOSITION (2026-11-11)

- Exact-SHA startup audit of PR #45 `c68deb447d25d1d893ffef9f42474322cfcee6b3`: Tests, Pylint, Foundation, UI and Documentation SUCCESS; PR Checks FAILURE on metadata.
- New pure `estimate_bright_ball_position` composes existing single-bright-component extraction, calibrated pixel rays and existing ball silhouette range solver; validates calibrated image dimensions before processing. No duplicate ray or sphere solver, no camera reader.
- Added offline disk/invalid-dimensions/ambiguous-component/invalid-radius tests. Brightness is not proof of golf-ball identity, and synthetic results are not physical accuracy evidence. No live impact publication. Gates 20–24 OPEN; no hardware tests, merges, releases. New SHA CI pending.

---

# PHASE 5 GATE 20 SYNTHETIC BRIGHT CONTOUR EXTRACTION (2026-11-11)

- Read-only startup audit of PR #45 exact HEAD `3be171b1aa2b870f6631f9ae97f0bd6c178d7b87`: Tests, Pylint, Foundation, UI, Documentation SUCCESS; PR Checks FAILURE on PR metadata.
- Added a pure offline OpenCV bright-foreground contour extraction helper with caller-specified intensity threshold, minimum contour area and border margin. Rejects zero/multiple eligible components, invalid image type/size, invalid thresholds and clipped contours. Reuses existing Gate 20 contour quality validator; does not add a camera reader.
- Synthetic regression tests included. A bright connected component is **not** proof of ball identity, roundness, contact timing or physical accuracy. Not wired to physical measurement publication. Gate 20–24 OPEN; no physical tests, merge or release. New SHA CI pending.

---

# PHASE 5 GATE 22 OPTIONAL IMAGE-DOMAIN INTEGRATION (2026-11-11)

- Startup audit PR #45 head `57da15f6ac977a263561761844622fe96aa267a0`: Documentation, Pylint, foundation SUCCESS; Tests and UI IN PROGRESS; PR Checks FAILURE on metadata.
- Integrated `validate_capture_frame_image` into synthetic observed impact behind explicit `validate_frame_image=True` opt-in. A supplied capture/index must now contain a grayscale uint8 image matching calibrated dimensions, otherwise fail closed without impact coordinates. Default False preserves prior synthetic placeholder-frame tests. Added integrated rejection/acceptance and missing-capture regression tests.
- Fixed accidental literal backslash-n in function docstring. Image validation **does not establish** that independent ball/face pixels came from selected image. No automatic detection, physical contact inference, hardware tests, merge or release. Gates 20–24 OPEN; exact-SHA CI pending.

---

# PHASE 5 GATE 22 OFFLINE CAPTURE IMAGE DOMAIN (2026-11-11)

- Read-only audit of PR #45 head `ddf2b2abc585c669216dcff4927a35605ce2c661`: Pylint, foundation, Documentation SUCCESS; Tests and UI IN PROGRESS at audit; PR Checks FAILURE on metadata. No claim of completed CI.
- New standalone `validate_capture_frame_image` verifies explicit candidate index, capture timing/identity, uint8 2D grayscale image and exact declared calibrated width/height; returns a defensive copy. Eleven hardware-free cases test valid copy, mismatched shape/dtype, invalid size, invalid provenance.
- This is a **pure validator**, not automatic image extraction or proof that independently supplied ball/face pixels came from the image. It does not create a camera reader or alter existing synthetic impact API. No physical tests, merge or release. Gates 20–24 OPEN; exact-SHA CI pending.

---

# PHASE 5 GATE 22 OBSERVATION-FRAME METADATA BINDING (2026-11-11)

- Startup audit: PR #45 at `1b5e7d55077350dca695eb7ea73e2c9f863bb42b`; CI was in progress for Tests/Pylint/Foundation/UI, Documentation SUCCESS and PR Checks FAILURE on metadata. No CI success inferred.
- Gate 22 synthetic impact API gains optional `observation_frame_index`. If supplied, it requires a valid capture and a valid index identical to the explicit candidate frame index. Reject mismatched, out-of-range or malformed observation indices without coordinates. Existing callers remain compatible.
- Important: this binds **caller-provided metadata only**; it cannot prove that pixel observations were extracted from that image, or that the image contains physical contact. Future image extraction must carry trusted frame provenance.
- Added offline integration regression tests. One atomic source/test/handoff commit; verify exact-SHA CI. Gates 20–24 remain OPEN. No physical tests, merges, releases.

---

# PHASE 5 GATE 24 CI TEST-DATA FIX (2026-11-11)

- Exact-SHA CI at `bf87de053d90ea996077c549731c35b027722c2a`: Tests FAILURE (Python 3.10: 2650 passed, 1 failed, 7 skipped); Pylint, foundation, UI and Documentation SUCCESS; PR Checks FAILURE on metadata.
- Root cause: Gate 24 regression parameter contained literal backslash+t rather than a tab character; whitespace-only validation correctly did not reject that nonblank string. Test now uses the actual tab escape in Python source. Production code unchanged, assertions retained.
- Batch updates test and handoff together; reverify CI on the new SHA. Gates 20–24 OPEN; no hardware tests, merge or release.

---

# PHASE 5 GATE 24 RESULT INVARIANT BATCH (2026-11-11)

- Read-only startup audit of PR #45 head `f9c1fef0be725cf922988fa772a984d01cd5b4d7`: Tests, Pylint, Face Impact foundation, UI and Documentation SUCCESS; PR Checks FAILURE (title/description metadata).
- Gate 24: accepted synthetic impact results now reject whitespace-only horizontal or vertical region labels, consistent with existing rejected-result nonblank reason validation. Added four offline regression cases. No change to physical measurement semantics.
- Source, tests and handoff committed atomically to minimize CI runs. New exact-SHA CI is pending. Gates 20–24 remain OPEN. No physical camera test, merge, release or PR-check bypass.

---

# PHASE 5 GATE 20 RESULT-CONTRACT HARDENING (2026-11-11)

- Read-only startup audit of draft PR #45 at `bbb8a5f7a14da70ea975e1fd9f60a931fbe76b40`: all five technical workflows SUCCESS; PR Checks FAILURE due title and required PR-description sections. Source and tests inspected before editing.
- Gate 20: reject invalid/nonfinite/boolean or inconsistent range, angular radius and residual in immutable BallSilhouettePosition results. Tests cover malformed scalar diagnostics and valid contract; no physical accuracy claim.
- Atomic batch changes source, tests and handoff in one commit. CI for this new HEAD pending; do not infer results from preceding SHA. Gate 20–24 OPEN. No hardware tests, merges, releases, or PR check bypass.

---

# PHASE 5 GATE 22 CI CONTRACT FIX (2026-11-11)

- Read-only audit at `2d1fab4cd3502319790c3c7c3c40f2db17e86869`: Documentation, Pylint, Face Impact foundation and UI passed; Tests failed 3 assertions on changed error wording. PR Checks still fail title/description. CI logs show all 3 failures expect substring `missing capture identity` while the new stricter identity validator returned `missing or invalid capture identity`.
- This atomic batch preserves existing diagnostic contract `missing capture identity` while retaining the new requirement that shot_id and session_id be nonblank strings. No test weakening, no hardware changes. All source/tests from previous batch remain.
- CI for new SHA must be checked; gates 20–24 remain OPEN. No physical tests, merge or release.

---

# PHASE 5 GATE 22 IDENTITY VALIDATION BATCH (2026-11-11)

- Read-only startup audit of draft PR #45, head `b7483af87ba55972df97239bfbcf736376e85af7`: Tests, Pylint, Face Impact foundation, UI and Documentation all SUCCESS. PR Checks FAILURE: title and missing required description headings.
- Gate 22 hardening: require both shot_id and session_id to be nonblank strings, not merely truthy values; reject malformed integers, booleans, lists and whitespace-only identity. New focused regression tests. This protects offline provenance validation only; it does not infer physical contact or bind supplied pixels to a capture frame.
- Changes to source, tests and handoff committed atomically once to minimize GitHub CI. New commit CI must be verified before claiming acceptance. PR metadata still requires edit; no tool currently available for PR edits.
- All Gates 20–24 OPEN; physical testing deferred until all 35 Gates developed. No merges/releases.

---

# PHASE 5 GATE 22 BATCH REGRESSION CHECKPOINT (2026-11-11)

- CI on `ae78a6991a5c239084e8e092087eec9dc2943fdb`: **all five technical workflows passed** (Tests, Pylint, Face Impact foundation, UI, Documentation). PR Checks failed exclusively on conventional title and required PR-description sections. Do not claim PR Checks green.
- This batch adds synthetic integration regression tests for invalid capture session identity, nonmonotonic host clock, unbracketed trigger and omitted candidate index. Every rejection must expose no impact coordinates or region labels. No actual image-to-frame correspondence verification and no contact timing inference.
- PR metadata still needs a compliant title and required headings; no connected PR-edit tool available. Do not change CI rules or bypass checks. CI on this batch's new SHA is pending.
- User-approved batched development: keep code, tests and handoff in same Git tree commit to reduce redundant CI. Gates 20–24 remain OPEN, no physical tests until all 35 Gates developed, no merge/release.

---

# PHASE 5 BATCH CI FAILURE AND FIX (2026-11-11)

- Read-only audit of draft PR #45 at `d6b701f853a6ee35710c30ced2829712458c7109`: Documentation, Pylint and Face Impact foundation passed; Tests FAILED on Python 3.11 (2627 passed, 1 failed, 7 skipped); UI still in progress at audit. PR Checks failed on nonconventional PR title and missing required PR description sections, NOT on screenshot check according to job list.
- Exact failure: `test_mismatched_calibration_size_is_rejected` expected `dimensions`, but newly inserted Gate 20 contour border validation rejected the observation first. This batch fixes fail-closed validation ordering: `calculate_synthetic_observed_impact` now rejects `image_size != calibration.image_size` before contour inspection, with explicit dimensions message. Regression test also supplies a clipped contour and mismatched dimensions to lock precedence.
- PR metadata must be updated separately (title conventional, description headings `Why was this required?`, `Automated tests`, `Manual (human) testing`), without claiming manual testing. GitHub tool surface currently has no PR edit action; do not bypass governance or invent screenshots.
- Source, regression test and handoff committed together in one Git tree/ref update to minimize CI. Recheck CI on resulting HEAD. Gates 20–24 OPEN; no physical testing, merge or release.

---

# PHASE 5 BATCH DEVELOPMENT CHECKPOINT (2026-11-11)

- User approved batching changes to reduce GitHub Actions cost. This checkpoint is included in the **same Git tree commit** as source and tests, rather than a separate handoff push.
- Batch integrates optional Gate 22 timing provenance into `calculate_synthetic_observed_impact`: caller can supply a `TriggeredCapture` and explicit `candidate_frame_index`; invalid timing/identity/index rejects with `INVALID_GEOMETRY` and no impact coordinates. Existing synthetic-only callers remain supported. This is **NOT** frame-image correspondence verification, a physical contact detector, or a claim that the trigger equals impact time. No second camera acquisition owner.
- Synthetic integration tests cover accepted explicit candidate, out-of-range candidate, and missing capture. Source/test/handoff committed together. CI must be checked at resulting HEAD; do not claim green until verified.
- Gates 20–24 remain OPEN. No physical testing until 35 Gates, no merge or release without separate approval.
- Next: same-SHA CI, correct failures as one batch, then continue quality/uncertainty integration. Prefer single Git tree/commit/ref update per coherent batch.

---

# PHASE 5 GATE 20 OBSERVED IMPACT INTEGRATION (2026-11-11)

- Read-only audit of PR #45 at `64e1a674f685898b4331a4301ac84f8d5213ec0c`: draft, technical workflows queued at time of check; no latest-SHA CI success claimed.
- Commit `8b67a41407edc4e99851151cfc5789b259612b4d`: `calculate_synthetic_observed_impact` now calls `validate_ball_contour_pixels` before calibrated ray inversion. Optional explicit `ball_border_margin_px=0.0` maintains existing caller compatibility. Invalid or clipped contours yield existing `INVALID_GEOMETRY` rejection with no impact coordinates. This is synthetic/offline only.
- Commit `bafabf36ec3e01887435e78d4d893f616fbf00df`: synthetic observed-impact tests check rejection for border clipping and accepted known contact with positive margin.
- Important: No actual image contour detector, no physical contact timing, no ELP hardware test, no release/merge. Gate 20–24 remain OPEN. Latest code has NOT been verified against same-SHA CI; inspect and fix technical failures. Reassess whether optional zero margin is sufficient for eventual physical observations (requires evidence).
- Next: exact-SHA CI, then Gate 21/22/23/24 synthetic end-to-end gating and quality contract; avoid asserting physical accuracy. Handoff update advances SHA.

---

# PHASE 5 GATE 20 IMAGE-DOMAIN CONTOUR QUALITY (2026-11-11)

- Draft PR #45 audited at `9d57a2484e0d94543989c7c332f3bb10bf9e50d4`: Documentation passed; foundation and Pylint in progress; Tests, UI and PR Checks queued. Prior `6c741f57...` had Documentation, Pylint, foundation green; Tests/UI in progress; PR Checks failed. **Do not claim latest SHA CI green.**
- Gate 20 new standalone offline contour-quality validator `src/openflight/camera/ball_contour_quality.py` at commit `cd1be109138974fe97f6f5bf773b7bf4e0233801`: checks image dimensions, explicit safe border margin, >=5 finite distinct pixel pairs, clipping; returns a defensive copy. This does **not** detect contours, infer ball identity or assert physical accuracy.
- Gate 20 tests `tests/test_ball_contour_quality.py` at `82494302338c5fc2bf4d9728fe033947401fbc6d`: valid copy, bad shapes/nonfinite/duplicate samples, border clipping, invalid image/margin.
- This is standalone; next step is to integrate into the synthetic observed-impact path with an explicit configurable margin, and verify existing call sites/tests before modifying signatures. Calibrated ray solver already checks ray coverage and consistency separately.
- Gate 22 explicit frame-index and provenance checks, Gate 21 pose quality, Gates 23–24 impact result invariants remain in same branch; see previous handoff entries. Recheck exact-SHA CI and resolve technical failures. No physical tests, merges or releases.

---

# PHASE 5 GATE 22 CANDIDATE FRAME CHECKPOINT (2026-11-11)

- PR #45 remains draft/unmerged. Last read-only audit of `6c741f579fba1bd8d2359687cb9b886368635be8`: Pylint and Documentation passed; foundation in progress; Tests, UI and PR Checks queued. A much older SHA `70093cfae191068f4eb7056f5b43e4c65e575e9b` had all technical workflows green, with PR Checks red (deferred screenshots). **No same-SHA green claim for latest changes.**
- Gate 22 commit `b912d31a3e1bf237bb5cf2890c6f7aebfad576c7`: `validate_candidate_frame_index(capture, candidate_index)` now requires valid capture timing/identity and an explicitly supplied bounded frame index. It does NOT infer the physical impact instant from trigger or timestamps. Test commit `e051dc75e39eebe2f2a0e72097cbd385fb1496c8` checks accepted indices, invalid indices and rejected provenance.
- This is an offline contract helper only, **not yet wired into impact calculation or live publication**. The selected candidate remains a hypothesis, not verified physical contact.
- Next: verify CI on new HEAD, check Pylint and tests, then continue Gate 20 contour quality and Gate 21/23/24 integration. No physical tests until all 35 Gates, no merge/release without authorization. Handoff commit advances HEAD.

---

# PHASE 5 GATE 22 RING INTEGRATION TEST CHECKPOINT (2026-11-11)

- PR #45 read-only audit: HEAD `85e87a96545adbb117f966907ea17a216405085b`, draft, unmerged. All six PR workflows were **queued** when checked, including Tests, Pylint, UI, Documentation, foundation and PR Checks. **No same-SHA pass has been verified.**
- Commit `872a3ff4b19495ced1e2f225ef9a05801ca5ec39` adds an offline Gate 22 regression test feeding actual `TriggeredFrameBuffer` frames, firing a deterministic host trigger, consuming `TriggeredCapture`, checking shot/session identity and passing it to `assess_trigger_timing`. Also tests rejection when trigger precedes the last pre-frame host timestamp. No hardware involved.
- **Important:** This integration test only exercises synthetic frame metadata and the existing ring buffer; no physical contact timestamp is inferred. Gate 22 validator is still standalone and not connected to real measurement publication.
- NEXT: Recheck GitHub CI on latest HEAD after this handoff commit; avoid repeatedly pushing documentation-only commits if CI is queued. If technical CI fails, inspect job logs and fix. Also inspect existing `SyntheticImpactResult` constructors for Gate 23–24 contract compatibility and reconcile exact MDP V1.2 Gate definitions before closeout. Continue approved parallel Gates 20–24, no merge/release/physical testing.

---

# PHASE 5 GATE 22 OFFLINE TIMING PROVENANCE (2026-11-11)

- Draft PR #45 remains the approved Phase 5 work surface; no merge/release/physical tests.
- Read `triggered_buffer.py`, `capture_runtime.py` and `test_camera_triggered_buffer.py`. Existing `TriggeredCapture` has distinct sensor timestamps, host timestamps, host trigger time, shot/session IDs and pre/post frame boundary. This is a pre-existing camera ring, not proof of actual impact instant.
- Gate 22 implementation commit `e2d7859f14f9c7ad985440f5f6cb97828c99c89c`: new pure `src/openflight/camera/trigger_timing_quality.py` rejects missing pre/post frames, bad/missing shot/session identity, invalid/nonmonotonic sensor or host clocks and host triggers not bracketed by the pre/post host timestamps. It **does not** compare unrelated sensor and host clock epochs, infer contact time or create a second acquisition owner.
- Gate 22 synthetic tests commit `94ff3f3b89b3aed21895b0d72fc6c6e2eb0d7042`: valid and rejected capture provenance, nonmonotonic clocks and distinct clock origins.
- This is an **offline validator not yet wired to a physical publication path**. It is not hardware calibration or exposure-time verification.
- The latest new commit's CI is not verified. Inspect exact-SHA workflow outcomes and fix failures; consider whether the host trigger bracketing rule is too strict for a real asynchronous trigger before integrating (keep it a conservative rejection until justified).
- Gate 20, 21, 23 and 24 changes are documented in preceding handoff sections. Recheck their CI and result-constructor compatibility. Current handoff edit advances HEAD.

---

# PHASE 5 PARALLEL GATES 21, 23, 24 — CHECKPOINT (2026-11-11)

- Branch `mdp-v1.2/phase5-gates20-24-parallel`, draft PR #45 https://github.com/andersdui22/openflight-face-impact/pull/45 (unmerged). At previous SHA `70093cfae191068f4eb7056f5b43e4c65e575e9b`, Documentation, foundation and Pylint succeeded, UI and Tests were still in progress, and PR Checks failed on the deferred screenshot policy. These are NOT checks on the new commits below.
- **Gate 21** code `5c91e524e274b037267954e9dfdf8d36300b22bf`: existing synthetic planar pose estimator rejects malformed RMS/margin thresholds before OpenCV. Tests `01f09cc1b3d4f893b0d0a7bb63b977962a07dd0b`: invalid scalar/bool/array/nonfinite thresholds.
- **Gates 23–24** code `7e6002af00663ee2af776ac530cf9ffdc01c7621`: synthetic impact result contract enforces finite coordinates and populated region labels for accepted results, and forbids coordinates/regions on rejected results, requiring an explicit rejection reason. Tests `061a6ee3bbff102af4ef6b0953c87536f029a900`: contradictory-result regressions.
- **Gate 20** earlier code and tests remain on the branch; Gate 22 timing/trigger provenance audit is still pending.
- All new code is synthetic/offline only; no physical camera tests, merge, release, new camera receive owner, or claims of physical pose/impact accuracy.
- **Immediate next step:** verify the new exact-SHA technical CI; inspect and correct failures. Audit all existing `SyntheticImpactResult` constructors for compatibility with new fail-closed invariant. Then audit Gate 22 timestamp source and shot/session ownership. Update this handoff after meaningful milestones. This handoff commit advances SHA, so re-fetch remote HEAD.

---

# PHASE 5 GATE 20 IMMUTABILITY CHECKPOINT (2026-11-11)

- Draft PR #45 remains unmerged. At last observed PR HEAD `7c2b89af1cf96d27cb55e2f97d4465e23c331f83`, Documentation succeeded, other technical CI workflows were in progress, and PR Checks failed under the previously deferred screenshot requirement. Do not claim technical CI passed.
- Gate 20 commit `a155ae8b54fcd13b0e16aedf07f361a227aa80e2`: `BallSilhouettePosition` now validates, copies and write-protects its camera XYZ result array to prevent caller mutation/aliasing of an accepted observation.
- Gate 20 commit `9d913ecfd1bb8f9d94594b454daf722de0008d9e`: regression tests for write protection, caller-array aliasing and invalid result coordinates.
- **New commits require same-SHA CI verification**. Next: inspect tests/Pylint on newest head and fix introduced failures. Continue only within approved Gates 20–24; no physical ELP tests, merge or release.
- This handoff edit advances HEAD again; always fetch current GitHub HEAD and CI before continuing.

---

# PHASE 5 PR AND CI CHECKPOINT (2026-11-11)

- Created **draft PR #45**: https://github.com/andersdui22/openflight-face-impact/pull/45, head `mdp-v1.2/phase5-gates20-24-parallel`, base `mdp-v1.2/phase4-gates17-19-parallel`. No merge/release.
- PR creation triggered GitHub Actions on SHA `d3992511719458bec1d09ca5689cff4f963ad9be`. At observation, Tests, Pylint, UI, Documentation and PR Checks were **in progress**; Face Impact foundation **queued**. No successful same-SHA result yet. Recheck latest HEAD after this handoff commit and verify **its** CI.
- Gate 20 source and regression test commits: `105e99ec`, `ff801f0e`. Only strict validation of supplied radius and angular residual budget has changed; no physical ball detector or camera reader added.
- Next: inspect failing CI jobs if any, fix within scope, then continue bounded Gate 20 observation-quality and Gate 21 pose-validation work. Keep this file current after milestones.

---

# PHASE 5 IMPLEMENTATION UPDATE — GATE 20 (2026-11-11)

- Verified Phase 5 branch `mdp-v1.2/phase5-gates20-24-parallel` at prior handoff SHA `2d388f87537ab6216ece5b1b61b84043d9f48822`; no PR-triggered workflow runs were returned for that SHA (not a pass).
- Read `src/openflight/camera/ball_silhouette_range.py` and `tests/test_ball_silhouette_range.py`. Reused the existing sphere/rim estimator; **did not** add a second camera owner or detector.
- Gate 20 code commit `105e99ec15159e019c23e4aa35f89b11e95fc336`: fail-closed scalar type checking for radius and angular residual budget, avoiding exceptions or ambiguous NumPy array truth values.
- Gate 20 test commit `ff801f0e7f1361013e137e7927d81a766b0f842e`: malformed scalar/radius/budget regression cases. These are synthetic hardware-free tests, not physical accuracy validation.
- **CI for `ff801f0e` and this handoff's newer SHA has NOT been verified**. Next: check same-SHA CI; if absent because no Phase 5 PR exists, create a draft PR on the approved Phase 5 branch with the proper stacked base, then verify checks. Fix any introduced failures.
- Continue Gates 20–24 within user-approved scope. All physical testing deferred until after development of 35 Gates; no merge/release/screenshot bypass.
- Read the current full handoff and `MDP_V1_2_PHASE5_GATES20_24_PARALLEL_SCOPE.md` below before resuming.

---

# CURRENT HANDOFF — PHASE 5 GATES 20–24 (2026-11-11)

**READ THIS FIRST.** This section supersedes earlier status snapshots below. GitHub is authoritative for current HEAD, CI, PRs and files. Re-audit before any code change; this handoff is a dated snapshot.

## Mission and authorization
- Project: standalone Windows **OpenFlight Face Impact** using one **ELP OV9281 USB camera**; reuse existing Python/OpenCV and React/Electron code. No ConnectorNext, MLM2PRO, Bluetooth, radar, GSPro or upstream OpenFlight edits.
- Law: `docs/governance/PROJECT_LAW.md` **Project Law V1**. The user explicitly approved **parallel development of Phase 5 Gates 20–24**, starting with read-only audit, then hardware-free tests and CI. Physical testing is postponed until development of **all 35 Gates**. **No merge, release or physical testing** without separate authorization. UI screenshots are deferred, **not waived**; never fake or bypass PR Checks.
- Working repository: `andersdui22/openflight-face-impact`. Current Phase 5 branch: `mdp-v1.2/phase5-gates20-24-parallel`, branched from Phase 4 integration SHA `fcda0ff666eb6c39f90777947d8b70a55a172492`. Phase 5 scope/audit commit `659d51988ce0dd2540a683469907208dd0947894`. **This handoff edit creates a newer HEAD: verify it remotely before claiming same-SHA CI.**
- Phase 4 integration: branch `mdp-v1.2/phase4-gates17-19-parallel`, draft PR **#44** (unmerged). Six technical workflows passed on code SHA `8e44a8584d95dfa6ea5229e9af5072c862fcfb60`; subsequent Phase 4 documentation SHA `fcda0ff6` had mixed completed/in-progress checks at the last audit. PR Checks failed due deferred screenshot requirement. Gates 17–19 remain OPEN; do not claim physical acceptance.
- Earlier draft PRs #40–43 were not merged at Phase 5 startup. Check their current status independently. No physical Golden baselines exist.

## Phase 5 read-only startup audit and next work
- Scope and acceptance directions: `docs/governance/MDP_V1_2_PHASE5_GATES20_24_PARALLEL_SCOPE.md`. Read that file, `PROJECT_LAW.md`, `ACTIVE_CHANGE_GATE.md`, `BASELINES.md`, `CANDIDATES.md` and this handoff before resuming. The older `ACTIVE_CHANGE_GATE.md` contains historical Gate 14/15 text and is not the latest Phase 5 authorization; the user's current approval plus Phase 5 scope govern the new work.
- Gate 20: ball detection/silhouette/observation quality. Existing `src/openflight/camera/ball_silhouette_range.py` estimates a sphere centre from explicit calibrated silhouette rays, known radius and angular residual; `calibrated_rays.py` provides rays. Neither physically detects ball pixels or proves accuracy. Next: audit existing tests and add minimal **pure fail-closed observation-quality validation** with focused tests; no second camera reader.
- Gate 21: clubface detection and 3D pose. Reuse `synthetic_face_landmark_pose.py`, `synthetic_pose_observability.py`, `synthetic_mesh_pose.py`. Reject ambiguous/nonobservable poses and unsupported physical inference.
- Gate 22: contact instant and temporal reconstruction. Inspect single acquisition owner, buffered frame metadata, shot/session identity and timing source. Do not equate host-arrival with exposure timestamp or fabricate subframe contact.
- Gate 23: face-local impact coordinates, centre distance and face boundaries. Reuse `synthetic_observed_impact.py`, `synthetic_impact_pipeline.py`, `synthetic_face_polygon.py` and Phase 4 planar reference contracts; rejected impacts have no coordinates.
- Gate 24: uncertainty, quality controls and explicit rejection. Keep offline residuals separate from physical accuracy and carry provenance into results.
- The canonical Master Development Plan V1.2 file was **not found in the inspected GitHub tree**; Gate names were recovered from prior user-approved conversation. Reconcile before individual closeout; do not invent unverified acceptance criteria.
- The existing `get_synthetic_face_impact` SocketIO endpoint is a synthetic demonstration, **not** a physical ELP measurement publication boundary. Do not gate it on physical calibration or modify unrelated radar processing. Physical mode, lens/crop identity, face pose, real club geometry and physical impact accuracy remain UNKNOWN.
- Candidate registry includes restricted 690CB assets. Do not import restricted models or assume licensing.
- No Phase 5 production code or tests have yet been changed as of this handoff. Phase 5 CI for `659d5198` was not returned by the PR-triggered workflow query (no Phase 5 PR yet); **do not interpret absence of runs as a pass**.

## Resume procedure / evidence discipline
1. Fetch current branch SHA and any PRs from GitHub. Reconcile drift against this snapshot; inspect exact-SHA CI. Do not assume a clean local checkout from remote contents alone.
2. Read Project Law, active scope, baseline/candidate registers, handoff and relevant source/tests. Confirm approved change boundaries before editing.
3. Continue Gate 20 read-only code/test audit, then minimal hardware-free implementation with tests; work Gates 21–24 in parallel only where dependencies allow.
4. Record each new commit SHA, same-SHA CI, changed files, failures and unknowns. Maintain this **top-of-file current handoff** after meaningful milestones and before handing off; keep earlier snapshots below for history.
5. No merges, releases, physical tests, destructive Git operations, screenshot bypass or unsupported physical accuracy claims. Draft PR and exact-SHA CI are separate from Gate acceptance.

---

# GATE 13 USER-APPROVED TECHNICAL CLOSEOUT — 2026-11-10

The user explicitly approved technical closeout of Phase 3 Gate 13 after all technical CI checks passed on exact SHA `b4843c71b326a0c6adb02127d974756bdfec70b7`. This approval **closes Gate 13 technically**, not physically. The previously deferred screenshot-in-PR-description requirement remains **deferred, not waived**, and the PR description completeness check remains failed. Physical ELP camera testing, calibrated measurement validation and end-to-end Electron/Python backend integration remain unverified.

- Branch: `mdp-v1.2/phase3-gate13-camera-preview`; draft PR #39, open/unmerged, stacked on draft PR #38.
- Technical scope delivered: existing USB status and buffered JPEG endpoints integrated into six-panel Camera Preview; honest camera/offline/error and non-measurement states; single camera owner preserved; mocked Playwright coverage.
- All technical checks succeeded on exact pre-closeout SHA `b4843c71b326a0c6adb02127d974756bdfec70b7`: Python 3.10–3.12, Playwright E2E, UI unit, build, lint, formatting, Pylint, Windows diagnostics and quality checks. This governance update creates a new HEAD; recheck exact-SHA CI.
- **No Gate 14 implementation is authorized.** Next permitted work: read-only audit and prepare Gate 14 scope/approval proposal under Project Law V1. No merge, release or physical testing.

---

# CURRENT STATUS OVERRIDE — PHASE 3 GATE 13 TECHNICAL ACCEPTANCE (2026-11-10)

**Read this first.** GitHub is authoritative; verify current branch HEAD, exact-SHA CI, Project Law and PR before continuing. Older handoff sections are archived historical snapshots.

- Repository `andersdui22/openflight-face-impact`; Project Law V1; Master Development Plan V1.2 (8 phases / 35 Gates). No upstream OpenFlight or ConnectorNext modifications.
- Gate 12 was technically closed by user on `fa142ca893a375f9c45a3ef8d962296f92b460dc`. Its draft PR #38 remains unmerged; screenshot requirement deferred, **not waived**.
- Gate 13 explicitly approved by user: integrate existing buffered USB JPEG `/api/camera/preview.jpg` into six-panel Camera Preview, report `/api/camera/usb/status`, preserve single camera reader, show offline/error states, add simulated integration tests. Branch `mdp-v1.2/phase3-gate13-camera-preview`, draft stacked PR #39 https://github.com/andersdui22/openflight-face-impact/pull/39 (unmerged).
- Implementation: `ui/src/components/FaceImpactCameraPreview.tsx` polls backend status every five seconds without overlapping status requests, displays a buffered JPEG still when running, and handles disabled/starting/stopped/error/offline/unavailable JPEG. `ui/src/App.tsx` uses a neutral non-measurement topbar instead of falsely claiming camera offline. No new capture loop.
- Tests: UI SSR component test, four mocked-camera Playwright scenarios, existing dashboard tests and Python camera contract tests. **All technical CI checks passed on exact code SHA `fd49b99167923f066af49877fa18ea4779dea2e5`**: Python 3.10/3.11/3.12, Windows diagnostics, UI unit, E2E, build, lint, Prettier, Pylint and quality checks. PR description completeness remains **failed** because screenshot evidence was deferred; do not bypass or claim pass.
- Limitations: periodic JPEG stills, not a validated continuous live stream; physical ELP camera and calibration have not been tested; no measured impact results. Electron portable EXE remains UI-only without bundled Python backend. Real hardware and backend connectivity are not verified.
- **Gate 13 is technically ready for separate user closeout decision, but remains OPEN.** No Gate 14, merge, release, or physical test authorized. This documentation commit changes HEAD; verify its exact-SHA CI before claiming new HEAD green.

---

# CURRENT STATUS OVERRIDE — PHASE 3 GATE 13 (2026-11-10)

**Read this first.** The Gate 12 and Phase 2 sections below are historical. Verify authoritative GitHub branch HEAD, exact-SHA CI, PR and Project Law before work.

- Repository `andersdui22/openflight-face-impact`; Project Law V1; Master Development Plan V1.2 (8 phases, 35 Gates). Do not change upstream OpenFlight or ConnectorNext.
- **Gate 12 technically closed by user** on `fa142ca893a375f9c45a3ef8d962296f92b460dc`, screenshot evidence deferred, not waived. Draft PR #38 unmerged.
- **User explicitly approved Gate 13** (2026-11-10): wire six-panel Camera Preview to existing `/api/camera/preview.jpg` and `/api/camera/usb/status`, preserve existing single camera owner/buffer, show offline state, add hardware-free integration tests. No Gate 14, physical testing, merges or releases authorized.
- Active branch `mdp-v1.2/phase3-gate13-camera-preview`, stacked on Gate 12; draft PR #39 https://github.com/andersdui22/openflight-face-impact/pull/39 (open/unmerged).
- Implementation: `ui/src/components/FaceImpactCameraPreview.tsx` periodically polls backend status (5 seconds) and requests existing buffered JPEG endpoint when backend reports running; handles disabled, starting, stopped, error, offline and JPEG failure; labels preview as non-measurement. `ui/src/App.tsx` mounts it in Camera Preview. Electron portable UI remains UI-only; Python backend is not bundled. Preview is periodic JPEG stills, not verified live video.
- Tests: `ui/src/components/FaceImpactCameraPreview.test.tsx` contains SSR checking-state test (not part of current UI CI). `ui/tests/e2e/gate13-camera-preview.spec.ts` covers offline backend, stopped camera, backend error and missing JPEG using mocked HTTP responses.
- **Exact verified SHA `db67c925e3a6cd1ded4dfffb70c53b6ca26ce872`: all technical CI succeeded** (UI build, lint, format, Playwright E2E, Python 3.10–3.12, Pylint, quality checks). `PR description completeness` fails due to previously deferred screenshot requirement; do not bypass or claim success. Earlier Prettier failure was corrected and mandatory workflow restored.
- **Known limitations / next Gate 13 tasks:** topbar in `ui/src/App.tsx` still hardcodes “FACE IMPACT CAMERA OFFLINE · SYNTHETIC PREVIEW” even if camera is running; reconcile this without duplicating capture. Check overlapping status polling and recovery behavior. No real ELP hardware test or Golden baseline. Update evidence after changes; each documentation commit changes HEAD and requires rechecking exact-SHA CI. Gate 13 remains open until separate user closeout approval.

---

# CURRENT STATUS OVERRIDE — PHASE 3 GATE 12 (2026-11-10)

**Read this first.** The older Phase 2 text below is historical and no longer the active authorization. GitHub is authoritative; verify HEAD, PR, exact-SHA checks and Project Law before acting.

- Repository `andersdui22/openflight-face-impact`; Project Law V1; Master Development Plan V1.2 (8 phases, 35 gates).
- User approved **Phase 3 Gate 12 only**, explicitly on 2026-11-10: single-owner Windows ELP USB camera architecture, Python/React interface inventory, status/lifecycle contract and hardware-free tests. Gate 13–15 implementation NOT approved. No merges, releases or physical tests.
- Active branch `mdp-v1.2/phase3-gate12-camera-architecture`; base Phase 2 technical-closeout SHA `79549289b7de332a3752f90911850346bcd9fcf0`. Draft PR #38 https://github.com/andersdui22/openflight-face-impact/pull/38 (stacked on Phase 2 draft PR #37). All drafts unmerged.
- Gate 12 architecture document: `docs/governance/MDP_V1_2_PHASE3_GATE12_ARCHITECTURE.md`. Existing `WindowsUsbCamera` has one reader and `TriggeredFrameBuffer`; server already provides `/api/camera/preview.jpg` and `/api/camera/usb/status`; legacy UI `CameraFeed.tsx` is not integrated into six-panel Face Impact dashboard. Phase 2 Electron portable bundle has no Python backend.
- Tests added in `tests/test_windows_usb_camera.py` for idempotent start/single camera owner and release/retry after failed open. Exact test commit `5d6862868d28b026e1c69e56c2cc7d8d7155df22`.
- On exact pre-handoff HEAD `651e54f76f1a5e6ddb78c82a4cb6d4e1bbf49449`, **all technical GitHub CI checks succeeded**, including Windows+Ubuntu USB camera fixtures, Python 3.10–3.12, E2E, UI, lint, format and Windows diagnostics. `PR description completeness` FAILED due to the previously user-deferred screenshot-in-PR-description requirement. Do not waive, bypass or claim it passed.
- This handoff commit changes HEAD: **recheck CI on the new exact SHA** before Gate 12 closeout. No physical evidence or Golden baseline. Gate 12 remains open pending exact-HEAD check and formal closeout; do not begin Gate 13.
- The user previously approved Phase 2 technical closeout on `79549289...` with screenshot still deferred; no merge/release. Prior handoff statements that Gate 10/11 are incomplete are outdated.

---

# CURRENT HANDOFF — OpenFlight Face Impact / MDP V1.2

**Updated:** 2026-11-10. **GitHub is authoritative.** Begin each successor chat with read-only verification of branch HEAD, PR, governance and exact-SHA CI. The archived material below is historical only.

## Active project and governance
- Repository: `andersdui22/openflight-face-impact`. Never modify upstream OpenFlight or ConnectorNext.
- Project Law V1: `docs/governance/PROJECT_LAW.md`. Approved Master Development Plan V1.2: 8 phases, 35 Gates.
- **Current authorization: Phase 2 Gates 09–11 bundled development approved**. User approved completing remaining Phase 2 gates consecutively on 2026-11-10.
- Active branch: `mdp-v1.2/phase2-gate09-demo-mode`, stacked on Gate08 branch `mdp-v1.2/phase2-gate08-ui-contract`. Draft PR **#37**: https://github.com/andersdui22/openflight-face-impact/pull/37. PRs #35 (Gate07) and #36 (Gate08) remain draft/unmerged.
- **Latest known branch commit before this handoff update:** `43842063c4668d0dc7c8b0f3fbee03215cb30531`. Fetch latest HEAD and reverify; handoff update itself changes HEAD.
- `Fortsæt` permits autonomous work within Phase 2 Gates 09–11. No merge, release, physical tests or later phases without separate user approval. Keep PR draft.

## Gate11 packaged EXE smoke verified — 2026-11-10
Exact code SHA `1dbf9d41d553790db4a15c61a1f85ab1aaef6110`: **all technical CI success**, including packaged Windows EXE launch and renderer check of six Face Impact panels. Windows workflow run `42838234719` succeeded. Screenshot artifact `gate11-windows-dashboard-screenshot` ID `13774303142`; portable bundle artifact ID `13774068585`. Screenshot was uploaded but not independently visually reviewed or inserted into PR description. PR description completeness still fails by user-deferred requirement. No physical tests, real ELP measurements, bundled Python backend, merge or release. Gate09–11 closeout evidence now exists; seek explicit Phase 2 closeout approval after rechecking latest HEAD. Latest documentation commit before this handoff update: `696c518c854dd5a74fa36bc6e0d3b441baa9a853`.

## Latest Gate10/11 CI evidence (2026-11-10)
Exact code SHA `9c54404e37bec28e8f7b215f26d276a0a2dc69fa`: **all technical CI passed**, including Windows `portable-exe` job (run `42810519769`), E2E, Prettier, lint, UI build/unit, Python matrix, pylint, Windows diagnostics. Downloadable development-only artifact ID `13761873646` named `gate10-windows-portable-development-only` (161,503,560 bytes) was produced. **Only** PR description completeness fails due to user-deferred screenshot. No GUI startup test, no hardware, no Python backend in portable EXE, no merge/release. Gate11 runtime/visual acceptance remains open. Acceptance evidence recorded in `docs/governance/MDP_V1_2_PHASE2_GATES10_11_ACCEPTANCE.md`. This handoff documentation update changes HEAD; check latest HEAD before declaring same-SHA status.

## Phase 2 bundled authorization — Gates 09–11 (2026-11-10)
User explicitly approved continuing all remaining Phase 2 Gates 09–11 and fixing GitHub CI errors afterward, without per-Gate pauses. This authorization does **not** include merges, releases or physical testing. Governance recorded in `docs/governance/ACTIVE_CHANGE_GATE.md`.
- Gate09 demo CI passed all technical checks on `2bb8e76271ef4bef217edfab9b92f8c110db5e94`. Screenshot-in-PR-description check remains deferred, not waived.
- Gate10 implementation now includes `scripts/build-face-impact-windows.ps1`, relative Vite asset paths, Electron local-file startup for portable mode, and manual-only `.github/workflows/gate10-windows-portable.yml` with bundle artifact validation. This produces a **folder-based EXE**, not a single-file installer, and excludes the Python backend. Windows runtime has **not** been verified.
- Gate11 acceptance checklist in `docs/governance/MDP_V1_2_PHASE2_GATES10_11_ACCEPTANCE.md`; pending new exact-HEAD CI and Windows EXE runtime/visual acceptance.
- Last known commit before this handoff update: `4f121a52b61d32b82d0931212bdd8aa11d7e7673`; fetch authoritative HEAD. PR #37 remains draft and unmerged. Avoid implying packaging is tested or Gate11 is accepted.

## Implemented in active Gate09
- `ui/src/components/FaceImpactSessionDemo.tsx`: deterministic, local React-only simulated shots with mm X/Y sample coordinates; enter/exit, add, reset, shot history, count and averages. Exiting demo clears synthetic session.
- `ui/src/App.tsx`: shared demo state renders points inside existing **Impact Distribution** SVG and a separate clearly labeled **DEMO METRICS — SIMULATED, NOT MEASURED** panel. Actual measurement metrics and legacy OpenFlight shot counts are not overwritten.
- `ui/tests/e2e/gate09-simulated-session.spec.ts`: Playwright lifecycle, plot, averages, reset, exit and clean re-entry.
- Existing six-panel Gate07 dashboard remains; Gate08 UI navigation/reset remain. CAMERA SETTINGS opens legacy OpenFlight Camera view, **not** a working ELP OV9281 Face Impact integration. Real camera and capture controls remain inactive.
- No real measurements, physical testing, hardware camera acquisition, release or merge.

## Verified CI and outstanding work
- On `c15bb140d5ea4e513e05f1e9d3b4e1f8da6d1f82`: E2E, UI build, lint, UI unit, Python tests 3.10/3.11/3.12, pylint and Windows diagnostics passed; Prettier failed on `ui/src/App.tsx`.
- GitHub Actions UI workflow run `42807074528` generated artifact `gate09-prettier-app` (artifact ID `13758513819`) containing exact Prettier-formatted `App.tsx`. On `c102635326f4d614d4b4ccb2aa68fb1323e803f6`, the resulting two formatting differences were applied to `App.tsx`; format and all other technical checks later passed on exact SHA `2bb8e76271ef4bef217edfab9b92f8c110db5e94`.
- Temporary diagnostic steps were **removed** from `.github/workflows/ui-build.yml` in `33e42f7c2003184b4344612c0b2c21e740cf96dd`. The original `npm run format:check` and all other CI checks remain active.
- PR description completeness **fails** due to the previously deferred screenshot-in-description requirement. User explicitly deferred screenshot; never claim waived, bypassed or passed, and do not repeatedly request it.
- **Gate09 closeout proposal:** `docs/governance/MDP_V1_2_PHASE2_GATE09_CLOSEOUT.md` added in `43842063c4668d0dc7c8b0f3fbee03215cb30531`. **Next:** verify exact new HEAD CI including Prettier, E2E, all Python versions, UI unit, build, lint and Windows diagnostics. Ask explicit user approval before closing Gate09 or opening Gate10.
- Minimize unnecessary GitHub Actions runs by batching meaningful changes. Do not disable CI checks without approval.

## Future Gates (NOT authorized)
- Gate10: Windows double-click EXE packaging.
- Gate11: visual and functional acceptance.
- Later phases: real ELP camera acquisition, calibration, geometry, tracking, mathematical impact model, integration and validation.

---

## Archived handoff from previous gate sequence
The material below predates MDP V1.2 and refers to historical Gate 25–31 work. It is retained as archive, **not** the active gate or authorization.

# Active handoff

Current snapshot: 2026-11-09. GitHub is authoritative. Start each session with a read-only audit.

## Gate 31 continuation point — 2026-11-09

- Project Law V1. Anders approved one offline integration from supplied synthetic ball-rim and labelled face pixels to the existing finite-face contact result.
- Branch `gate31/synthetic-observed-impact` starts from Gate 30 `3f91831bd62bd208b131559aa19cac56c41f85f5`. Draft PR #30 recorded seven successful workflows on that exact SHA and remains unmerged.
- [Gate 31 evidence](GATE31_SYNTHETIC_OBSERVED_IMPACT.md) states the input and tolerance contracts. Its draft PR records final same-SHA checks after publication; reverify GitHub before closeout.
- Gate 26 physical testing remains deferred. The current scope does not infer a contact frame or detect real image features. No physical Golden baseline. Next gate requires separate approval.

## Gate 30 continuation point — 2026-11-09

- Project Law V1. Anders approved synthetic planar face pose estimation with labelled correspondences and ambiguity rejection.
- Branch `gate30/synthetic-face-landmark-pose` starts from Gate 29 `9e924d5874f00f51792dddf620624f49a6587d62`. Draft PR #29 recorded seven successful workflows.
- [Gate 30 evidence](GATE30_SYNTHETIC_FACE_POSE.md) describes pose conventions, known metric tests and rejection criteria. [Draft PR #30](https://github.com/andersdui22/openflight-face-impact/pull/30) records the final SHA and CI.
- Gate 26 physical testing remains deferred. Physical landmark detection and end-to-end contact integration remain open. A new gate requires explicit approval.

## Gate 29 continuation point — 2026-11-09

- Project Law V1. Anders approved offline synthetic ball centre estimation from calibrated silhouette rays and an explicit radius.
- Branch `gate29/synthetic-ball-silhouette-range` starts from Gate 28 `60a4232463aed9352cfe7a631394ef6ff26a166f`. Draft PR #28 recorded seven successful workflows.
- [Gate 29 evidence](GATE29_SYNTHETIC_BALL_RANGE.md) describes source reuse, the synthetic range contract and its rejection criteria. [Draft PR #29](https://github.com/andersdui22/openflight-face-impact/pull/29) records the final SHA and CI.
- Gate 26 physical testing remains deferred. Real edge detection, clubface pose and impact remain unverified. A new gate requires explicit approval.

## Gate 28 continuation point — 2026-11-09

- Project Law V1. Anders approved offline ray conversion of synthetic ball and clubface observations.
- Branch `gate28/calibrated-optical-rays` starts from Gate 27 `3fde3dfa53dd8fb40683ebf694abcbb4a5aebc20`. Draft PR #27 recorded seven successful workflows.
- [Gate 28 evidence](GATE28_CALIBRATED_RAYS.md) describes Brown-five correction, synthetic known-ray verification and rejection checks. [Draft PR #28](https://github.com/andersdui22/openflight-face-impact/pull/28) records the final SHA and CI.
- Gate 26 physical testing remains deferred. Depth, world pose and hardware validation remain open. A new gate requires explicit approval.

## Gate 27 continuation point — 2026-11-09

- Project Law V1. Anders explicitly deferred all physical tests and approved offline checkerboard calibration on synthetic images.
- Branch `gate27/offline-checkerboard-calibration` is based on Gate 26 `5ab6f698802fb5d990b0f6a076a0a834e49453c2`. PR #26 remains an open draft with physical evidence pending.
- [Gate 27 scope and evidence](GATE27_OFFLINE_CHECKERBOARD.md) describes the experimental-source adaptation, known-optics checks and held-out image validation. [Draft PR #27](https://github.com/andersdui22/openflight-face-impact/pull/27) records the verified head and CI.
- Hardware calibration and physical Golden remain outstanding. Any next gate requires explicit approval.

## Gate 26 continuation point — 2026-11-09

- Project Law V1. Anders approved the physical ELP operator procedure. Scope and commands are in [Gate 26 ELP operator test](GATE26_ELP_OPERATOR_TEST.md).
- Branch `gate26/elp-operator-test` is based on Gate 25 `4bcb6d311949aa8c3763c957538b419b61f67200`, with eight successful workflows. PR #25 remains an open draft.
- [Draft PR #26](https://github.com/andersdui22/openflight-face-impact/pull/26) records the SHA and CI. Verify them before using the runbook.
- The user-operated Windows ELP test is deferred. No physical evidence or Golden baseline has been collected.

## Gate 25 continuation point — 2026-11-09

- Project Law V1. Anders explicitly approved the Windows desktop smoke and camera test preparation.
- Branch `gate25/windows-desktop-runtime` is based on Gate 24 `e022c2f2348e80d29e4ff3e627669c3dcfa8c645`, with six required successful workflows. PRs #1–#24 were open drafts at startup audit.
- Scope, Windows setup and automated acceptance are in [Gate 25 Windows desktop runtime](GATE25_WINDOWS_DESKTOP_RUNTIME.md). [Draft PR #25](https://github.com/andersdui22/openflight-face-impact/pull/25) records the verified head and CI.
- Physical camera evidence and physical Golden baseline are outstanding. The next physical validation procedure requires separate explicit approval.

## Gate 24 continuation point

- Repository: `andersdui22/openflight-face-impact`. Main: `a3ab081a8abff71fd344d4fd782412d624b99f3f`.
- Project Law V1. Gate 24 implementation is complete. Final closeout is effective after same-SHA CI verification on this documentation commit, recorded on [draft PR #24](https://github.com/andersdui22/openflight-face-impact/pull/24).
- Branch `gate24/react-python-localhost-e2e`, based on Gate 23 `8555d933e781458be5dfae205d1545a9d0369750`. Previously verified implementation HEAD `372aa1707fefba4b158ebeff5c30916f653c5073` passed six required workflows plus Anti-slop Audit. PRs #1–#24 were open, draft and unmerged at audit.
- Gate 24 verifies actual React-to-Python Socket.IO over localhost for synthetic accepted and rejected results, offline error and reconnection. Windows desktop lifecycle and physical measurements remain unverified by these tests. No physical Golden baseline.
- Next: read-only Gate 25 planning for Windows runtime and camera test preparation. Implementation requires separate explicit approval.

The sections below are historical snapshots.

## Authority and state

- User approved Gate 01 with `Det er godkendt. Fortsæt` after the concrete
  foundation-gate request. Project Law V1 is adopted for this project.
- Approved task: repository, governance and CI foundation only.
- Project repository: `andersdui22/openflight-face-impact`, public fork of
  `open-flight/openflight`; remote `main` at the source baseline. Read and
  branch write access are verified for this repository.
- Local preparation branch: `foundation/governance-ci`; remote branch created
  at the source baseline, foundation content not yet published.
- Official source baseline: `open-flight/openflight` `main`
  `a3ab081a8abff71fd344d4fd782412d624b99f3f`.
- Project remote main SHA: `a3ab081a8abff71fd344d4fd782412d624b99f3f`.
  Remote gate branch exists at the same source SHA. Project PRs and CI: **none**.
  Do not invent a same-SHA closeout.
- Completed: Phase 0 audit; Gate 01 local preparation is incomplete.
- Local checks: backend 2,079 passed/7 skipped; isolated geometry 2 passed;
  UI 248 passed plus lint/build/format; strict docs build passed. All are
  Linux results, not project GitHub CI or Windows hardware proof. Details in
  `docs/evidence/GATE01_PREFLIGHT.md`.
- Golden physical baselines: **none**.
- Physical test, merge and release: **not authorized**.

## Technical findings to preserve

The original Python backend and React/Electron UI exist. Pi camera capture,
preview, buffering and replay exist; a Windows ELP USB adapter and camera-only
shot lifecycle do not. Unmerged and forked geometry/Face Impact code exists,
but no validated physical strike-location accuracy. The project manifest
excludes Windows from uv's resolver environment. See
`docs/evidence/PHASE0_AUDIT.md` and `docs/governance/CANDIDATES.md`.

## Current blocker and next authorized action

The browser login was completed by the user, and the fork was created from
the exact official source baseline. The initial GitHub integration write
returned 403 because the new repository was not selected. Anders saved the
installation setting with this repository added while retaining the prior
selection. Branch creation then succeeded. Publish the reviewed foundation
tree, run project CI, open the approved draft PR and close out on its final
same SHA. Do not touch ConnectorNext.

Gate 02 Windows bootstrap is only a future proposal, requiring separate user
authorization after Gate 01 is complete. Recheck source and remote drift
before any resumed work.


## 2026-11-08 remote verification update

A subsequent read-only GitHub verification supersedes the earlier local-preparation
snapshot above. Gate 01 foundation changes were published and draft PR #1 was
opened: https://github.com/andersdui22/openflight-face-impact/pull/1 .
The gate branch and PR head were both verified at
`a6bee2f0cb8eadd88b40c3e80aff5935c0c5ebbf`; main remained at
`a3ab081a8abff71fd344d4fd782412d624b99f3f`.

Seven GitHub Actions workflow runs completed successfully on that exact
pre-document-update SHA: UI, Anti-slop Audit, Face Impact foundation,
PR Checks, Pylint, Documentation, and Tests. These are CI results,
not evidence of physical Windows camera capture or impact accuracy.
The project source and UI were unchanged by PR #1.

IMPORTANT: This handoff update itself changes the branch SHA, so the seven
previous results cannot be used as final same-SHA closeout evidence.
Verify the new remote HEAD and await all required CI checks on the final
documentation SHA before closing Gate 01. No merge, release, physical test,
or Gate 02 production work is authorized by this update.

## 2026-11-08 Gate 03 successor audit — supersedes earlier active-gate instructions

- Authoritative law: `docs/governance/PROJECT_LAW.md` (Project Law V1); active gate: `docs/governance/ACTIVE_CHANGE_GATE.md` and `GATE03_WINDOWS_ELP_CAMERA.md`. Gate 03 was explicitly approved by the user on 2026-11-08.
- Repository: `andersdui22/openflight-face-impact`; working branch `gate03/windows-elp-camera`; base `gate02/windows-bootstrap` at `546eff3f9a761891e16178de40afc617b29960ed`. PR #3 is open, draft, unmerged. PR #1 and #2 are also open draft stacked predecessors.
- Reviewed Gate 03 HEAD before this handoff update: `66d069b759c46a65a67cd0e256516d510304dca5`. This handoff update creates a newer SHA; verify remote HEAD again and never treat checks from an older SHA as final closeout.
- The USB adapter, preview, read-only status API and React status integration exist in the Gate 03 branch. Commit `be9a48ee0310929213e017c239bc2dc772b7d872` normalized JSX conditional formatting. Commit `66d069b759c46a65a67cd0e256516d510304dca5` corrected the USB runbook to reflect the implemented UI status.
- CI: GitHub connector's commit workflow-run and combined-status queries returned empty arrays for the reviewed SHA. This is **unverified**, not evidence of passing or failing. Inspect PR Checks/Actions through an authoritative source before closing Gate 03.
- Real rendered React screenshot is still missing. Do not use generated mockups as evidence. No physical ELP test, hardware FPS proof, Face Impact accuracy, Golden, merge or release has been authorized.
- Next authorized task: reconcile same-SHA CI evidence, investigate any failures, obtain a genuine UI screenshot through a real browser/test environment, and keep PR #3 in draft until acceptance evidence is complete. No ConnectorNext modifications.

## 2026-11-08 Gate 05 current handoff — authoritative successor section

This section supersedes all older "current" instructions above. On every new session verify GitHub HEAD, active gate, draft PRs and same-SHA CI rather than relying on this snapshot.

- Mission: standalone Windows single ELP OV9281 USB-camera Face Impact app, reusing existing OpenFlight backend and React/Electron UI. No ConnectorNext, MLM2PRO, Bluetooth, radar integration or upstream edits.
- Governance: Project Law V1 `docs/governance/PROJECT_LAW.md`. Gate 05 expressly approved by user ("Godkendt", 2026-11-08) after proposal to reuse existing geometry, build synthetic known-dimension calibration and test transforms/unknown inputs. Active gate `docs/governance/ACTIVE_CHANGE_GATE.md`; full scope `docs/governance/GATE05_SYNTHETIC_CALIBRATION.md`.
- Working branch: `gate05/synthetic-camera-calibration`, branched from Gate 04 immutable SHA `0a6aae04901d11b02b90fdc37d80005a731da866`. Gate 04 PR #4 https://github.com/andersdui22/openflight-face-impact/pull/4 is draft, unmerged; all eight workflows succeeded on its exact base SHA. User expressly postponed physical ELP test; do not ask to perform it now or mark it passed.
- Gate 05 initial documentation: `docs/governance/GATE05_CALIBRATION_INVENTORY.md`. Pure `src/openflight/camera/geometry.py::deroll_normalized_offsets` is reusable; existing `tests/test_camera_geometry.py` has two synthetic tests. `club_delivery.py` is experimental and radar-dependent, NOT a Face Impact requirement. `detector.py` ball detector assumes IR-lit dark background; suitability for ELP camera unknown.
- User clarified: club motion metrics (Club Path, AoA, speed, full swing analysis) are NOT product goals. Only short-window clubhead tracking if needed for contact-frame selection; face and ball localization, clubface orientation, contact-time and impact-position estimation are future separately approved gates. Do not develop Face Impact solver in Gate 05.
- Gate 05 approved scope: pure synthetic camera calibration with known reference geometry and millimeter units, explicit coordinate conventions, degenerate/invalid-input rejection, regression tests, documentation and CI. No physical calibration or accuracy claim, no presumed intrinsics, lens distortion, physical camera scale, clubhead mesh truth, or hardware results.
- Current work before this handoff update: Gate 05 branch created; active gate and calibration inventory documents committed. No Gate 05 production calibration code, draft PR or same-SHA CI closeout verified yet. **This handoff commit changes HEAD**; re-fetch HEAD and CI before claiming final checks. Keep all PRs draft and unmerged. Do not merge/release/nominate Golden without separate authorization.
- Next task: inspect existing geometry and test conventions; implement minimal synthetic planar reference mapping in isolated pure code, verify forward/inverse and invalid cases, run CI, open stacked draft PR based on Gate 04 branch, update handoff with verified SHA and CI status. No user physical action required.

## 2026-11-08 Gate 05 CI verification and next-session note

- Draft PR #5: https://github.com/andersdui22/openflight-face-impact/pull/5 ; stacked base Gate 04 `gate04/windows-elp-physical-validation`, unmerged.
- Last verified **pre-handoff** Gate 05 code HEAD: `b5741a00afbeed3619675d83846ac7a52dd1c10a`.
- On that exact SHA, GitHub Actions completed successfully: latest PR Checks run 42526658655 (superseding initial failed PR Checks run 42526592571 caused by nonconforming PR title/body, fixed in PR metadata), Documentation 42526592551, Pylint 42526592604, Tests 42526592599, Face Impact foundation 42526592575, UI 42526592588 (build, format, lint and e2e successful).
- Code: `src/openflight/camera/synthetic_calibration.py` pure affine pixel-to-planar-mm reference mapping and `tests/test_synthetic_calibration.py` hardware-free forward/inverse, degeneracy and invalid-value tests. No integration into live camera or impact computation. Only ideal planar synthetic mathematical behavior verified.
- This documentation commit **changes the branch HEAD**. Recheck exact new SHA and all applicable CI before declaring final same-SHA closeout. Do not conflate previous successful code SHA with a new documentation SHA.
- Keep Gate 05 PR draft and unmerged. Gate 04 physical validation deferred by user. No physical accuracy claim, Golden, merge or release authorization.

## 2026-11-08 Gate 06 active handoff — latest authoritative scope

- Explicit user approval: "Godkendt" to Gate 06 proposal for camera-frame/calibration integration using synthetic test data only, without physical camera testing or Face Impact calculation. Project Law V1 unchanged.
- Working repository `andersdui22/openflight-face-impact`; branch `gate06/synthetic-frame-calibration` created from Gate 05 HEAD `631c7bbb008da94c13a42c8596e4c7a9e589eb80`, which had all six same-SHA CI workflows successful. Gate 05 PR #5 remains draft/unmerged. No merge or release authorization.
- Active gate `docs/governance/ACTIVE_CHANGE_GATE.md`; scope and stop conditions `docs/governance/GATE06_SYNTHETIC_FRAME_INTEGRATION.md`.
- New isolated pure Python adapter `src/openflight/camera/synthetic_frame_calibration.py::map_frame_points_to_millimeters` reuses Gate 05 `SyntheticPlanarCalibration`, checks synthetic frame shape and point bounds, and maps caller-supplied (column,row) points to planar mm. New hardware-free regression tests `tests/test_synthetic_frame_calibration.py`. No automatic point detection, no live capture, no UI changes, no Face Impact solver.
- Gate 04 physical ELP validation remains deferred. No physical calibration/accuracy evidence or Golden baseline.
- At handoff authoring, last code commit `3190972e3d299c9e8e68c7a5df4b4cff2cafa22a`; this handoff commit changes HEAD. Open stacked draft PR #6 targeting Gate 05 branch; check new HEAD and exact-SHA CI before closeout, fix any failures. No physical user action required.

## 2026-11-08 Gate 06 six-workflow CI verification

- Verified draft PR #6 https://github.com/andersdui22/openflight-face-impact/pull/6, unmerged, at exact pre-handoff SHA `3f0653c99ad5f13e281a1fb6264cc158ba0c7fa3`.
- Six GitHub Actions workflows completed successfully on that SHA: Documentation run 42527299416, PR Checks 42527299424, Pylint 42527299573, Face Impact foundation 42527299559, Tests 42527299437, UI 42527299777 (including e2e). No failed workflow reported on that SHA.
- Evidence class: CI/software only. Synthetic frame pixel-coordinate mapping uses caller-supplied points and existing Gate 05 affine transform. No physical camera validation, automatic image detection, impact-location accuracy or Windows clean-install proof.
- This handoff edit creates a **new branch SHA**, so the six successful workflows above are not final same-SHA results for the new HEAD. Recheck and await the applicable CI on the new commit before final closeout.
- Gate 06 remains draft/unmerged; Project Law V1; Gate 04 physical test deferred. No merge/release/Golden authorization.

## 2026-11-08 Gate 07 approved synthetic localization — successor handoff

- Explicit user approval: "Godkendt" to Gate 07 proposal for synthetic ball and clubface localization; no physical ELP camera test or Face Impact computation. Project Law V1 remains unchanged.
- Repository: `andersdui22/openflight-face-impact`; branch `gate07/synthetic-ball-face-localization` based on Gate 06 `9522651a6a4be988f8bd8da22447b50cf1779099`. Gate 06 PR #6 is draft/unmerged; all six CI workflows succeeded on that exact Gate 06 SHA. Earlier PRs #1–#5 remain draft/unmerged. No Golden physical baseline; physical Gate 04 validation deferred.
- Gate: `docs/governance/ACTIVE_CHANGE_GATE.md`; scope `docs/governance/GATE07_SYNTHETIC_LOCALIZATION.md`.
- Source inventory: existing `src/openflight/camera/detector.py::BallDetector` assumes IR-lit ball against dark background and uses OpenCV Hough circles; not verified for ELP or synthetic annotated fixtures. No change to legacy detector, capture, React/Electron UI or calibration. `docs/governance/CANDIDATES.md` retains unadmitted external experiments and restricted mesh concerns.
- New `src/openflight/camera/synthetic_localization.py` recognizes strictly color-coded synthetic RGB fixtures: red perfect disk = ball; green filled rectangle = clubface. It returns pixel centers and bounding boxes, rejects missing/ambiguous/invalid markers. `tests/test_synthetic_localization.py` tests known positions and rejection cases. These synthetic labels do NOT imply automatic recognition of natural images or any physical accuracy.
- Last pre-handoff code commit: `81c6557c1d358053ca0fe36d4d345b28d3d0f0d7`. This documentation commit changes HEAD. Open stacked draft PR #7 targeting Gate 06 branch, then verify GitHub CI on latest exact SHA; diagnose failures without weakening tests. No merge, release or physical user action.

## 2026-11-08 Gate 07 CI and IR illumination evidence update

- User specified a physical 850 nm IR lamp for the planned ELP OV9281 Windows setup. This is user-reported hardware configuration, NOT a completed physical test or proof of detector suitability. No camera test requested or authorized.
- Existing `src/openflight/camera/detector.py::BallDetector` is designed for bright IR-lit ball on dark background and may be a reuse candidate for a later, separately approved real-image gate. No modification to the legacy detector in Gate 07; no assumption that 850 nm alone proves ball/face detection or physical accuracy.
- Verified Gate 07 draft PR #7 https://github.com/andersdui22/openflight-face-impact/pull/7, unmerged, at exact **pre-handoff** SHA `d05547a07a9282957ae67f2e22b13845aa839c23`: all six workflows completed success — PR Checks 42528065219, Documentation 42528065223, Pylint 42528065260, Tests 42528065270, Face Impact foundation 42528065335, UI 42528065222.
- This handoff update creates a NEW branch SHA; verify CI on the resulting SHA before same-SHA closeout. Gate 07 stays draft/unmerged, no physical/accuracy/Golden/merge/release claim.

## 2026-11-08 Gate 08 initial handoff — IR-style synthetic fixtures

- User explicitly approved Gate 08 ("Godkendt") for IR-style ball and clubface localization on synthetic images, reusing existing OpenFlight IR detector. Project Law V1 unchanged; physical tests remain deferred.
- Repository `andersdui22/openflight-face-impact`; branch `gate08/ir-synthetic-detection` from Gate 07 `cb8d13451dac1648d2f5c4f8921a5663ad9eb621` (all six CI successful, draft PR #7 unmerged). Prior PRs #1–#7 draft/unmerged. Golden physical baselines: none.
- Scope: `docs/governance/GATE08_IR_SYNTHETIC_DETECTION.md`; active gate `docs/governance/ACTIVE_CHANGE_GATE.md`.
- Read-only evidence: existing `src/openflight/camera/detector.py::BallDetector` uses OpenCV threshold/blur/HoughCircles and confidence heuristics on IR-bright ball vs dark background; actual ELP OV9281/850 nm image performance unknown. User reported an 850 nm IR lamp, but no physical measurement has been taken.
- Initial change: `tests/test_camera_ir_synthetic.py` exercises the unchanged existing detector with synthetic grayscale disks of controlled brightness and location, including no-detection cases. The fixture is not physical accuracy evidence. Pre-handoff test commit `8a3b4d8d394a88986056d17bce48eff905697dbc`.
- Next: open stacked draft PR #8 against Gate 07; inspect CI on latest handoff SHA, investigate any brittle Hough behavior. Evaluate controlled synthetic face-region detection only with evidence and within approved scope. No live camera, physical test, Face Impact computation, merge or release.

## Gate 08 continuation — synthetic IR face region (2026-11-08)

- Added `src/openflight/camera/synthetic_ir_face.py::locate_synthetic_ir_face` and `tests/test_synthetic_ir_face.py`. The new isolated fixture-only helper accepts exactly one bright filled axis-aligned rectangle in a uint8 grayscale **face-only crop**, returns inclusive pixel bounds and center, and rejects missing, ambiguous, incomplete or malformed synthetic fixtures. This is NOT natural clubface identification or pose estimation; bright reflections are not proof of a clubface.
- Latest **pre-handoff** code SHA `1cd7d87de0b52aa8c64d2ed63fd7658f8735effc`. CI snapshot: Documentation and PR Checks successful; Python Tests, Pylint, Face Impact foundation and UI in progress. Do not claim same-SHA CI success before completion.
- This documentation update advances the branch HEAD again; check the resulting SHA's CI. Keep draft PR #8 stacked on unmerged Gate 07, no physical tests, merge, release or Golden status.

## 2026-11-08 Gate 09 synthetic dual-object pipeline

- User explicitly approved Gate 09 ("Godkendt") for combining existing ball and face synthetic detection in one image process, without physical impact computation or camera testing.
- Branch `gate09/synthetic-dual-object-pipeline` from Gate 08 exact SHA `1bd4ad2919b4817cf3a6a8017f2b4d241684c9ff`, six of six CI success; draft PR #8 unmerged. Project Law V1 unchanged. Active scope in `docs/governance/GATE09_SYNTHETIC_DUAL_PIPELINE.md`.
- Added `src/openflight/camera/synthetic_dual_pipeline.py` composing unchanged `BallDetector.detect` and Gate 08 `locate_synthetic_ir_face` with explicitly supplied face-only crop bounds. Returns both detections in full-frame pixel coordinates, plus frame metadata. Rejects malformed/out-of-bounds crop, missing ball/face, extra bright pixels in crop, and synthetic ball/face overlap. No auto-crop discovery, natural image face recognition, geometry or physical impact inference.
- Added `tests/test_synthetic_dual_pipeline.py` with positive and negative hardware-free fixtures. Last pre-handoff code SHA `69654ddc7f470eb03870d994e4d597d2b92b6484`; CI not yet verified. Create stacked draft PR #9 against Gate 08 and verify all workflows on final SHA.
- No merge, physical tests, release or Golden baseline authorized.

## 2026-11-08 Gate 10 automatic synthetic face candidate proposal

- Explicit user approval "Godkendt" for a hardware-free automatic candidate region proposal on synthetic IR images. Base Gate 09 `c7d881f300b02fc0c6f6f91039e8bbf5f493acf8`, all six latest CI workflows successful; draft PR #9 unmerged. Project Law V1 unchanged.
- Active scope: `docs/governance/GATE10_SYNTHETIC_FACE_PROPOSAL.md`; branch `gate10/synthetic-face-region-proposal`.
- Added `src/openflight/camera/synthetic_face_proposal.py::propose_synthetic_ir_face_region`: connected-components scan of synthetic uint8 grayscale full frame, reuse Gate 08 strict filled-rectangle locator, return exactly one interior rectangular component in full-frame pixel coordinates. Reject zero/multiple rectangles and edge-touching rectangular candidates. Other shapes, such as the round synthetic ball, are not candidates. **This is not real clubface identification.**
- Added `tests/test_synthetic_face_proposal.py` with positive and fail-closed synthetic fixtures. Latest pre-handoff code SHA `420eab7a1ba64c0c6c82c3d2401d4771a65fb5cf`. Same-SHA CI still pending.
- No physical ELP testing, automatic real-world face detection, impact location, merge, release or Golden baseline authorized.


## 2026-11-08 Gate 11 camera-only synthetic 3D projection

User explicitly approved Gate 11 ("Godkendt") after the camera-only 3D projection proposal. Branch `gate11/camera-only-mesh-projection` started from Gate 10 SHA `3b4eca7149dbce637ac66c33a24f14c39bdc01d6`, with six same-SHA successful CI workflows and draft PR #10 unmerged. Scope is synthetic mesh projection with explicit intrinsics and extrinsics, orientation tests and fail-closed invalid calibration. Source references: upstream PR #250 SHA `8d244e25e41764bdeb5665a812af40ccf2e37b16`, `clubpose/mesh.py::rasterize_projected_triangles`, `clubpose/projection.py::_project`; original projection assumes fixed radar/rig world geometry. New isolated helper does not import the restricted 690CB asset. Its cv2 triangle filling is a narrow adaptation of the upstream projected silhouette behavior, not a claim of identical subpixel rasterization. No physical camera, real pose estimation, merge, or release authorized. Await exact-head CI before gate closeout.


## Gate 12 — 2026-11-08

Approved explicitly by user ("Godkendt"). Branch `gate12/synthetic-mesh-pose` starts from Gate 11 SHA `a45bbc93274cac42affe0545b3a06461eb1061a3`, whose six current PR CI workflows succeeded (prior PR title failure corrected). Gate 11 remains draft and unmerged. New synthetic candidate-only silhouette matching reuses Gate 11 camera projection and adapts the IoU fitting idea from upstream open-flight/openflight PR #250 `fit.py` at `8d244e25e41764bdeb5665a812af40ccf2e37b16`. No radar or restricted 690CB mesh. Results are discrete candidates with ambiguity rejection, not real 6DOF, clubface recognition, or millimetre impact measurements. No physical test, merge or release. Same-SHA Gate 12 CI pending.


## Gate 13 — synthetic pose observability (2026-11-08)

User explicitly approved Gate 13. Base Gate 12 SHA `32e09c5190316c082abe0d724acbeda8d9bc55e0` passed six CI workflows. Branch `gate13/synthetic-pose-observability` introduces bounded, candidate-set-specific synthetic silhouette overlap metrics and rejects near-identical orientations as unobservable. Tests include symmetric planar geometry with two distinct rigid orientations yielding identical camera silhouettes. This is NOT a physical angular error estimate, real 6DOF, impact location or a hardware test. Project Law V1, no Golden physical baseline; PR stays draft and unmerged. Exact Gate 13 CI pending.


## Gate 14 — synthetic clubface frame (2026-11-08)

Explicitly approved by user ("Godkendt") after proposal for heel/toe, vertical and center coordinate conventions. Branch `gate14/synthetic-face-coordinate-frame` from Gate 13 SHA `fbbbe9db38dcb4488372493fac1e985b7ae84e66`, six same-SHA successful CI workflows. New `synthetic_face_frame.py` transforms 3D points between world and synthetic clubface coordinates using validated rigid pose and right-handed orthonormal frame; no actual face dimensions, physical center, measurement, camera validation or millimetre impact claim. Tests cover identity, rotation/translation round-trip, signed off-plane distance and fail-closed invalid frames. PR remains draft/unmerged. Gate 14 exact-SHA CI pending.


## Gate 15 — synthetic sphere-plane Face Impact foundation (2026-11-08)

Explicit user approval ("Godkendt") for Gate 15. Branch `gate15/synthetic-ball-face-contact` starts from Gate 14 SHA `eb0ab8e28749758db06274a4214eaec1748bb3df` (six successful CI workflows, draft PR #14 unmerged). Added a strictly synthetic ball-to-infinite-planar-face tangency calculation, signed local mm coordinates and heel/toe/high/low labels. Requires explicitly provided ball radius and known rigid face pose; rejects gaps, penetration, wrong-side contact and invalid geometry. No actual clubhead finite face, curvature, measured ball position, physical impact, camera accuracy or release claim. Same-SHA CI pending. All PRs remain draft and unmerged.


## Gate 16 — finite synthetic clubface bounds (2026-11-09)

User explicitly approved Gate 16 ("Godkendt"). Branch `gate16/synthetic-finite-face-bounds` from Gate 15 SHA `2bb7039112f4089170df916410a565e5900bedff` with six successful same-SHA CI workflows; draft PR #15 unmerged. Adds an explicit positive finite rectangular face width and height (mm), validates Gate 15 tangent point inside inclusive centered edges/corners, rejects outside contact without expanding boundaries by tangency tolerance. Tests cover center, all edges/corners, outside by 0.001 mm, invalid dimensions, rotated face and Gate 15 non-tangency. This is synthetic-only; no real clubhead geometry or camera accuracy. No Golden physical baseline, merge or release. Exact Gate 16 CI pending.


## Gate 17 — synthetic polygonal face footprint (2026-11-09)

Explicit user approval ("Godkendt"). Branch `gate17/synthetic-face-polygon` from Gate 16 SHA `8915eb7f418b1eebf08e2c92a56e87edabee5ba7`, six same-SHA CI successes, draft PR #16 unmerged. Added finite simple polygon boundary in local face millimetres, including asymmetric and concave shapes, inclusive edges and corners, invalid/self-intersecting geometry rejection; reuses Gate 15 tangent calculation and Gate 14 face frame. Synthetic only, no actual clubhead asset, measured impact, physical camera, merge, release or Golden baseline. Same-SHA CI pending.


## Gate 18 — integrated synthetic Face Impact pipeline (2026-11-09)

Explicit user approval ("Godkendt"). Branch `gate18/synthetic-impact-pipeline` from Gate 17 SHA `bb4b6338edbdb1c3135db5d4e01d2b7f38f81dbc`, six same-SHA CI successes; draft PR #17 unmerged. Added `calculate_synthetic_face_impact` composing existing Gate 17 polygon containment and Gate 15 sphere tangency, returning either signed X/Y in mm with heel/toe/high/low labels, or structured outside-face/no-tangency/invalid-geometry rejection without partial coordinates. Synthetic-only known ball/face geometry; no real camera observations, actual pose accuracy, physical impact, merge, release or Golden baseline. Gate 18 exact-SHA CI pending.


## Gate 19 — synthetic Face Impact UI preview (2026-11-09)

Explicit user approval ("Godkendt"). Branch `gate19/synthetic-face-impact-ui` from Gate 18 SHA `fd96259236cc36b69af369e75416731a6dad8444`, six same-SHA CI successes, draft PR #18 unmerged. Added `ui/src/components/FaceImpactView.tsx` with SVG polygon, synthetic marker, signed X/Y millimetres, region labels and rejection state; wired an explicitly synthetic sample into the existing debug panel without replacing original OpenFlight React/Electron UI. Added server-rendered UI component tests. This is not a live backend feed or measured impact; no physical tests, merge, release or Golden baseline. Exact Gate 19 CI pending.


## Gate 20 — synthetic Python-to-React contract (2026-11-09)

User explicitly approved Gate 20 after Gate 19 six-workflow same-SHA success at `70daacd6dc72a9e86f2e952b0d584055ea49b45a`. Branch `gate20/synthetic-impact-contract` stacked on unmerged Gate 19. Gate 20 adds versioned static JSON scenarios `ui/src/data/syntheticFaceImpactCases.json`, Python tests proving the JSON outcomes exactly match `calculate_synthetic_face_impact`, and a React scenario selector inside the original debug panel. The UI displays the backend-shaped results but does not calculate Face Impact or receive a live backend stream. No camera, physical accuracy, merge, release or Golden baseline. Verify Gate 20 remote HEAD and same-SHA CI; this paragraph is a snapshot, not proof of completed checks.


## Gate 21 — local synthetic SocketIO bridge (2026-11-09)

Explicit user approval to reuse the existing Flask-SocketIO Python server and React socket.io-client without live camera or physical tests. Branch `gate21/synthetic-socket-bridge` stacked on Gate 20 exact SHA `ca4e5ebe6ba872ed30383f20bc3fe2c7ef3c6fe2` (six same-SHA successful workflows; PR #20 draft/unmerged). Python `synthetic_impact_socket.py` computes bounded known synthetic cases via Gate 18 pipeline; `server.py` handles `get_synthetic_face_impact` with an acknowledgment payload. The existing frontend socketService requests and validates the versioned response, and the original React diagnostic component shows server results or explicit disconnected/error states. No second socket, real camera observations, physical testing, merge, release or Golden baseline. Gate 21 CI and running-app proof remain pending; verify exact remote SHA before closeout.


## Gate 22 — synthetic Socket.IO integration tests (2026-11-09)

User expressly approved automated integration testing only. Branch `gate22/socket-integration-tests` stacked on Gate 21 `beaa98cb2b634945b696f6bac6f25bfb6c5d01dc` with seven same-SHA workflows successful; PR #21 draft/unmerged. New Python tests exercise Flask-SocketIO's in-process test client, real registered event dispatch and acknowledgment, success/rejection/unknown identifiers and a new session after disconnect. React tests exercise existing socketService with a mocked transport for acknowledgment, invalid/mismatched results, timeout, disconnect and reconnection. Distinguish in-process Python transport and mocked JS transport: this is NOT an end-to-end cross-process live network test, Windows desktop startup proof or camera measurement. No production camera, merge, release or Golden baseline. CI and closeout remain pending.


## Gate 23 — separate-process localhost Socket.IO (2026-11-09)

Explicit approval for synthetic-only localhost network tests. Branch `gate23/localhost-socket-e2e` stacked on Gate 22 `d2435307ac93f6025ac1098e6b5df685226cdf02` (six successful same-SHA workflows, draft PR #22 unmerged). New `tests/test_synthetic_socket_localhost.py` launches the existing Flask-SocketIO app in an isolated child process bound to 127.0.0.1 and exercises actual TCP Socket.IO acknowledgments from a separate python-socketio Client, including accepted and rejected synthetic cases, invalid identifiers, disconnect and a fresh connection. Hardware-oriented server main() is not invoked. This is Python-to-Python network integration, not a real React/Electron runtime, Windows desktop launch or camera measurement. CI verification pending. No merge, release, physical test or Golden baseline.


## Gate 24 — actual React browser-to-Python localhost (2026-11-09)

User expressly approved browser/Socket.IO integration. Branch `gate24/react-python-localhost-e2e` stacked on Gate 23 `8555d933e781458be5dfae205d1545a9d0369750` (six successful same-SHA workflows, PR #23 draft/unmerged). Reuses existing Playwright webServer configuration launching the Python backend in mock mode at 127.0.0.1:8080 and Vite React at 127.0.0.1:5173. New `ui/tests/e2e/synthetic-face-impact-localhost.spec.ts` drives the real debug panel and real browser Socket.IO client for accepted and rejected synthetic Face Impact, offline error and recovery. No browser transport mocks, new production code, camera or physical hardware. See the current continuation point above for CI evidence. Browser test is not Electron packaging or Windows startup proof. No merge, release or Golden baseline.
