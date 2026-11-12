"""Server-owned synthetic ball and fiducial rasters for offline review."""

from collections.abc import Callable

import cv2 as cv
import numpy as np

from .checkerboard_calibration import CheckerboardCalibration
from .offline_capture_preflight import preflight_offline_capture
from .offline_marker_runner import analyze_marker_observed_offline_capture
from .synthetic_face_polygon import SyntheticFacePolygon
from .triggered_buffer import CameraFrame, TriggeredCapture


def publish_synthetic_offline_impact_demo(  # pylint: disable=no-member
    case_id: str, emit: Callable, *, recipient: str,
) -> dict | None:
    """Publish one fixed synthetic case through the actual offline runner."""
    if case_id not in ("contact", "missing-ball"):
        return None

    width, height = 640, 400
    radius = 21.35
    calibration = CheckerboardCalibration(
        (width, height),
        np.array([[530., 0., 315.], [0., 525., 198.], [0., 0., 1.]]),
        np.array([-0.24, 0.08, 0.002, -0.003, 0.01]), 0., (),
    )
    landmarks = np.array([
        [-44., -19.], [42., -17.], [36., 22.], [-35., 18.], [8., 12.], [-9., -4.],
    ])
    polygon = SyntheticFacePolygon(np.array([[-45., -25.], [45., -25.], [45., 25.], [-45., 25.]]))
    rotation = cv.Rodrigues(np.array([0.29, -0.32, 0.2]))[0] @ np.diag([1., -1., -1.])
    translation = np.array([64., -22., 420.])

    def project(points):
        pixels, _ = cv.projectPoints(
            points, np.zeros(3), np.zeros(3), calibration.camera_matrix, calibration.distortion,
        )
        return pixels.reshape(-1, 2)

    face_points = np.column_stack((landmarks, np.zeros(len(landmarks))))
    reference_pixels = project(face_points @ rotation.T + translation)
    marker_image = np.zeros((height, width), dtype=np.uint8)
    for x, y in np.rint(reference_pixels).astype(int):
        cv.circle(marker_image, (int(x), int(y)), 4, 245, -1)

    # Keep the synthetic background below the ball threshold, with enough
    # contrast to pass the same quality checks in both replay cases.
    before = np.tile(np.linspace(16, 64, width, dtype=np.uint8), (height, 1))
    after = before.copy()
    if case_id == "contact":
        centre = rotation @ np.array([12., 5., radius]) + translation
        direction = centre / np.linalg.norm(centre)
        across = np.cross(direction, [0., 1., 0.])
        across /= np.linalg.norm(across)
        up = np.cross(direction, across)
        ratio = radius / np.linalg.norm(centre)
        angles = np.linspace(0., 2. * np.pi, 360, endpoint=False)
        # Rays tangent to the known sphere define its apparent rim.
        rim = centre * (1. - ratio**2) + radius * np.sqrt(1. - ratio**2) * (
            np.cos(angles)[:, None] * across + np.sin(angles)[:, None] * up
        )
        cv.fillPoly(after, [np.rint(project(rim)).astype(np.int32)], 220)

    capture = TriggeredCapture(
        (CameraFrame(before, 8_000_000, 16_000_000, 1_000, 1.),
         CameraFrame(after, 16_000_000, 24_000_000, 1_000, 1.)),
        1, 20_000_000, shot_id=f"synthetic-{case_id}", session_id="synthetic-offline-demo-v1",
    )
    timing = {"max_sensor_gap_ns": 8_000_000, "max_host_gap_ns": 8_000_000}
    return analyze_marker_observed_offline_capture(
        calibration, capture, {0: marker_image, 1: marker_image},
        reference_pixels, landmarks, polygon,
        max_marker_distance_px=2., ball_radius_mm=radius, max_ball_residual_rad=0.03,
        max_face_rms_px=1., min_face_margin_px=0.1, contact_tolerance_mm=5., threshold=100,
        min_area_px=300., ball_border_margin_px=2., min_circularity=0.8,
        preflight=preflight_offline_capture(capture, **timing),
        emit=emit, recipient=recipient, **timing,
    )
