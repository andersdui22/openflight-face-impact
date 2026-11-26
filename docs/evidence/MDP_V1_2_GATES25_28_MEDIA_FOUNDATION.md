# Media Foundation camera diagnostics

Baseline: draft PR #51 at `b8f54dddbc75d9624a1a4fccc4dcfbe03c801df5`.
The [approved decision](../governance/DECISION_REGISTER.md) adds a native x64
DLL built with CMake, MSVC and the Windows SDK. Static MSVC runtime linking
keeps the app folder portable. Windows Media Foundation must be available
in the host OS, including the Media Feature Pack where needed on Windows N.

## Terminal-free ELP workflow

1. Extract the complete portable folder and double-click **OpenFlight Face Impact.exe**.
2. Attach the ELP OV9281. In the Face Impact dashboard open **Camera setup and diagnostics**.
3. Click **Scan Windows cameras** and select the exact listed device. If cameras
   have the same name, compare their identifiers by unplugging one and rescanning.
   A changed symbolic link after a port change requires reselection.
4. Check **Enable physical diagnostics**, then **Load advertised modes**.
   The query briefly opens the selected source to enumerate modes, then closes
   it. Select a supported native mode. Use 120 FPS only if the device advertises it.
5. Select driver default, auto, or manual exposure. Enter integer exposure/gain
   values in driver units if supported. Start the physical camera. Compare the
   requested and negotiated format, delivered raster, reported controls,
   observed FPS, frame age and sample timing. Driver support may be unavailable.
6. Look for **Physical camera · diagnostic image** in the preview. To change
   settings or reconnect, apply them with **Start or reconnect physical camera**.
   Stop and rescan if the link changes. The backend never substitutes a device.
7. Choose frame counts and a purpose, including checkerboard, club landmarks,
   setup or golf diagnostic. Prepare the viewed target and select
   **Record and export diagnostic** for a manual host trigger. Retain the ZIP
   and note the physical setup and target independently.
8. Stop the camera, then use either app or window close.

## Export and provenance

The outer ZIP has `diagnostic.json`, lossless luminance `capture.zip` and
original native sample payloads under `native/`. Open MJPG samples as normal
JPEGs. YUY2 and NV12 samples are stored as packed native bytes, with format and
dimensions in the manifest. For a directly viewable lossless grayscale copy,
extract an inner `.gray8` raster and prepend the PGM header
`P5\n<width> <height>\n255\n` without editing the pixel bytes. Keep the
original packages and hashes. The manifest records sample time, sample duration and Source Reader callback time
in 100 ns units, flags, discontinuity, host timestamps, device identity,
mode, controls, capture window and app SHA. Driver sequence is unknown.
A metadata receipt is stored in the existing SQLite database, separately
from admitted replay and accepted impact history.

The native DLL activates the exact unique symbolic-link entry and verifies the
requested media type again on open. Sources that only offer unsupported
formats or padded layouts that cannot be validated fail closed. Current
native modes are YUY2, NV12 and MJPG. Readback via IAM interfaces is
driver-dependent; unsupported requests remain unverified. JPEG preview
uses already-buffered grayscale frames at a separate periodic rate. The
native read waits at most 1.5 seconds for an asynchronous sample callback.
A stuck native open, teardown or driver call remains a hardware test case.
Buffer admission accounts for 4 bytes per pixel of native data plus the
analysis plane, with up to 16 pre and 16 post frames and a 64 MiB working
buffer budget. Export serialization temporarily holds additional copies.

## Evidence and pending acceptance

Windows CI loads the packaged native DLL and invokes Media Foundation device
enumeration. Controlled Python and browser tests exercise the integration
without physical input. The physical setup screenshot shows a controlled
inventory, with no camera opened. No ELP was available for Windows-runner
verification. Preview, driver negotiation/controls, CPU/load, sustained FPS,
port changes, two-camera substitution, unplug/reconnect, and real export
must be checked on the user's hardware.

Sample timestamps remain stream provenance. The analysis frames retain
the host-alias rejection marker, even when a native sample timestamp exists.
Gate 22 still needs a verified exposure clock and trigger relation. At
120 FPS a nominal sample interval is 8.33 ms; there is no contact or
subframe inference in this diagnostic feature. Physical checkerboard
quality, camera/lens revision and club/landmark evidence remain pending.
Gates 20–28 stay open.

## Operator observations from the PR #52 portable build

