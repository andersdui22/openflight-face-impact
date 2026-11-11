"""Gates 20-24: bounded explicit candidate assessment and rejection matrix."""

from dataclasses import replace

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.synthetic_face_polygon import SyntheticFacePolygon
from openflight.camera.synthetic_frame_candidates import (
    SyntheticFrameCandidate, assess_synthetic_frame_candidates,
)
from openflight.camera.synthetic_impact_pipeline import SyntheticImpactStatus
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def fixture_data():
    size = (320, 240)
    calibration = CheckerboardCalibration(
        size, np.array([[260., 0., 160.], [0., 260., 120.], [0., 0., 1.]]),
        np.zeros(5), 0., (),
    )
    blank = np.zeros((240, 320), dtype=np.uint8)
    disk = blank.copy()
    cv.circle(disk, (160, 120), 20, 220, thickness=-1)
    frames = (
        CameraFrame(blank.copy(), 100, 1000, 100, 1.),
        CameraFrame(blank.copy(), 200, 2000, 100, 1.),
        CameraFrame(disk, 300, 3000, 100, 1.),
    )
    capture = TriggeredCapture(frames, 2, 2500, shot_id="shot", session_id="session")
    landmarks = np.array([[-20., -10.], [20., -10.], [20., 10.], [-20., 10.]])
    options = dict(
        ball_radius_mm=21.35, max_ball_residual_rad=0.02,
        max_face_rms_px=0.5, min_face_margin_px=0.1,
        contact_tolerance_mm=0.01, threshold=100,
        min_area_px=100., ball_border_margin_px=2., min_circularity=0.8,
    )
    return calibration, capture, landmarks, SyntheticFacePolygon(landmarks), options


def evaluate(candidates, capture_override=None, **extra):
    calibration, capture, landmarks, polygon, options = fixture_data()
    options.update(extra)
    return assess_synthetic_frame_candidates(
        calibration, capture if capture_override is None else capture_override,
        candidates, landmarks, polygon, **options,
    )


def test_two_frames_are_reported_separately_without_contact_selection():
    _, _, landmarks, _, _ = fixture_data()
    candidates = (
        SyntheticFrameCandidate(1, landmarks),
        SyntheticFrameCandidate(2, np.zeros((4, 2))),
    )
    results = evaluate(candidates)
    assert tuple(item.frame_index for item in results) == (1, 2)
    assert all(item.assessment.impact.status is SyntheticImpactStatus.INVALID_GEOMETRY
               for item in results)
    assert "exactly one" in results[0].assessment.impact.rejection_reason
    assert "exactly one" not in results[1].assessment.impact.rejection_reason
    for item in results:
        assert item.assessment.impact.x_mm is None
        assert item.assessment.impact.y_mm is None
        assert item.assessment.quality.reason == item.assessment.impact.rejection_reason
        assert item.assessment.quality.physically_validated is False
        assert item.assessment.quality.position_uncertainty_mm is None


def test_out_of_range_frame_fails_closed_in_individual_result():
    _, _, landmarks, _, _ = fixture_data()
    result, = evaluate((SyntheticFrameCandidate(9, landmarks),))
    assert result.frame_index == 9
    assert result.assessment.impact.status is SyntheticImpactStatus.INVALID_GEOMETRY
    assert "candidate frame index" in result.assessment.impact.rejection_reason


def test_candidate_copies_supplied_pixels():
    pixels = np.ones((4, 2))
    candidate = SyntheticFrameCandidate(2, pixels)
    pixels[:] = 99
    assert np.all(candidate.face_pixels_px == 1)
    assert candidate.face_pixels_px.flags.writeable is False


@pytest.mark.parametrize("index", [-1, True, 2.5, "2"])
def test_invalid_candidate_identity_rejected(index):
    with pytest.raises(ValueError, match="frame index"):
        SyntheticFrameCandidate(index, np.zeros((4, 2)))


@pytest.mark.parametrize("pixels", [
    np.ones((4, 3)), np.array([[np.nan, 1.]]),
    np.array([["a", "b"]]), np.zeros(4),
])
def test_invalid_face_pixels_rejected(pixels):
    with pytest.raises(ValueError, match="face pixels"):
        SyntheticFrameCandidate(2, pixels)


def test_duplicate_frame_identity_rejected_before_assessment():
    candidate = SyntheticFrameCandidate(2, np.zeros((4, 2)))
    with pytest.raises(ValueError, match="duplicate"):
        evaluate((candidate, replace(candidate)))


def test_candidate_count_limit_rejected_before_assessment():
    _, _, landmarks, _, _ = fixture_data()
    candidates = (SyntheticFrameCandidate(1, landmarks),
                  SyntheticFrameCandidate(2, landmarks))
    with pytest.raises(ValueError, match="bounded"):
        evaluate(candidates, max_candidates=1)


@pytest.mark.parametrize("candidates", [(), [], None])
def test_empty_or_wrong_batch_type_rejected(candidates):
    with pytest.raises(ValueError, match="bounded"):
        evaluate(candidates)


@pytest.mark.parametrize("limit", [0, -1, True, 2.5])
def test_invalid_candidate_limit_rejected(limit):
    _, _, landmarks, _, _ = fixture_data()
    with pytest.raises(ValueError, match="max_candidates"):
        evaluate((SyntheticFrameCandidate(2, landmarks),), max_candidates=limit)
