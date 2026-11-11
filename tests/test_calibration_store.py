"""Hardware-free persistence and invalid-file regression checks for Gate 16."""

import numpy as np

from openflight.camera.calibration_profile import CameraCalibrationProfile
from openflight.camera.calibration_store import (
    load_calibration_profile,
    load_calibration_status,
    save_calibration_profile,
)
from openflight.camera.checkerboard_calibration import CheckerboardCalibration


def profile():
    optics = CheckerboardCalibration(
        (640, 400),
        np.array([[530., 0., 315.], [0., 525., 198.], [0., 0., 1.]]),
        np.array([-0.24, 0.08, 0.002, -0.003, 0.]),
        0.22,
        (0.3, 0.25, 0.28),
    )
    return CameraCalibrationProfile(optics, "synthetic:640x400:full-frame")


def test_save_load_roundtrip(tmp_path):
    path = tmp_path / "optics.json"
    save_calibration_profile(path, profile())
    assert load_calibration_profile(path).to_json() == profile().to_json()


def test_unreadable_profile_fails_closed(tmp_path):
    status = load_calibration_status(tmp_path / "missing.json")
    assert status["state"] == "profile_invalid"
    assert status["physical_validation"] is False


def test_corrupt_profile_fails_closed(tmp_path):
    path = tmp_path / "optics.json"
    path.write_text('{"version": 1, "camera_matrix": "invalid"}', encoding="utf-8")
    status = load_calibration_status(path)
    assert status["state"] == "profile_invalid"
    assert status["profile_loaded"] is False


def test_loaded_profile_without_verified_mode_fails_closed(tmp_path):
    path = tmp_path / "optics.json"
    save_calibration_profile(path, profile())
    status = load_calibration_status(path)
    assert status["state"] == "mode_unknown"
    assert status["profile_loaded"] is True
    assert status["physical_validation"] is False


def test_loaded_profile_rejects_different_crop_with_same_resolution(tmp_path):
    path = tmp_path / "optics.json"
    save_calibration_profile(path, profile())
    status = load_calibration_status(
        path, camera_mode_id="other-crop", image_size=(640, 400)
    )
    assert status["state"] == "mode_incompatible"
    assert status["mode_compatible"] is False
