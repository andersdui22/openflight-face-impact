# Software-first autonomous delivery plan — 2026-11-12

## Approved working approach
Deliver the largest coherent, reviewable batches practical. Do not request approval for individual implementation changes inside the approved scope. Preserve Project Law V1, MDP V1.2 and Gate-specific approvals. No upstream changes, merges or releases without separate authorization. Defer physical ELP camera testing until software is as complete as possible.

## Batch A — Gates 20–24, functional offline analysis
1. Establish exact-SHA CI baseline, inspect failures, repair blocking defects.
2. Replace supplied face landmarks with a testable image-derived landmark observation path where technically defensible; keep synthetic and real observations explicitly separated and reject uncertainty.
3. Exercise ball contour, face pose, temporal candidate selection, impact geometry and rejected cases with deterministic unmocked raster tests.
4. Wire a server-owned offline replay producer to validated, targeted Socket.IO events. No untrusted client-submitted measured impact payloads.
5. Exercise Python server -> actual Socket.IO -> React state -> impact history in an automated browser test.
6. Audit evidence provenance and traceability; update handoff and Gate criteria. Do not claim physical accuracy.

## Batch B — Windows launch and packaging
1. Define one-click Windows start contract for bundled Python backend + React/Electron UI, controlled shutdown and error reporting.
2. Build reproducible Windows packaging with clean-machine smoke test and CI artifact.
3. Verify camera is not opened in mock/synthetic smoke runs; defer hardware-dependent assertions.
4. Maintain explicit unsupported/physically-unvalidated UI indicators.

## Batch C — remaining software Gates
Implement later software-only Gates in cohesive increments with acceptance tests and handoff; record physical test blockers separately.

## Completion standard
A Gate is software-ready only when its exact acceptance criteria are demonstrably satisfied with reproducible tests, green required CI at the exact commit, documented limitations, and a traceable handoff. Physical-dependent Gates remain conditional/open pending real-camera validation. No claim of background execution: work progresses during active development sessions.
