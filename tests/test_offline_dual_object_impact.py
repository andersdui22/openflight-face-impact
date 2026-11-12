"""Synthetic two-object scene through the real 3D impact geometry path."""

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.offline_dual_object_impact import assess_synthetic_dual_object_impact
from openflight.camera.synthetic_face_polygon import SyntheticFacePolygon
from openflight.camera.synthetic_impact_pipeline import SyntheticImpactStatus
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def scene():
    image = np.zeros((240, 320), dtype=np.uint8)
    cv.rectangle(image, (35, 40), (115, 95), 230, -1)
    cv.circle(image, (240, 150), 20, 220, -1)
    return image


def assess(image):
    capture = TriggeredCapture(
        (CameraFrame(image.copy(), 100, 1000, 100, 1.),
         CameraFrame(image.copy(), 200, 2000, 100, 1.)),
        1, 1500, shot_id="shot", session_id="session",
    )
    calibration = CheckerboardCalibration(
        (320, 240),
        np.array([[260., 0., 160.], [0., 260., 120.], [0., 0., 1.]]),
        np.zeros(5), 0., (),
    )
    landmarks = np.array([[-20., -10.], [20., -10.], [20., 10.], [-20., 10.]])
    return assess_synthetic_dual_object_impact(
        calibration, capture, 1, landmarks, SyntheticFacePolygon(landmarks),
        ball_radius_mm=21.35, max_ball_residual_rad=0.02,
        max_face_rms_px=0.5, min_face_margin_px=0.1,
        contact_tolerance_mm=0.01,
    )


def test_two_shapes_reach_real_geometry_and_quality_pipeline():
    result = assess(scene())
    assert result.observation.face.frame_index == 1
    assert result.observation.face.shot_id == "shot"
    assert result.impact.status in tuple(SyntheticImpactStatus)
    assert result.quality.physically_validated is False
    assert result.physical_contact_confirmed is False
    assert result.observation.ball_contour_px.flags.writeable is False


def test_extra_shape_fails_before_geometry():
    image = scene()
    cv.circle(image, (160, 210), 10, 220, -1)
    with pytest.raises(ValueError, match="exactly two"):
        assess(image)


def test_ball_occlusion_fails_before_geometry():
    image = scene()
    cv.circle(image, (240, 150), 7, 0, -1)
    with pytest.raises(ValueError, match="interior hole"):
        assess(image)
