# Gate 26 ELP OV9281 operator test

Anders approved the physical operator procedure on 2026-11-09. Start from
Gate 25 `4bcb6d311949aa8c3763c957538b419b61f67200`. Gate 25's Windows
CI verified Electron and Python together with USB acquisition disabled.

## Prepare the Windows PC

Use PowerShell, Git, Python 3.12 and Node.js 24. Clone the test branch into a
new folder and note the commit. Verify the SHA against draft PR #26 before
starting. Stop if any setup command fails.

```powershell
git clone --single-branch --branch gate26/elp-operator-test https://github.com/andersdui22/openflight-face-impact.git OpenFlight-Gate26
Set-Location OpenFlight-Gate26
git rev-parse HEAD
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[camera]"
Set-Location ui
npm.cmd ci
npm.cmd run build
Set-Location ..
```

Close apps that might hold the camera, including OBS, AMCap and Windows
Camera. Connect one ELP OV9281 USB camera. Stop any other OpenFlight instance
using port 8080. Start with device index 0. This is a DirectShow index and may
select a different camera. Confirm the actual source by briefly covering the
ELP lens and observing that the preview changes. Stop the launcher before
trying another index. Record the camera model and, if available, the USB
hardware ID from Device Manager. There are no golf shots in this procedure.

## Start and observe

In the first PowerShell window, from the cloned folder:

```powershell
$logs = Join-Path $env:TEMP 'OpenFlight-Gate26'
New-Item -ItemType Directory -Force $logs | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$env:OPENFLIGHT_PYTHON = (Resolve-Path .\.venv\Scripts\python.exe).Path
$env:OPENFLIGHT_WEB_PORT = '8080'
$env:OPENFLIGHT_USB_CAMERA_INDEX = '0'
node.exe scripts/windows-bootstrap.mjs 2>&1 | Tee-Object -FilePath (Join-Path $logs "launcher-$stamp.txt")
```

In OpenFlight, select **Camera** and confirm that the preview is live and
comes from the ELP. Stop if it is the wrong source, black or frozen. After
confirming the source, open a second PowerShell window in the same cloned
folder. Set `--index` to the index used in the first window.

```powershell
$logs = Join-Path $env:TEMP 'OpenFlight-Gate26'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
.\.venv\Scripts\python.exe scripts/windows-usb-observe.py --seconds 60 --index 0 --out (Join-Path $logs "usb-60s-$stamp.jsonl")
```

Keep the Camera tab open and note any visual freeze. The sampler reads the
existing USB status endpoint about every two seconds. It stops on an error,
non-running capture or a counter that fails to advance. Keep the partial log
if it stops. The launcher requests 640 × 400 at 120 FPS. The driver may
negotiate another mode. Keep the requested mode, negotiated mode, reported
FPS and observed host-arrival FPS separate.

Close Electron and wait for the launcher to exit. Start it once more using
the same commands, index and port. Reconfirm the preview and repeat the
observer command with `--seconds 10`. Then close Electron.

## Evidence to return

Return both JSONL files, any launcher error log and a short note stating
which index selected the ELP, whether preview remained live, and whether it
returned after restart. The log folder opens with:

```powershell
explorer.exe (Join-Path $env:TEMP 'OpenFlight-Gate26')
```

The sampler records the Git commit, Windows platform, OpenCV version,
operator-entered index, status snapshots and the interval rate from
`frames_received` divided by elapsed time. The status endpoint also reports
a rolling host-arrival rate. Neither rate measures the sensor exposure clock.
Polling can detect a stalled interval, but cannot characterize every dropped
frame. Exposure, gain and sensor timing remain unknown unless measured
separately. Keep images and raw user logs local unless the user chooses to
share them.

## Acceptance and stops

Record correct camera and live preview, a complete 60-second observation
with increasing frame counts, and successful restart with a complete
10-second observation. Report the observed mode and rates even if they
differ from the requested 120 FPS. If the camera, preview, stream or restart
fails, preserve the logs and stop for diagnosis. Physical result review and
same-SHA CI are required before closeout. No driver modifications, calibration,
Face Impact measurement, Golden nomination, merge, installer or release.
