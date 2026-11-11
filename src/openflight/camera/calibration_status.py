"""Fail-closed camera calibration status for API/UI consumers.

Status is metadata only. It never starts a camera or changes frame processing.
"""

from __future__ import annotations

from .calibration_profile import CameraCalibrationProfile


def calibration_status(
    profile: CameraCalibrationProfile | None,
    *,
    camera_mode_id: str | None,
    image_size: tuple[int, int] | None,
) -> dict:
    """Report compatibility without asserting physical calibration or accuracy.

    Mode identity must be externally verified; dimensions alone are insufficient.
    """
    result = {
        "state": "not_calibrated",
        "profile_loaded": profile is not None,
        "mode_compatible": False,
        "physical_validation": False,
        "evidence_kind": None,
        "fit_rms_px": None,
        "validation_rms_px": None,
    }
    if profile is None:
        return result
    result["evidence_kind"] = profile.evidence_kind
    if camera_mode_id is None or image_size is None:
        result["state"] = "mode_unknown"
        return result
    try:
        profile.require_mode(camera_mode_id, image_size)
    except ValueError:
        result["state"] = "mode_incompatible"
        return result
    result["state"] = "offline_profile_compatible"
    result["mode_compatible"] = True
    result["fit_rms_px"] = profile.calibration.fit_rms_px
    result["validation_rms_px"] = list(profile.calibration.validation_rms_px)
    return result
