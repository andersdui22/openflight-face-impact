# Gates 20–28 — camera and Windows readiness

The approved base is draft PR #46 at
`f65762b1ea48bc73bb3d8ef59790b4d5126ba32d`. The scope is software-only camera
and desktop readiness under Project Law V1 and MDP V1.2. Keep the six-panel
dashboard, existing calibration/binding rules, and one camera owner.

## Windows USB preview preparation

The existing Windows USB CLI takes an explicit device index, width, height and
requested FPS. `--windows-usb-reconnect` optionally retries a failed open or read
on that index. It releases the previous handle before reopening and rotates the
capture session. It cannot identify a USB serial number or assume an index
still refers to the same device after re-enumeration. Keep physical acquisition
disabled in the distributed development package. A blocked driver read reports
stale delivery and suppresses preview and triggering. The adapter will not
start a second reader while the first can still own the device.

Optional `--windows-usb-driver-exposure` and `--windows-usb-driver-gain` values
use DirectShow driver units. Status distinguishes requested, driver-accepted
and driver-reported controls from sensor exposure and gain, which remain
unknown. Status also exposes arrival age, delivered dimensions and rolling
host FPS. Mixed raster dimensions and invalid frame formats are rejected per
capture session. These checks do not certify an ELP mode or media subtype.

## Measurement evidence

- Gates 20 and 21 retain controlled synthetic segmentation and labelled planar
  landmarks. Real scenes, natural landmark correspondence and curved faces
  require independent evidence.
- Gates 22–24 retain independent-time preflight, bounded geometry and rejection.
  Host-clock aliases are ineligible. Unique synthetic geometry does not establish
  contact time. Calibrated physical uncertainty and false acceptance remain open.
- Gate 25 exposes the existing preview/status route. Optics profile dimensions
  must match delivered dimensions. Camera mode identity, actual lens, and
  club-model/geometry binding are still required before physical publication.
  The existing offline binding and revision checks remain authoritative.
- Gates 26–27 preserve the SQLite and analysis contract. A separate offline ZIP
  writer prepares lossless post-adapter monochrome raster retention with per-frame
  hashes, capture identity, app SHA and explicit clock provenance. It bounds a
  recording to 512 frames and 64 MiB and uses temporary output before publishing
  the complete ZIP. It has no automatic recording or camera-side storage by
  default. Real-data retention policy, independent mode/lens identifiers and a
  physical review workflow remain open.
- Gate 28 adds bounded recovery of a previously healthy owned desktop backend.
  Smoke kills the process and verifies a new child identity and Socket.IO
  reconnection. It also retains the independent quit-while-down scenario.

The Windows backend uses the dependency versions from the successful PR #46
package and checks their compatibility before freezing. npm still uses its
existing lockfile. This controls Python dependency versions without promising
bit-for-bit equality across runner images or interpreter patches. Actual ELP
hardware tests, clean-PC acceptance, gate closure and release remain separate.
