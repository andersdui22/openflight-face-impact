"""Gate 16 status contract: no physical claims or implicit mode matching."""

import numpy as np

from openflight.camera.calibration_profile import CameraCalibrationProfile
from openflight.camera.calibration_status import calibration_status
from openflight.camera.checkerboard_calibration import CheckerboardCalibration


def make_profile():
    cal = CheckerboardCalibration(
        (640, 400),
        np.array([[530., 0., 315.], [0., 525., 198.], [0., 0., 1.]]),
        np.array([-0.24, 0.08, 0.002, -0.003, 0.]),
        0.22,
        (0.3, 0.25, 0.28),
    )
    return CameraCalibrationProfile(cal, "synthetic:640x400:full-frame")


def test_missing_profile_is_not_calibrated():
    status = calibration_status(None, camera_mode_id=None, image_size=None)
    assert status["state"] == "not_calibrated"
    assert status["profile_loaded"] is False
    assert status["physical_validation"] is False


def test_unknown_mode_fails_closed_even_when_profile_loaded():
    status = calibration_status(make_profile(), camera_mode_id=None, image_size=(640, 400))
    assert status["state"] == "mode_unknown"
    assert status["mode_compatible"] is False
    assert status["physical_validation"] is False


def test_same_resolution_different_mode_is_incompatible():
    status = calibration_status(
        make_profile(), camera_mode_id="different-crop:640x400", image_size=(640, 400)
    )
    assert status["state"] == "mode_incompatible"
    assert status["fit_rms_px"] is None


def test_compatible_offline_profile_is_never_physical_validation():
    status = calibration_status(
        make_profile(), camera_mode_id="synthetic:640x400:full-frame", image_size=(640, 400)
    )
    assert status["state"] == "offline_profile_compatible"
    assert status["profile_loaded"] is True
    assert status["mode_compatible"] is True
    assert status["physical_validation"] is False
    assert status["evidence_kind"] == "synthetic_offline"
    assert status["fit_rms_px"] == 0.22
    assert status["validation_rms_px"] == [0.3, 0.25, 0.28]
