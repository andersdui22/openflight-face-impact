# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 24

Title: Real React/Socket.IO to Python localhost integration
State: ACTIVE — explicitly approved by user (2026-11-09).
Project Law: V1 unchanged.
Working branch: `gate24/react-python-localhost-e2e`.
Base: Gate 23 `8555d933e781458be5dfae205d1545a9d0369750`, all six same-SHA workflows successful; draft PR #23 unmerged.

## Authorized scope
Reuse the existing Playwright Chromium, Vite React frontend and Python Flask-SocketIO backend harness in `ui/playwright.config.ts` (loopback only, backend mock mode). Add end-to-end browser tests that navigate to the existing debug Face Impact UI, exercise the real React socketService to Python Socket.IO acknowledgement for accepted/rejected synthetic results, observe offline error and recovery on reconnection. No new production socket, UI, server or camera code unless a test demonstrates a minimal need.

## Acceptance
Actual browser and actual separate Python backend, no mocked browser transport, finite synthetic coordinates only for valid contacts, rejection without marker, offline error and recovery, same-SHA green CI. State that mock mode is existing upstream simulated shot backend, not hardware validation.

## Exclusions
No live camera, physical tests, radar hardware, MLM2PRO/ConnectorNext, merges, releases or Golden baseline.
