"""Gate 19: synthetic calibration-to-club identity guards."""

from dataclasses import replace

import numpy as np
import pytest

from openflight.camera.calibration_club_binding import (
    CalibrationClubBinding,
    require_calibration_club_binding,
)
from openflight.camera.calibration_profile import CameraCalibrationProfile
from openflight.camera.calibration_revision import calibration_revision
from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.club_face_model import ClubFaceModel, ClubFamily, FaceSurface


def profile():
    return CameraCalibrationProfile(
        CheckerboardCalibration(
            (640, 400),
            np.array([[530., 0., 315.], [0., 525., 198.], [0., 0., 1.]]),
            np.zeros(5), 0.2, (0.2, 0.2, 0.2),
        ),
        "synthetic:640x400:full-frame",
    )


def club():
    return ClubFaceModel(
        ClubFamily.IRON, "synthetic-7iron", FaceSurface.PLANAR,
        width_mm=60., height_mm=30., evidence_source="synthetic-test-fixture",
    )


def test_matching_offline_binding_is_accepted():
    p = profile()
    require_calibration_club_binding(
        CalibrationClubBinding(calibration_revision(p), club().model_id),
        profile=p, club_model=club(),
    )


def test_stale_calibration_rejected():
    p = profile()
    with pytest.raises(ValueError, match="stale"):
        require_calibration_club_binding(
            CalibrationClubBinding(calibration_revision(p), club().model_id),
            profile=replace(p, camera_mode_id="different-crop"), club_model=club(),
        )


def test_substituted_club_identity_rejected():
    p = profile()
    with pytest.raises(ValueError, match="identity incompatible"):
        require_calibration_club_binding(
            CalibrationClubBinding(calibration_revision(p), club().model_id),
            profile=p, club_model=replace(club(), model_id="synthetic-9iron"),
        )


def test_unknown_club_geometry_rejected():
    p = profile()
    with pytest.raises(ValueError, match="evidenced"):
        require_calibration_club_binding(
            CalibrationClubBinding(calibration_revision(p), "unknown"),
            profile=p, club_model=ClubFaceModel(ClubFamily.IRON, "unknown"),
        )


def test_malformed_binding_rejected():
    with pytest.raises(ValueError, match="revision"):
        CalibrationClubBinding("", "synthetic-7iron")
    with pytest.raises(ValueError, match="identity"):
        CalibrationClubBinding("placeholder", " ")
