"""Gate 20-24: synthetic rendered ball image through real contour and pose solvers."""

import cv2 as cv
import numpy as np

from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.offline_capture_batch import assess_offline_capture_batch
from openflight.camera.offline_impact_handoff import prepare_offline_impact_handoff
from openflight.camera.synthetic_face_polygon import SyntheticFacePolygon
from openflight.camera.synthetic_frame_candidates import SyntheticFrameCandidate
from openflight.camera.synthetic_impact_pipeline import SyntheticImpactStatus
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def test_rendered_sphere_and_projected_face_complete_positive_image_pipeline():
    """No geometry solver is mocked: render a tangent sphere silhouette."""
    size = (640, 400)
    radius = 21.35
    matrix = np.array([[530., 0., 315.], [0., 525., 198.], [0., 0., 1.]])
    distortion = np.array([-0.24, 0.08, 0.002, -0.003, 0.01])
    calibration = CheckerboardCalibration(size, matrix, distortion, 0., ())
    landmarks = np.array([
        [-44., -19.], [42., -17.], [36., 22.],
        [-35., 18.], [8., 12.], [-9., -4.],
    ])
    polygon = SyntheticFacePolygon(
        np.array([[-45., -25.], [45., -25.], [45., 25.], [-45., 25.]])
    )
    rotation_tilt, _ = cv.Rodrigues(np.array([0.29, -0.32, 0.2]))
    rotation = rotation_tilt @ np.diag([1., -1., -1.])
    translation = np.array([64., -22., 420.])
    local_center = np.array([12., 5., radius])
    ball_center = rotation @ local_center + translation

    def project(points):
        pixels, _ = cv.projectPoints(
            np.asarray(points, dtype=float), np.zeros(3), np.zeros(3),
            matrix, distortion,
        )
        return pixels.reshape(-1, 2)

    face_points = np.column_stack((landmarks, np.zeros(len(landmarks))))
    face_pixels = project(face_points @ rotation.T + translation)
    direction = ball_center / np.linalg.norm(ball_center)
    transverse = np.cross(direction, [0., 1., 0.])
    transverse /= np.linalg.norm(transverse)
    vertical = np.cross(direction, transverse)
    ratio = radius / np.linalg.norm(ball_center)
    ring_center = ball_center * (1. - ratio**2)
    ring_radius = radius * np.sqrt(1. - ratio**2)
    angles = np.linspace(0., 2. * np.pi, 720, endpoint=False)
    ring = ring_center + ring_radius * (
        np.cos(angles)[:, None] * transverse
        + np.sin(angles)[:, None] * vertical
    )
    rim_pixels = project(ring)
    image = np.zeros((size[1], size[0]), dtype=np.uint8)
    cv.fillPoly(image, [np.rint(rim_pixels).astype(np.int32)], 220)
    blank = np.zeros_like(image)
    capture = TriggeredCapture(
        (
            CameraFrame(blank.copy(), 100, 1000, 100, 1.),
            CameraFrame(blank.copy(), 200, 2000, 100, 1.),
            CameraFrame(image, 300, 3000, 100, 1.),
        ), 2, 2500, shot_id="rendered-ball", session_id="synthetic",
    )
    report = assess_offline_capture_batch(
        calibration, capture, (SyntheticFrameCandidate(2, face_pixels),),
        landmarks, polygon,
        ball_radius_mm=radius, max_ball_residual_rad=0.015,
        max_face_rms_px=0.5, min_face_margin_px=0.1,
        contact_tolerance_mm=5., threshold=100, min_area_px=100.,
        ball_border_margin_px=2., min_circularity=0.8,
    )
    assert report.audit.total == 1
    result = report.frames[0].assessment
    assert result.impact.status is SyntheticImpactStatus.OK, result.impact.rejection_reason
    assert abs(result.impact.x_mm - local_center[0]) < 5.
    assert abs(result.impact.y_mm - local_center[1]) < 5.
    assert result.quality.accepted_synthetic_geometry is True
    assert result.quality.physically_validated is False
    assert result.quality.position_uncertainty_mm is None
    assert report.audit.accepted_synthetic == 1
    assert report.audit.physical_contact_established is False
    handoff = prepare_offline_impact_handoff(
        capture, report, max_sensor_gap_ns=100, max_host_gap_ns=1000,
    )
    assert handoff.temporal.spacing.accepted is True
    assert handoff.impact.accepted_for_offline_analysis is True
    assert handoff.impact.frame_index == 2
    assert handoff.impact.shot_id == "rendered-ball"
    assert handoff.impact.session_id == "synthetic"
    assert abs(handoff.impact.x_mm - local_center[0]) < 5.
    assert abs(handoff.impact.y_mm - local_center[1]) < 5.
    assert handoff.impact.physically_validated is False
    assert handoff.impact.position_uncertainty_mm is None

    # The same valid synthetic geometry must never bypass a timing failure.
    bad_timing = prepare_offline_impact_handoff(
        capture, report, max_sensor_gap_ns=99, max_host_gap_ns=1000,
    )
    assert bad_timing.temporal.spacing.accepted is False
    assert bad_timing.impact.accepted_for_offline_analysis is False
    assert bad_timing.impact.frame_index is None
    assert bad_timing.impact.x_mm is None
    assert bad_timing.impact.y_mm is None
    assert bad_timing.impact.physically_validated is False
