# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 22

Title: Automated synthetic Socket.IO integration and reconnection verification
State: ACTIVE — explicitly approved by user (2026-11-09).
Project Law: V1 unchanged.
Working branch: `gate22/socket-integration-tests`.
Base: Gate 21 `beaa98cb2b634945b696f6bac6f25bfb6c5d01dc`, seven successful same-SHA workflows; draft PR #21 unmerged.

## Authorized scope
Test the existing Flask-SocketIO server request handler using Flask-SocketIO's in-process test client, including successful synthetic calculations, rejected contacts, malformed case IDs and disconnect/reconnect. Test the existing React socketService client with a mocked Socket.IO transport for acknowledgement, invalid response, timeout/disconnect and reconnection, without introducing a second connection. Preserve existing behavior; any production change must be minimal and evidenced by tests.

## Acceptance
Tests explicitly distinguish real in-process server transport from mocked browser transport, no hardware access, CI green on the exact gate SHA, and no fabricated contact results.

## Exclusions
No live camera, physical tests, external network service, ConnectorNext, MLM2PRO, merges, releases or Golden baseline.
