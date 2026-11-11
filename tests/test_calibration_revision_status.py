"""Gate 19: revision binding must not turn offline optics into physical evidence."""

from dataclasses import replace

import numpy as np

from openflight.camera.calibration_profile import CameraCalibrationProfile
from openflight.camera.calibration_revision import calibration_revision
from openflight.camera.calibration_revision_status import (
    revision_bound_calibration_status,
)
from openflight.camera.checkerboard_calibration import CheckerboardCalibration


def profile():
    return CameraCalibrationProfile(
        CheckerboardCalibration(
            (640, 400),
            np.array([[530., 0., 315.], [0., 525., 198.], [0., 0., 1.]]),
            np.array([-0.24, 0.08, 0.002, -0.003, 0.]),
            0.22, (0.3, 0.25, 0.28),
        ),
        "synthetic:640x400:full-frame",
    )


def status(p, revision, mode="synthetic:640x400:full-frame", size=(640, 400)):
    return revision_bound_calibration_status(
        p, expected_revision=revision, camera_mode_id=mode, image_size=size
    )


def test_matching_revision_and_mode_remain_offline_only():
    p = profile()
    result = status(p, calibration_revision(p))
    assert result["state"] == "offline_profile_compatible"
    assert result["revision_compatible"] is True
    assert result["physical_validation"] is False


def test_missing_expected_revision_fails_closed():
    result = status(profile(), None)
    assert result["state"] == "revision_invalid"
    assert result["revision_compatible"] is False
    assert result["mode_compatible"] is False


def test_stale_revision_masks_previous_compatible_status():
    p = profile()
    changed = replace(p, camera_mode_id="different-crop")
    result = status(changed, calibration_revision(p), mode="different-crop")
    assert result["state"] == "revision_invalid"
    assert result["mode_compatible"] is False
    assert result["fit_rms_px"] is None


def test_correct_revision_does_not_override_mode_unknown():
    p = profile()
    result = status(p, calibration_revision(p), mode=None)
    assert result["state"] == "mode_unknown"
    assert result["revision_compatible"] is True
    assert result["physical_validation"] is False


def test_correct_revision_does_not_override_crop_mismatch():
    p = profile()
    result = status(p, calibration_revision(p), mode="different-crop")
    assert result["state"] == "mode_incompatible"
    assert result["revision_compatible"] is True
    assert result["mode_compatible"] is False


def test_missing_profile_stays_not_calibrated():
    result = status(None, None)
    assert result["state"] == "not_calibrated"
    assert result["revision_compatible"] is False
