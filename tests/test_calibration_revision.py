"""Gate 19: deterministic revision binding and fail-closed stale-profile tests."""

from dataclasses import replace

import numpy as np
import pytest

from openflight.camera.calibration_profile import CameraCalibrationProfile
from openflight.camera.calibration_revision import (
    calibration_revision,
    require_calibration_revision,
)
from openflight.camera.checkerboard_calibration import CheckerboardCalibration


def profile():
    return CameraCalibrationProfile(
        CheckerboardCalibration(
            (640, 400),
            np.array([[530., 0., 315.], [0., 525., 198.], [0., 0., 1.]]),
            np.array([-0.24, 0.08, 0.002, -0.003, 0.]),
            0.22,
            (0.3, 0.25, 0.28),
        ),
        "synthetic:640x400:full-frame",
    )


def test_roundtrip_preserves_revision():
    original = profile()
    loaded = CameraCalibrationProfile.from_json(original.to_json())
    assert calibration_revision(loaded) == calibration_revision(original)
    assert require_calibration_revision(
        loaded, expected_revision=calibration_revision(original)
    ) == calibration_revision(original)


def test_changed_optics_are_stale_even_at_same_resolution():
    original = profile()
    changed = replace(
        original,
        calibration=replace(
            original.calibration, camera_matrix=np.array(
                [[531., 0., 315.], [0., 525., 198.], [0., 0., 1.]]
            )
        ),
    )
    with pytest.raises(ValueError, match="stale"):
        require_calibration_revision(
            changed, expected_revision=calibration_revision(original)
        )


def test_changed_mode_is_stale_even_with_same_optics():
    original = profile()
    with pytest.raises(ValueError, match="stale"):
        require_calibration_revision(
            replace(original, camera_mode_id="different-crop"),
            expected_revision=calibration_revision(original),
        )


@pytest.mark.parametrize("revision", [None, "", "A" * 64, "0" * 63, "invalid"])
def test_unknown_or_malformed_expected_revision_fails_closed(revision):
    with pytest.raises(ValueError, match="explicit SHA-256"):
        require_calibration_revision(profile(), expected_revision=revision)


def test_digest_does_not_establish_physical_validation():
    original = profile()
    assert original.evidence_kind == "synthetic_offline"
    assert len(calibration_revision(original)) == 64
