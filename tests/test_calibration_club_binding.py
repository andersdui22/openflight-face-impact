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
from openflight.camera.club_geometry_revision import club_geometry_revision


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
        CalibrationClubBinding(calibration_revision(p), club().model_id, club_geometry_revision(club())),
        profile=p, club_model=club(),
    )


def test_stale_calibration_rejected():
    p = profile()
    with pytest.raises(ValueError, match="stale"):
        require_calibration_club_binding(
            CalibrationClubBinding(calibration_revision(p), club().model_id, club_geometry_revision(club())),
            profile=replace(p, camera_mode_id="different-crop"), club_model=club(),
        )


def test_substituted_club_identity_rejected():
    p = profile()
    with pytest.raises(ValueError, match="identity incompatible"):
        require_calibration_club_binding(
            CalibrationClubBinding(calibration_revision(p), club().model_id, club_geometry_revision(club())),
            profile=p, club_model=replace(club(), model_id="synthetic-9iron"),
        )


def test_unknown_club_geometry_rejected():
    p = profile()
    with pytest.raises(ValueError, match="evidenced"):
        require_calibration_club_binding(
            CalibrationClubBinding(calibration_revision(p), "unknown", club_geometry_revision(club())),
            profile=p, club_model=ClubFaceModel(ClubFamily.IRON, "unknown"),
        )


def test_malformed_binding_rejected():
    with pytest.raises(ValueError, match="revision"):
        CalibrationClubBinding("", "synthetic-7iron")
    with pytest.raises(ValueError, match="identity"):
        CalibrationClubBinding("placeholder", " ")


def test_same_club_identity_but_changed_dimensions_rejected():
    p = profile()
    original = club()
    binding = CalibrationClubBinding(
        calibration_revision(p), original.model_id, club_geometry_revision(original)
    )
    with pytest.raises(ValueError, match="geometry revision"):
        require_calibration_club_binding(
            binding, profile=p, club_model=replace(original, width_mm=61.),
        )


def test_missing_geometry_revision_rejected():
    p = profile()
    with pytest.raises(ValueError, match="geometry revision required"):
        require_calibration_club_binding(
            CalibrationClubBinding(calibration_revision(p), club().model_id),
            profile=p, club_model=club(),
        )


def test_geometry_revision_is_deterministic_and_provenance_sensitive():
    original = club()
    assert club_geometry_revision(original) == club_geometry_revision(club())
    assert club_geometry_revision(original) != club_geometry_revision(
        replace(original, evidence_source="other-synthetic-fixture")
    )


@pytest.mark.parametrize("change", [
    {"family": ClubFamily.WEDGE},
    {"surface": FaceSurface.CURVED},
    {"height_mm": 31.},
    {"model_id": "synthetic-8iron"},
    {"evidence_source": "revised-synthetic-fixture"},
])
def test_geometry_revision_detects_every_model_contract_change(change):
    original = club()
    changed = replace(original, **change)
    assert club_geometry_revision(original) != club_geometry_revision(changed)


def test_geometry_revision_detects_curved_surface_radii_changes():
    original = ClubFaceModel(
        ClubFamily.DRIVER, "synthetic-driver", FaceSurface.CURVED,
        width_mm=90., height_mm=45., bulge_radius_mm=250.,
        roll_radius_mm=300., evidence_source="synthetic-test-fixture",
    )
    for field in ("bulge_radius_mm", "roll_radius_mm"):
        changed = replace(original, **{field: getattr(original, field) + 1.})
        assert club_geometry_revision(original) != club_geometry_revision(changed)


def test_geometry_revision_rejects_unvalidated_input():
    with pytest.raises(ValueError, match="validated club model"):
        club_geometry_revision(None)
