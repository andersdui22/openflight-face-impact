"""Gate 24 end-to-end synthetic capture rejection and quality consistency."""

import numpy as np

from openflight.camera.capture_ball_synthetic_quality import (
    assess_capture_ball_synthetic_impact,
)
from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.synthetic_face_polygon import SyntheticFacePolygon
from openflight.camera.synthetic_impact_pipeline import SyntheticImpactStatus
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def test_missing_ball_in_selected_frame_has_consistent_rejection_quality():
    size = (320, 240)
    calibration = CheckerboardCalibration(
        size, np.array([[260., 0., 160.], [0., 260., 120.], [0., 0., 1.]]),
        np.zeros(5), 0., (),
    )
    blank = np.zeros((240, 320), dtype=np.uint8)
    frames = tuple(
        CameraFrame(blank.copy(), i * 100, i * 1000, 100, 1.)
        for i in (1, 2, 3)
    )
    capture = TriggeredCapture(frames, 2, 2500, shot_id="shot", session_id="session")
    landmarks = np.array([[-20., -10.], [20., -10.], [20., 10.], [-20., 10.]])
    result = assess_capture_ball_synthetic_impact(
        calibration, capture, 2, landmarks, landmarks,
        SyntheticFacePolygon(landmarks),
        ball_radius_mm=21.35, max_ball_residual_rad=0.02,
        max_face_rms_px=0.5, min_face_margin_px=0.1,
        contact_tolerance_mm=0.01, threshold=100, min_area_px=100.,
        ball_border_margin_px=2., min_circularity=0.8,
    )
    assert result.impact.status is SyntheticImpactStatus.INVALID_GEOMETRY
    assert result.impact.x_mm is None and result.impact.y_mm is None
    assert result.quality.accepted_synthetic_geometry is False
    assert result.quality.reason == result.impact.rejection_reason
    assert result.quality.physically_validated is False
    assert result.quality.position_uncertainty_mm is None


def test_accepted_synthetic_impact_is_reported_without_physical_confidence(monkeypatch):
    from openflight.camera import capture_ball_synthetic_quality as module
    from openflight.camera.synthetic_impact_pipeline import SyntheticImpactResult

    expected = SyntheticImpactResult(
        SyntheticImpactStatus.OK, 12., -4., "toe", "low",
    )
    def fake_capture_impact(*_args, **_kwargs):
        return expected

    monkeypatch.setattr(module, "calculate_capture_ball_synthetic_impact", fake_capture_impact)
    result = module.assess_capture_ball_synthetic_impact(
        None, None, 2, None, None, None,
        ball_radius_mm=21.35, max_ball_residual_rad=0.02,
        max_face_rms_px=0.5, min_face_margin_px=0.1,
        contact_tolerance_mm=0.01, threshold=100,
        min_area_px=100., ball_border_margin_px=2.,
    )
    assert result.impact is expected
    assert result.quality.accepted_synthetic_geometry is True
    assert result.quality.physically_validated is False
    assert result.quality.position_uncertainty_mm is None
    assert "unverified" in result.quality.reason


def test_real_selected_disk_passes_contour_stage_but_rejects_bad_face_pose():
    import cv2 as cv

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
    # Deliberately invalid face pixels: contour extraction succeeds first,
    # but planar pose estimation must reject this degenerate observation.
    degenerate_face_pixels = np.zeros((4, 2), dtype=float)
    result = assess_capture_ball_synthetic_impact(
        calibration, capture, 2, landmarks, degenerate_face_pixels,
        SyntheticFacePolygon(landmarks),
        ball_radius_mm=21.35, max_ball_residual_rad=0.02,
        max_face_rms_px=0.5, min_face_margin_px=0.1,
        contact_tolerance_mm=0.01, threshold=100, min_area_px=100.,
        ball_border_margin_px=2., min_circularity=0.8,
    )
    assert result.impact.status is SyntheticImpactStatus.INVALID_GEOMETRY
    assert "exactly one" not in result.impact.rejection_reason
    assert result.quality.reason == result.impact.rejection_reason
    assert result.quality.physically_validated is False
    assert result.impact.x_mm is None and result.impact.y_mm is None
