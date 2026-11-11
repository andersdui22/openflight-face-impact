"""Gate 19: camera status API revision helper must remain offline-only."""

import numpy as np

from openflight.camera.calibration_api_status import load_revision_bound_calibration_status
from openflight.camera.calibration_club_binding import CalibrationClubBinding
from openflight.camera.calibration_club_binding_store import save_calibration_club_binding
from openflight.camera.calibration_profile import CameraCalibrationProfile
from openflight.camera.calibration_revision import calibration_revision
from openflight.camera.calibration_store import save_calibration_profile
from openflight.camera.checkerboard_calibration import CheckerboardCalibration


def files(tmp_path):
    profile = CameraCalibrationProfile(
        CheckerboardCalibration(
            (640, 400),
            np.array([[530., 0., 315.], [0., 525., 198.], [0., 0., 1.]]),
            np.zeros(5), 0.2, (0.2, 0.2, 0.2),
        ),
        "synthetic:640x400:full-frame",
    )
    optics = tmp_path / "optics.json"
    binding = tmp_path / "binding.json"
    save_calibration_profile(optics, profile)
    save_calibration_club_binding(
        binding, CalibrationClubBinding(calibration_revision(profile), "club", "a" * 64)
    )
    return optics, binding


def test_matching_revision_does_not_verify_camera_or_club(tmp_path):
    result = load_revision_bound_calibration_status(*files(tmp_path))
    assert result["state"] == "mode_unknown"
    assert result["revision_compatible"] is True
    assert result["club_geometry_compatible"] is False
    assert result["physical_validation"] is False


def test_stale_revision_is_reported(tmp_path):
    optics, binding = files(tmp_path)
    save_calibration_club_binding(
        binding, CalibrationClubBinding("b" * 64, "club", "a" * 64)
    )
    result = load_revision_bound_calibration_status(optics, binding)
    assert result["state"] == "revision_invalid"
    assert result["revision_compatible"] is False
    assert result["physical_validation"] is False


def test_missing_binding_rejected(tmp_path):
    optics, binding = files(tmp_path)
    binding.unlink()
    result = load_revision_bound_calibration_status(optics, binding)
    assert result["state"] == "revision_invalid"
    assert result["binding_loaded"] is False


def test_absent_profile_uses_existing_status():
    result = load_revision_bound_calibration_status(None, None)
    assert result["state"] == "not_calibrated"
    assert result["physical_validation"] is False


def test_corrupt_profile_fails_closed(tmp_path):
    optics, binding = files(tmp_path)
    optics.write_text("not json", encoding="utf-8")
    result = load_revision_bound_calibration_status(optics, binding)
    assert result["state"] == "profile_invalid"
    assert result["physical_validation"] is False


def test_optional_binding_preserves_legacy_unknown_mode_status(tmp_path):
    optics, _ = files(tmp_path)
    result = load_revision_bound_calibration_status(optics, None)
    assert result["state"] == "mode_unknown"
    assert result["physical_validation"] is False


def test_malformed_binding_is_revision_invalid(tmp_path):
    optics, binding = files(tmp_path)
    binding.write_text("not json", encoding="utf-8")
    result = load_revision_bound_calibration_status(optics, binding)
    assert result["state"] == "revision_invalid"
    assert result["binding_loaded"] is False
    assert result["physical_validation"] is False


def test_missing_profile_does_not_validate_binding(tmp_path):
    optics, binding = files(tmp_path)
    optics.unlink()
    result = load_revision_bound_calibration_status(optics, binding)
    assert result["state"] == "profile_invalid"
    assert result["physical_validation"] is False
