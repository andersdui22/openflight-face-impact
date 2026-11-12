# Preparatory work for software integration and physical validation

The [approved MDP V1.2 archive](https://github.com/andersdui22/openflight-face-impact/blob/1c36e1b13142a09f17e0daa6d9799341ddbf1eb1/docs/governance/MASTER_DEVELOPMENT_PLAN.md) matches the plan on `docs/master-development-plan-v1.2-20261111` at `3ae8769363814e9dc9c8007927c0438ab0f2c811`.

| Gate | Approved objective | Acceptance evidence still needed |
| --- | --- | --- |
| 25 | Camera measurements in the existing dashboard | Actual camera data in the dashboard while preserving its layout |
| 26 | Shot history, sessions and storage | Save, reload and export with shot, capture, model, calibration, calculation and quality provenance |
| 27 | Statistics, distribution and club analysis | Consistent and labelled calculations |
| 28 | Settings, diagnostics, errors and integration tests | Integrated workflow and safe degraded states |
| 29 | Physical ELP/IR testing with several clubs | Documented hardware setup and raw recordings |
| 30 | Independent impact reference | Millimetre error measured against that reference |

## Current software preparation

- The capture preflight checks grayscale quality, frame continuity and metadata. The analysis runner can bind the preflight to capture bytes before analysis and publication. Thresholds are provisional until measured with ELP frames.
- The server-owned replay exercises the dashboard and offline review with accepted and rejected synthetic evidence. On a loopback mock backend, SQLite stores versioned shot records beside the configured profiles file. The saved-session control can reload and export JSON with capture, club, calibration, calculation and quality provenance. Raw frame and marker bytes are represented by digests and metadata. The fixture generates the rasters on demand.
- To try the workflow, open **Saved synthetic sessions** under offline review. **Run in new session** starts a new session with the selected replay case. Use the normal replay button to add heel contact, compact club contact or a missing ball. Repeating a case in a session preserves the original record.
- Load a session to view counts, impact distribution, mean X/Y and population standard deviation in millimetres for each club model. The **Club model** filter scopes the charts and shot diagnostics. Two accepted points on the same club model are required for spread. Export JSON includes the archived records plus the analysis and validation status.
- Keep acquisition under the existing single camera owner. Preserve explicit capture, club and calibration provenance when preparing session persistence and statistics. Gates 29–30 require physical data and remain deferred. Define the independent reference, sampling and error tolerances before those tests.

## Windows lifecycle and archive evidence

The user verified the six-panel dashboard, synthetic replay marker, session history, statistics and diagnostics on a Windows PC. The test exposed stale Socket.IO messaging and a failure in the in-app shutdown flow. The portable renderer now follows the current Socket.IO connection, identifies archive results and delegates desktop shutdown to Electron.

| Gate | Regression evidence in the portable smoke |
| --- | --- |
| 26 | Accepted evidence is restored and exported after normal shutdown. A rejected shot saved before a forced backend exit survives the restart and appears in the export. SQLite commits each evidence record before publication. |
| 27 | The restored report retains one accepted point and one rejected result after the forced exit. The rejected shot has no marker and contributes no point to the saved club statistics. |
| 28 | The renderer connects to its own backend, reports loss of connection while keeping previously loaded evidence visible, and exits via both the power dialog and native close. The runner checks for backend exit and release of port 8080. |

This evidence uses mock capture. A shutdown during an unfinished write can discard the unfinished transaction. Physical capture and its acceptance work remain deferred.
