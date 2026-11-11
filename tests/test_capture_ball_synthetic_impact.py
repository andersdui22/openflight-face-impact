"""Selected-frame silhouette to synthetic impact integration regressions."""

import cv2 as cv
import numpy as np

from openflight.camera.capture_ball_synthetic_impact import (
    calculate_capture_ball_synthetic_impact,
)
from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.synthetic_face_polygon import SyntheticFacePolygon
from openflight.camera.synthetic_impact_pipeline import SyntheticImpactStatus
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def test_selected_frame_without_bright_contour_fails_closed():
    size = (320, 240)
    calibration = CheckerboardCalibration(
        size, np.array([[260., 0., 160.], [0., 260., 120.], [0., 0., 1.]]),
        np.zeros(5), 0., (),
    )
    blank = np.zeros((240, 320), dtype=np.uint8)
    disk = blank.copy()
    cv.circle(disk, (160, 120), 20, 220, thickness=-1)
    frames = (
        CameraFrame(blank, 100, 1000, 100, 1.),
        CameraFrame(blank, 200, 2000, 100, 1.),
        CameraFrame(disk, 300, 3000, 100, 1.),
    )
    capture = TriggeredCapture(frames, 2, 2500, shot_id="s", session_id="session")
    options = dict(
        ball_radius_mm=21.35, max_ball_residual_rad=0.02,
        max_face_rms_px=0.5, min_face_margin_px=0.1,
        contact_tolerance_mm=0.01, threshold=100,
        min_area_px=100., ball_border_margin_px=2.,
        min_circularity=0.8,
    )
    face_points = np.array([[-20., -10.], [20., -10.], [20., 10.], [-20., 10.]])
    polygon = SyntheticFacePolygon(face_points)
    result = calculate_capture_ball_synthetic_impact(
        calibration, capture, 1, face_points, face_points, polygon, **options,
    )
    assert result.status is SyntheticImpactStatus.INVALID_GEOMETRY
    assert "exactly one" in result.rejection_reason
    assert result.x_mm is None and result.y_mm is None
    result = calculate_capture_ball_synthetic_impact(
        calibration, capture, 3, face_points, face_points, polygon, **options,
    )
    assert result.status is SyntheticImpactStatus.INVALID_GEOMETRY
    assert "candidate frame index" in result.rejection_reason
