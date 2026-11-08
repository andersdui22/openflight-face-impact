# Windows Bootstrap — developer verification

Gate 02 provides a **development launcher**, not a packaged Windows release.
The original OpenFlight Flask backend and Electron/React UI are reused.
The backend runs in `--mock` mode: **no radar or ELP camera is connected**.

## Prerequisites

Install Python 3.12, Node.js matching `.node-version`, and npm on Windows.
Open PowerShell in the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
cd ui
npm ci
npm run build
cd ..
$env:OPENFLIGHT_PYTHON = (Resolve-Path .\.venv\Scripts\python.exe).Path
node scripts/windows-bootstrap.mjs
```

The launcher starts `python -m openflight.server --mock --host 127.0.0.1
--web-port 8080`, waits for a successful HTTP response, and starts the
upstream Electron entry point. To select a different port:

```powershell
$env:OPENFLIGHT_WEB_PORT = "8081"
node scripts/windows-bootstrap.mjs
```

`OPENFLIGHT_STARTUP_TIMEOUT_MS` controls the readiness timeout (default
30,000 ms). Do not expose the mock server to the network: the launcher
binds only to `127.0.0.1`.

## Automated verification

```powershell
node --test tests/windows-bootstrap.test.mjs
python tests/windows_backend_smoke.py
```

The second command requires the backend dependencies installed above and
starts the real mock Flask process on a temporary local port. GitHub Actions
also builds the existing React UI on Windows.

## Current limitations

- No Windows installer, packaging, or release.
- No ELP OV9281 acquisition or Face Impact calculation.
- The inherited Python dependencies may require platform-specific fixes;
  CI must verify them before declaring Windows support.
- This is not a physical test or a Golden baseline.
- No changes to ConnectorNext or MLM2PRO.
