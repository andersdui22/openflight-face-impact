# Gates 20–28 — recorded offline replay

Approved base: draft PR #47 at
`1781e74327f077e855da277dac23e25ea52ec5ca`. Software-only recording and replay
reuse the capture, profile, binding, offline preflight, landmark/pose/impact,
and SQLite evidence chain. A fixture recording can be created and replayed
locally with:

```text
uv run --extra camera python -m openflight.camera.offline_recording_cli --record <directory> --app-sha <known producer commit>
uv run --extra camera python -m openflight.camera.offline_recording_cli --replay <zip> --app-sha <known producer commit> --archive <optional local session SQLite path>
```

The Windows Python EXE supports the same arguments after `--offline-recording`.
The producer SHA is supplied separately. The trusted fixture case provides an
independent receipt for bytes, clocks, camera fixture identity, mode, optics
and club revisions. The reader accepts existing v1 packages, checks exact
members, raster hashes and the full capture fingerprint, and reads bounded
uncompressed members without filesystem extraction. A ZIP is self-consistent
evidence and is not a trusted receipt by itself.

The existing marker runner still detects and associates fiducials against the
controlled per-frame reference. It receives identical stored raster bytes and
runs the existing pose, geometry and result quality contracts. Diagnostics
identify integrity, independent provenance, camera identity, binding, timing
or frame quality, and marker or geometry failure. An unadmitted capture cannot
publish coordinates. Accepted and coordinate-free rejected synthetic results
can use the SQLite history contract. Invalid inputs abort without storing a
shot. There is no upload route or change to the six-panel dashboard.

## Windows identity and clocks

`windows_usb.py` uses OpenCV DirectShow `VideoCapture(index)`. The current
interface exposes an enumeration index and negotiated properties. It does not
associate a device-interface path or serial with the handle. Reopening an index
cannot establish device continuity after USB re-enumeration. The reader has only
host arrival timestamps taken after `read()`; exposure/gain property readback
does not supply a sensor clock. Legacy host-alias metadata can be reconstructed
to check a ZIP fingerprint and is still rejected by independent-time preflight.
A future physical adapter needs an independently admitted identity and timing
source tied to the frames it delivers. No access to physical hardware occurred.

## Open acceptance boundaries

- Gates 20–24 retain controlled landmark correspondence and planar geometry.
  Real landmarks, camera-to-club pose, curved geometry, contact timing,
  physical uncertainty and measured rejection rates remain open.
- Gates 25–28 gain deterministic offline replay, independent binding checks
  and local archive diagnostics. Native Windows device identity, sensor timing,
  operator import UI, real raw-data retention and physical data integration
  remain open. UI rendering, archive export and packaging regressions run as
  before. The packaged Windows workflow additionally records and replays an
  identical fixture and checks synthetic SQLite evidence.
- No gate closure or physical acceptance is inferred.
