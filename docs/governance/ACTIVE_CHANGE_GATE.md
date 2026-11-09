# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 23

Title: Real localhost Socket.IO integration between separate Python processes
State: ACTIVE — explicitly approved by user (2026-11-09).
Project Law: V1 unchanged.
Working branch: `gate23/localhost-socket-e2e`.
Base: Gate 22 `d2435307ac93f6025ac1098e6b5df685226cdf02`, all six same-SHA workflows successful; draft PR #22 unmerged.

## Authorized scope
Run the existing Flask-SocketIO application in an isolated child process bound only to 127.0.0.1 on a dynamically selected port, without invoking the hardware-oriented OpenFlight main() startup. Use a separate python-socketio Client from the test runner to verify real TCP localhost request acknowledgments for synthetic impact, rejected/invalid identifiers, disconnect and fresh reconnection. Clean up processes deterministically and fail on timeouts. No second production socket or new product UI.

## Acceptance
Cross-process localhost integration tests with bounded startup and shutdown, no camera/hardware, actual Socket.IO network transport and same-SHA green CI. Clearly distinguish this from React/Electron end-to-end runtime or physical accuracy.

## Exclusions
No live camera, physical tests, radar/MLM2PRO/ConnectorNext, production startup changes, merges, releases or Golden baseline.
