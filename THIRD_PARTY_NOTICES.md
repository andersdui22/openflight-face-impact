# Third-party notices and asset admission

Status: foundation inventory, **not** a complete release notice bundle.

| Component or asset | Current evidence | Distribution decision |
| --- | --- | --- |
| OpenFlight source | AGPL-3.0-or-later as declared in `pyproject.toml`; upstream `LICENSE` retained. | Preserve history, notices and applicable corresponding source. |
| Python and npm dependencies | Declared in the inherited manifests and lockfiles. | Audit exact package licenses and bundled binaries before packaging. |
| Electron/Chromium and FFmpeg | Existing Electron shell; replay may use FFmpeg. | Verify exact redistributed versions and notices before Windows release. |
| Titleist 690CB 7-iron mesh in PR #245/#250 | GrabCAD source; contributor says STL and normalized NPZ are local research only and must not be redistributed. | Excluded. No mesh binary in this gate. |
| Retired Callaway driver candidate | Contributor marked unsuitable as canonical geometry. | Excluded. |
| Raw photos, club reference research and physical captures | Some contributor inputs are not public; provenance and reuse rights incomplete. | Excluded pending evidence and explicit admission. |

This register is deliberately incomplete for a future release. A dependency,
model or artifact must not be treated as cleared because code references it.
