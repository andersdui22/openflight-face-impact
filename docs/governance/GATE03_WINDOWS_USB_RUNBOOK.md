# Gate 03 — Windows USB camera preview developer runbook

This is an **experimental developer path**, not a released Windows installer or a validated Face Impact measurement system. Only run a physical ELP camera test after separate explicit authorization under Project Law V1.

## Prerequisites

- Windows, Python 3.12, Node.js/npm and a locally cloned copy of this fork on the Gate 03 branch.
- The USB camera is connected, not held open by OBS/AMCap or another program.
- Camera support is an **optional** OpenFlight dependency, not part of the base installation.

## Developer installation (no camera test implied)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[camera]"
cd ui
npm ci
npm run build
cd ..
```

## Opt-in preview command — **not yet physically validated**

```powershell
.\.venv\Scripts\python.exe -m openflight.server --mock --host 127.0.0.1 --web-port 8080 --windows-usb-camera 0 --windows-usb-width 640 --windows-usb-height 400 --windows-usb-fps 120
```

The optional camera flag is an OpenCV DirectShow device **index**, not a guaranteed device identity. Index 0 can select another attached camera. Only one USB capture reader is created. The existing `GET /api/camera/preview.jpg` endpoint uses its latest buffered grayscale image and returns 404 when no camera runtime exists, 503 if no frame is available, or JPEG when available. The original Pi camera path remains separate and cannot be enabled simultaneously.

The reported FPS is a driver-reported property, **not measured delivery FPS**. Timestamps for USB frames are host-arrival timestamps copied into a legacy `sensor_timestamp_ns` field for buffer compatibility; they are **not** actual sensor exposure timestamps. Exposure and gain are unknown. USB video formats, sustained FPS, trigger latency, reconnect after device unplug, UI compatibility, and impact measurement are not physically verified.

## Current boundaries

- USB capture and JPEG preview are available only through an explicit server flag; the Windows bootstrap launcher still defaults to its original mock backend startup.
- The existing camera UI may rely on Pi-specific status, replay and exposure endpoints. Those features have **not** been claimed as compatible with USB.
- Camera enumeration by stable device name and automatic reconnect are not implemented. Restarting capture after a stop is covered by hardware-free tests.
- Physical testing, release, merge, Golden, and Face Impact solver development remain outside Gate 03.
