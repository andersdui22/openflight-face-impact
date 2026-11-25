"""Admission and analysis of recorded rasters using the existing offline runner."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .calibration_club_binding import CalibrationClubBinding, require_calibration_club_binding
from .calibration_profile import CameraCalibrationProfile
from .club_face_model import ClubFaceModel
from .offline_capture_preflight import preflight_offline_capture
from .offline_capture_recording import load_offline_capture
from .trigger_timing_quality import assess_trigger_timing


@dataclass(frozen=True)
class RecordedCaptureAdmission:
    """Independent, trusted capture receipt retained outside the recording ZIP."""

    fingerprint: str
    app_sha: str
    source: str
    camera_identity: str
    camera_mode_id: str
    binding: CalibrationClubBinding


class RecordedReplayRejected(ValueError):
    """Stage-labelled failure suitable for offline diagnostics."""

    def __init__(self, stage: str, detail: str):
        self.stage = stage
        super().__init__(f"{stage}: {detail}")


def prepare_recorded_replay(
    path: Path,
    *,
    admission: RecordedCaptureAdmission,
    camera_identity: str,
    profile: CameraCalibrationProfile,
    club: ClubFaceModel,
    max_sensor_gap_ns: int,
    max_host_gap_ns: int,
):
    """Reconcile bytes with independent identity/revisions before analysis."""
    try:
        recording = load_offline_capture(path)
    except ValueError as error:
        raise RecordedReplayRejected("integrity", str(error)) from error

    if ((recording.fingerprint, recording.app_sha, recording.source)
            != (admission.fingerprint, admission.app_sha, admission.source)):
        raise RecordedReplayRejected("provenance", "recording differs from independently admitted evidence")
    # An integer capture index, including one represented as a string, has no
    # stable identity. Callers supply a trusted namespaced identifier.
    scheme = "fixture" if recording.source == "synthetic_fixture" else "windows-device-interface"
    identity_prefix = scheme + ":"
    if (not isinstance(camera_identity, str) or not camera_identity.startswith(identity_prefix)
            or not camera_identity.removeprefix(identity_prefix).strip()
            or camera_identity != admission.camera_identity):
        raise RecordedReplayRejected("camera_identity", "camera identity missing or incompatible")

    try:
        if not isinstance(profile, CameraCalibrationProfile):
            raise ValueError("validated optics profile required")
        h, w = recording.capture.frames[0].image.shape
        profile.require_mode(admission.camera_mode_id, (w, h))
        require_calibration_club_binding(admission.binding, profile=profile, club_model=club)
    except ValueError as error:
        raise RecordedReplayRejected("calibration_binding", str(error)) from error

    timing = assess_trigger_timing(recording.capture)
    if not timing.valid:
        raise RecordedReplayRejected("timing_or_frame_quality", timing.reason)

    try:
        preflight = preflight_offline_capture(
            recording.capture, max_sensor_gap_ns=max_sensor_gap_ns, max_host_gap_ns=max_host_gap_ns,
        )
    except ValueError as error:
        raise RecordedReplayRejected("timing_or_frame_quality", str(error)) from error
    if recording.source != "synthetic_fixture":
        raise RecordedReplayRejected("acquisition", "physical publication is outside offline replay")
    return recording, preflight
