# Gate 25 Windows desktop runtime

Anders approved Gate 25 on 2026-11-09. The baseline is Gate 24
`e022c2f2348e80d29e4ff3e627669c3dcfa8c645`, verified on draft PR #24.

## Developer startup on Windows

From the repository root in PowerShell with Python 3.12 and Node matching
`.node-version`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[camera]"
Set-Location ui
npm ci
npm run build
Set-Location ..
$env:OPENFLIGHT_PYTHON = (Resolve-Path .\.venv\Scripts\python.exe).Path
Remove-Item Env:OPENFLIGHT_USB_CAMERA_INDEX -ErrorAction SilentlyContinue
node scripts/windows-bootstrap.mjs
```

The existing launcher starts Python on loopback in mock mode. It opens the
built React application in Electron after the server responds. In the Debug
tab, select the synthetic Face Impact case and request its result.

## Evidence and acceptance

Gate 04's Windows workflow verified Flask's HTTP response and the presence
of an Electron process. Gate 24 covered the React and Python connection
through the separate Vite and Chromium test harness.

Gate 25 extends the existing Windows bootstrap smoke. A temporary change to
the test checkout's npm script enables inspection on a dedicated loopback
port with an isolated Electron profile. The smoke checks the actual Electron
page at the Python server URL, connected status, one synthetic marker and its
expected coordinate. It closes the window, waits for the launcher to exit,
checks that the Python port is no longer listening, and repeats the test on
the same port. The test restores the npm script on exit. The USB status must
report disabled. No camera is opened.

Windows bootstrap CI must pass on the final draft PR head alongside the six
regular PR workflows. Draft PR #25 records the final SHA and CI runs.

## Stop conditions

Stop for a physical camera, driver changes, new dependencies, packaging or
work outside the approved Gate. Hardware timing, calibration, capture
stability and impact accuracy require separately authorized evidence.