The project owner reported the following from the physical ELP OV9281 on
Windows against the PR #52 baseline
[`9b33dda`](https://github.com/andersdui22/openflight-face-impact/commit/9b33ddab71698625e058c10d8a2cc64a2c0a908a):

- Windows enumerated **Global Shutter Camera**. The native provider listed
  the advertised modes, opened the chosen device and reported a matching
  capture handle. The physical preview reacted to changing light and to
  the operator covering and uncovering the camera.
- Preview started at **160 × 120, 640 FPS, NV12** and at
  **640 × 480, 30 FPS, YUY2**. These are selected mode labels. Sustained
  delivery rates were not measured.
- **640 × 480 at 210.00021000021 FPS** and **1280 × 800 at
  120.00048000192001 FPS** returned “Select a valid advertised camera mode”.
  The failed attempts do not establish whether the driver can stream those
  modes.

The baseline Python API rejected native mode integers above 65,535 before
opening the camera. Controlled regression inputs reproduce the reported
decimals using numerators of 10,000,000 and denominators of 47,619 and
83,333, respectively. A third case uses 23,809 for 420.0092402032845 FPS.
The controlled ratios reproduce the labels without asserting the operator's
unrecorded native metadata. The corrected boundary accepts positive
unsigned 32-bit fields. The selection key includes the exact ratio,
dimensions and pixel format. Native negotiation still requires an exact
match. Test evidence for the fix must be checked on its own commit.

This is partial physical evidence for enumeration, identity binding and
preview. Gates 20–28 remain open. Retest the fractional modes and record
one diagnostic ZIP per mode. Note the selected ratio, format, delivered
dimensions and observed FPS. Verify start after stopping, then unplug and
reconnect, rescan if the link changes and repeat with the same physical
device. Sustained delivery, physical export, timing, calibration and
measurement accuracy remain open physical acceptance items.

## Operator observations from the PR #53 portable build

The owner reported physical ELP OV9281 enumeration, correct device identity,
live preview responding to motion, and successful diagnostic ZIP export
from the PR #53 Windows build at
[`88b40ae`](https://github.com/andersdui22/openflight-face-impact/commit/88b40aec68b357f164b99d60c3214d842aac6be5).

| Selected resolution and nominal rate | Observed delivery FPS reported by the owner |
| --- | ---: |
| 1280 × 800 at 120 FPS | 120.91 |
| 640 × 480 at 210 FPS | 209.19 |
| 320 × 240 at 420 FPS | 418.72 |

The owner reported that 13 pre + 13 post frames worked, 14 + 14 failed, and
that exported data appeared to group frames around 16 ms. The original ZIPs
were absent from this workspace and were not independently inspected. The
reported rates represent observed delivery, not sensor measurement. No
independent sample timing, sustained throughput, calibration or impact
accuracy has been established.

### Reproduced recording limit and replacement

At 640 × 480 the old start route budgeted five bytes per pixel and
`2 × pre + post + 2` slots. That is 62,976,000 bytes for 13 + 13,
and 67,584,000 bytes for 14 + 14, above the 67,108,864-byte limit.
An independent 16-frame limit applied to each side. The native readout
scratch buffer was per frame. The offline raster ZIP already allowed up to
512 frames, subject to its own byte ceiling. Mode startup now validates
format and raster independently. Record validates the total window against
the 64 MiB payload budget and the existing 512-frame format limit. NV12
uses 2.5 bytes per pixel including the analysis raster, YUY2 uses 3, and
MJPG reserves its bounded maximum of 5. At 640 × 480 NV12 the total is
87 frames, and at 1280 × 800 NV12 it is 26. At 1280 × 800 MJPG the
conservative limit is 13 total. Milliseconds convert to whole frames
rounded up using the exact native ratio. They are nominal requested
durations, with actual intervals recorded separately.

While exporting, one completed window can coexist with the next rolling
history, for at most two 64 MiB frame payload windows, plus per-frame
scratch, metadata, one cached preview, and normal application overhead.
The outer ZIP is spooled to disk above 1 MiB and streamed from the backend.
The browser download still consumes the bounded archive as a Blob. One
manual capture/export request is prepared at a time. Ring history eviction
is expected and counted separately from unavailable device-drop counts.

### Timing instrumentation and interpretation

The earlier `source_reader_time_100ns` records the Media Foundation
`OnReadSample` media timestamp, not the local execution time of the callback.
The new export includes actual QPC callback and readout observations and
their frequency, the sample timestamp and duration, Python monotonic
arrival and raster preparation completion. Interval and segment statistics
are computed within each clock domain, preserving repeated, negative and
long intervals as observed. Payload hashes identify adjacent equal bytes
in the ZIP. Equal bytes or timestamps alone cannot establish duplicate
exposures. The diagnostic UI reports live statistics, buffer occupancy and
evictions, received/processed/last exported counts, and JPEG encode count
and wall time. A dropped-frame total and the sensor-exposure clock remain
unknown.

The Source Reader issues one async request at a time. It waits for its
callback, copies the sample and prepares the raster before issuing another
request. Thus USB/driver scheduling, callback dispatch, same-thread copy
and decode, or host scheduling could influence the apparent cadence. A
roughly 16 ms spacing alone does not identify USB batching or Windows timer
resolution. Preview uses the existing ring on independent HTTP workers.
Diagnostic preview now bounds JPEG encoding to one job at a time with a
100 ms cache interval. It never submits a capture request. There is no
timing repair, timer-resolution change, or second acquisition queue.

The provider queries `IAMCameraControl::GetRange` and
`IAMVideoProcAmp::GetRange` on the open source. Controls use native driver
units. Range, step, default, auto/manual capability, acceptance and readback
are reported only when the driver supplies them. Start/reconnect applies
the operator's selected controls to the same exact device. Support on the
physical ELP and its driver requires retest.

For the next test, export an otherwise unchanged mode with preview idle
and again with preview visible. Repeat at 120, 210 and 420 FPS. Preserve
the original ZIPs. Compare adjacent sample, QPC callback and host intervals
together with native readout, Python preparation and preview costs.
Gates 20–28 remain open.
