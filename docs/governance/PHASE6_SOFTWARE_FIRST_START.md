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
- To try the workflow, open **Saved synthetic sessions** under offline review. **Run in new session** starts a new session with the selected replay case. Use the normal replay button to add the other case. Repeating a case in a session preserves the original record. Refresh the saved-session list to load a session or export its JSON.
- Keep acquisition under the existing single camera owner. Preserve explicit capture, club and calibration provenance when preparing session persistence and statistics. Gates 29–30 require physical data and remain deferred. Define the independent reference, sampling and error tolerances before those tests.
