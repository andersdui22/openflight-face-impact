"""Integrated Gate 20-24 offline multi-frame batch and audit tests."""

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.offline_capture_batch import assess_offline_capture_batch
from openflight.camera.synthetic_face_polygon import SyntheticFacePolygon
from openflight.camera.synthetic_frame_candidates import SyntheticFrameCandidate
from openflight.camera.synthetic_impact_pipeline import SyntheticImpactStatus
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def setup():
    size = (320, 240)
    calibration = CheckerboardCalibration(
        size, np.array([[260., 0., 160.], [0., 260., 120.], [0., 0., 1.]]),
        np.zeros(5), 0., (),
    )
    blank = np.zeros((240, 320), dtype=np.uint8)
    disk = blank.copy()
    cv.circle(disk, (160, 120), 20, 220, -1)
    capture = TriggeredCapture(
        (
            CameraFrame(blank.copy(), 100, 1000, 100, 1.),
            CameraFrame(blank.copy(), 200, 2000, 100, 1.),
            CameraFrame(disk, 300, 3000, 100, 1.),
        ), 2, 2500, shot_id="shot", session_id="session",
    )
    landmarks = np.array([[-20., -10.], [20., -10.], [20., 10.], [-20., 10.]])
    options = dict(
        ball_radius_mm=21.35, max_ball_residual_rad=0.02,
        max_face_rms_px=0.5, min_face_margin_px=0.1,
        contact_tolerance_mm=0.01, threshold=100, min_area_px=100.,
        ball_border_margin_px=2., min_circularity=0.8,
    )
    return calibration, capture, landmarks, options


def test_full_offline_batch_reports_two_independent_rejection_causes():
    calibration, capture, landmarks, options = setup()
    candidates = (
        SyntheticFrameCandidate(1, landmarks),
        SyntheticFrameCandidate(2, np.zeros((4, 2))),
    )
    report = assess_offline_capture_batch(
        calibration, capture, candidates,
        landmarks, SyntheticFacePolygon(landmarks), **options,
    )
    assert tuple(item.frame_index for item in report.frames) == (1, 2)
    assert report.audit.total == 2
    assert report.audit.accepted_synthetic == 0
    assert report.audit.rejected_invalid_geometry == 2
    assert report.audit.all_rejections_fail_closed is True
    assert report.audit.physical_contact_established is False
    assert report.audit.physical_accuracy_established is False
    assert "exactly one" in report.frames[0].assessment.impact.rejection_reason
    assert "exactly one" not in report.frames[1].assessment.impact.rejection_reason
    for item in report.frames:
        assert item.assessment.impact.status is SyntheticImpactStatus.INVALID_GEOMETRY
        assert item.assessment.impact.x_mm is None
        assert item.assessment.quality.reason == item.assessment.impact.rejection_reason


def test_full_offline_batch_rejects_duplicate_candidates_before_processing():
    calibration, capture, landmarks, options = setup()
    candidate = SyntheticFrameCandidate(2, landmarks)
    with pytest.raises(ValueError, match="duplicate"):
        assess_offline_capture_batch(
            calibration, capture, (candidate, candidate),
            landmarks, SyntheticFacePolygon(landmarks), **options,
        )


def test_full_offline_batch_enforces_resource_limit():
    calibration, capture, landmarks, options = setup()
    candidates = (
        SyntheticFrameCandidate(1, landmarks),
        SyntheticFrameCandidate(2, landmarks),
    )
    with pytest.raises(ValueError, match="bounded"):
        assess_offline_capture_batch(
            calibration, capture, candidates,
            landmarks, SyntheticFacePolygon(landmarks),
            max_candidates=1, **options,
        )
