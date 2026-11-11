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
