"""Gate 19: offline lifecycle must reject stale and unverified evidence."""

from dataclasses import replace

import numpy as np

from openflight.camera.calibration_club_binding import CalibrationClubBinding
from openflight.camera.calibration_club_binding_store import save_calibration_club_binding
from openflight.camera.calibration_club_lifecycle import validate_stored_calibration_club
from openflight.camera.calibration_profile import CameraCalibrationProfile
from openflight.camera.calibration_revision import calibration_revision
from openflight.camera.calibration_store import save_calibration_profile
from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.club_face_model import ClubFaceModel, ClubFamily, FaceSurface
from openflight.camera.club_geometry_revision import club_geometry_revision


MODE = "synthetic:640x400:full-frame"
SIZE = (640, 400)


def profile():
    return CameraCalibrationProfile(
        CheckerboardCalibration(
            SIZE, np.array([[530., 0., 315.], [0., 525., 198.], [0., 0., 1.]]),
            np.zeros(5), 0.2, (0.2, 0.2, 0.2),
        ), MODE,
    )


def club():
    return ClubFaceModel(
        ClubFamily.IRON, "synthetic-iron", FaceSurface.PLANAR,
        width_mm=60., height_mm=30., evidence_source="synthetic-test-fixture",
    )


def saved(tmp_path):
    p, c = profile(), club()
    optics, binding = tmp_path / "optics.json", tmp_path / "binding.json"
    save_calibration_profile(optics, p)
    save_calibration_club_binding(
        binding, CalibrationClubBinding(
            calibration_revision(p), c.model_id, club_geometry_revision(c)
        )
    )
    return optics, binding


def check(paths, model=None, mode=MODE, size=SIZE):
    return validate_stored_calibration_club(
        *paths, club_model=club() if model is None else model,
        camera_mode_id=mode, image_size=size,
    )


def test_stored_matching_evidence_remains_offline_only(tmp_path):
    result = check(saved(tmp_path))
    assert result["state"] == "offline_evidence_compatible"
    assert result["revision_compatible"]
    assert result["club_geometry_compatible"]
    assert result["physical_validation"] is False


def test_unverified_camera_mode_fails_closed(tmp_path):
    result = check(saved(tmp_path), mode=None)
    assert result["state"] == "mode_unknown"
    assert not result["revision_compatible"]


def test_mismatched_camera_mode_fails_closed(tmp_path):
    result = check(saved(tmp_path), mode="different-crop")
    assert result["state"] == "mode_incompatible"
    assert not result["mode_compatible"]


def test_changed_geometry_rejected(tmp_path):
    result = check(saved(tmp_path), model=replace(club(), width_mm=61.))
    assert result["state"] == "binding_incompatible"
    assert not result["club_geometry_compatible"]


def test_missing_binding_fails_closed(tmp_path):
    optics, binding = saved(tmp_path)
    binding.unlink()
    result = check((optics, binding))
    assert result["state"] == "evidence_invalid"
    assert result["profile_loaded"]
    assert not result["binding_loaded"]


def test_stale_optics_revision_rejected(tmp_path):
    optics, binding = saved(tmp_path)
    save_calibration_profile(optics, replace(profile(), camera_mode_id="other"))
    result = check((optics, binding), mode="other")
    assert result["state"] == "binding_incompatible"
    assert not result["revision_compatible"]


def test_corrupt_binding_fails_closed_without_false_compatibility(tmp_path):
    optics, binding = saved(tmp_path)
    binding.write_text('{"version": 999}', encoding="utf-8")
    result = check((optics, binding))
    assert result["state"] == "evidence_invalid"
    assert result["profile_loaded"]
    assert not result["binding_loaded"]
    assert not result["mode_compatible"]
    assert result["physical_validation"] is False


def test_corrupt_profile_fails_closed_without_loading_binding(tmp_path):
    optics, binding = saved(tmp_path)
    optics.write_text('{"version": 999}', encoding="utf-8")
    result = check((optics, binding))
    assert result["state"] == "evidence_invalid"
    assert not result["profile_loaded"]
    assert not result["binding_loaded"]
    assert result["physical_validation"] is False


def test_unknown_geometry_rejected_even_with_matching_model_identity(tmp_path):
    result = check(
        saved(tmp_path), model=ClubFaceModel(ClubFamily.IRON, "synthetic-iron")
    )
    assert result["state"] == "binding_incompatible"
    assert not result["club_geometry_compatible"]
    assert result["physical_validation"] is False


def test_wrong_image_dimensions_rejected(tmp_path):
    result = check(saved(tmp_path), size=(800, 600))
    assert result["state"] == "mode_incompatible"
    assert not result["mode_compatible"]
    assert result["physical_validation"] is False


def test_malformed_club_model_is_rejected_without_exception(tmp_path):
    optics, binding = saved(tmp_path)
    result = validate_stored_calibration_club(
        optics, binding, club_model=None,
        camera_mode_id=MODE, image_size=SIZE,
    )
    assert result["state"] == "binding_incompatible"
    assert not result["club_geometry_compatible"]
    assert result["physical_validation"] is False
