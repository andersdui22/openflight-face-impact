"""Unmocked synthetic raster -> offline batch -> timing -> impact export.

The face pixels are explicitly supplied synthetic landmarks, not camera-derived
clubface recognition. This test cannot establish physical impact accuracy.
"""

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.offline_capture_batch import assess_offline_capture_batch
from openflight.camera.offline_impact_handoff import prepare_offline_impact_handoff
from openflight.camera.synthetic_face_polygon import SyntheticFacePolygon
from openflight.camera.synthetic_frame_candidates import SyntheticFrameCandidate
from openflight.camera.synthetic_impact_pipeline import SyntheticImpactStatus
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def test_rasterized_synthetic_contact_reaches_offline_export_without_mocks():
    size = (640, 400)
    radius = 21.35
    calibration = CheckerboardCalibration(
        size,
        np.array([[530., 0., 315.], [0., 525., 198.], [0., 0., 1.]]),
        np.array([-0.24, 0.08, 0.002, -0.003, 0.01]),
        0., (),
    )
    landmarks = np.array([
        [-44., -19.], [42., -17.], [36., 22.],
        [-35., 18.], [8., 12.], [-9., -4.],
    ])
    polygon = SyntheticFacePolygon(
        np.array([[-45., -25.], [45., -25.], [45., 25.], [-45., 25.]])
    )
    rotation_vector = np.array([0.29, -0.32, 0.2])
    rotation, _ = cv.Rodrigues(rotation_vector)
    rotation = rotation @ np.diag([1., -1., -1.])
    translation = np.array([64., -22., 420.])

    def project(points):
        pixels, _ = cv.projectPoints(
            np.asarray(points, dtype=float), np.zeros(3), np.zeros(3),
            calibration.camera_matrix, calibration.distortion,
        )
        return pixels.reshape(-1, 2)

    face_points = np.column_stack((landmarks, np.zeros(len(landmarks))))
    face_pixels = project(face_points @ rotation.T + translation)
    ball_center = rotation @ np.array([12., 5., radius]) + translation
    direction = ball_center / np.linalg.norm(ball_center)
    across = np.cross(direction, [0., 1., 0.])
    across /= np.linalg.norm(across)
    up = np.cross(direction, across)
    ratio = radius / np.linalg.norm(ball_center)
    ring_center = ball_center * (1. - ratio ** 2)
    ring_radius = radius * np.sqrt(1. - ratio ** 2)
    angles = np.linspace(0., 2. * np.pi, 720, endpoint=False)
    rim = ring_center + ring_radius * (
        np.cos(angles)[:, None] * across
        + np.sin(angles)[:, None] * up
    )
    image = np.zeros((size[1], size[0]), dtype=np.uint8)
    cv.fillPoly(image, [np.rint(project(rim)).astype(np.int32)], 220)
    blank = np.zeros_like(image)
    capture = TriggeredCapture(
        (
            CameraFrame(blank, 100, 1000, 100, 1.),
            CameraFrame(image, 200, 2000, 100, 1.),
        ),
        1, 1500, shot_id="synthetic-shot", session_id="synthetic-session",
    )
    batch = assess_offline_capture_batch(
        calibration, capture,
        (SyntheticFrameCandidate(0, face_pixels),
         SyntheticFrameCandidate(1, face_pixels)),
        landmarks, polygon,
        ball_radius_mm=radius,
        max_ball_residual_rad=0.03,
        max_face_rms_px=0.5,
        min_face_margin_px=0.1,
        contact_tolerance_mm=5.,
        threshold=100,
        min_area_px=300.,
        ball_border_margin_px=2.,
        min_circularity=0.8,
    )
    assert batch.frames[0].assessment.impact.status is SyntheticImpactStatus.INVALID_GEOMETRY
    assert batch.frames[1].assessment.impact.status is SyntheticImpactStatus.OK, (
        batch.frames[1].assessment.impact.rejection_reason
    )
    handoff = prepare_offline_impact_handoff(
        capture, batch, max_sensor_gap_ns=100, max_host_gap_ns=1000,
    )
    result = handoff.impact
    assert handoff.temporal.spacing.accepted is True
    assert handoff.temporal.accepted_for_offline_analysis is True
    assert result.accepted_for_offline_analysis is True
    assert (result.shot_id, result.session_id, result.frame_index) == (
        "synthetic-shot", "synthetic-session", 1,
    )
    assert result.x_mm == pytest.approx(12., abs=5.)
    assert result.y_mm == pytest.approx(5., abs=5.)
    assert result.horizontal_region == "toe"
    assert result.vertical_region == "high"
    assert result.physically_validated is False
    assert result.position_uncertainty_mm is None
