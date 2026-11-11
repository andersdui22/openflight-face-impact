"""Gate 19: offline calibration revision-aware status, without camera access.

A persisted expected revision is mandatory for use in a downstream
measurement workflow. Passing this check does not prove physical calibration.
"""

from __future__ import annotations

from .calibration_profile import CameraCalibrationProfile
from .calibration_revision import require_calibration_revision
from .calibration_status import calibration_status


def revision_bound_calibration_status(
    profile: CameraCalibrationProfile | None,
    *,
    expected_revision: str | None,
    camera_mode_id: str | None,
    image_size: tuple[int, int] | None,
) -> dict:
    """Extend existing fail-closed mode status with revision compatibility."""
    result = calibration_status(
        profile, camera_mode_id=camera_mode_id, image_size=image_size
    )
    result["revision_compatible"] = False
    if profile is None:
        return result
    try:
        require_calibration_revision(profile, expected_revision=expected_revision)
    except ValueError:
        result["state"] = "revision_invalid"
        result["mode_compatible"] = False
        result["fit_rms_px"] = None
        result["validation_rms_px"] = None
        return result
    result["revision_compatible"] = True
    return result
