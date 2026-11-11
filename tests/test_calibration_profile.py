"""Gate 16 offline profile round-trip and fail-closed compatibility checks."""

import json

import numpy as np
import pytest

from openflight.camera.calibration_profile import CameraCalibrationProfile
from openflight.camera.checkerboard_calibration import CheckerboardCalibration


def make_profile():
    fit = CheckerboardCalibration(
        (640, 400),
        np.array([[530.0, 0.0, 315.0], [0.0, 525.0, 198.0], [0.0, 0.0, 1.0]]),
        np.array([-0.24, 0.08, 0.002, -0.003, 0.0]),
        0.22,
        (0.3, 0.25, 0.28),
    )
    return CameraCalibrationProfile(fit, "synthetic:640x400:full-frame")


def test_profile_round_trip_preserves_optics_and_residuals():
    original = make_profile()
    restored = CameraCalibrationProfile.from_json(original.to_json())
    assert restored.to_json() == original.to_json()
    np.testing.assert_array_equal(restored.calibration.camera_matrix, original.calibration.camera_matrix)
    np.testing.assert_array_equal(restored.calibration.distortion, original.calibration.distortion)
    assert restored.evidence_kind == "synthetic_offline"


def test_mode_identity_required_even_with_matching_dimensions():
    profile = make_profile()
    profile.require_mode("synthetic:640x400:full-frame", (640, 400))
    with pytest.raises(ValueError, match="incompatible"):
        profile.require_mode("different-crop:640x400", (640, 400))
    with pytest.raises(ValueError, match="incompatible"):
        profile.require_mode("synthetic:640x400:full-frame", (800, 600))


@pytest.mark.parametrize("field,value", [
    ("version", 2),
    ("version", True),
    ("evidence_kind", "physical_verified"),
    ("camera_mode_id", ""),
    ("image_size", [640, 0]),
    ("camera_matrix", [[1, 0, 0], [0, 1, 0]]),
    ("distortion", [0, 0, 0, 0]),
    ("fit_rms_px", -1),
    ("validation_rms_px", []),
])
def test_invalid_profiles_rejected(field, value):
    data = json.loads(make_profile().to_json())
    data[field] = value
    with pytest.raises((ValueError, TypeError)):
        CameraCalibrationProfile.from_json(json.dumps(data))


def test_unknown_fields_rejected():
    data = json.loads(make_profile().to_json())
    data["physical_accuracy_mm"] = 0.01
    with pytest.raises(ValueError, match="schema"):
        CameraCalibrationProfile.from_json(json.dumps(data))


def test_nonfinite_optics_rejected():
    data = json.loads(make_profile().to_json())
    data["camera_matrix"][0][0] = float("nan")
    with pytest.raises(ValueError, match="finite"):
        CameraCalibrationProfile.from_json(json.dumps(data))
