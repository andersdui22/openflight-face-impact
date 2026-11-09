# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 21

Title: Synthetic Face Impact request/response over existing Flask-SocketIO channel
State: ACTIVE — explicitly approved by user (2026-11-09).
Project Law: V1 unchanged.
Working branch: `gate21/synthetic-socket-bridge`.
Base: Gate 20 `ca4e5ebe6ba872ed30383f20bc3fe2c7ef3c6fe2`, all six workflows passed on same SHA; draft PR #20 unmerged.

## Authorized scope
Reuse the existing Python Flask-SocketIO server and React socket.io-client connection. Add a narrowly scoped, explicitly synthetic request/response event that runs Gate 18 `calculate_synthetic_face_impact` on bounded, server-defined deterministic geometry cases. Return versioned structured results and finite face polygon in millimetres; reject unknown case identifiers without invented measurements. React must request and display only server-returned results, with honest disconnected/error states, and no second socket connection. Test both backend and UI behavior.

## Acceptance
Automated tests for known success/rejection, unknown case, schema, no hardware access, UI error behavior, and all six same-SHA CI workflows. Preserve original OpenFlight shell and existing socket behavior.

## Exclusions
No ELP camera acquisition, live measurements, physical testing, radar, ConnectorNext, unrelated server changes, merge, release or Golden baseline.
