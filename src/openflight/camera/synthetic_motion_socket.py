"""Explicit synthetic motion fixture for Socket.IO diagnostics demo.

This is not a camera stream and must not be described as a measured shot.
"""

from __future__ import annotations

import cv2 as cv
import numpy as np

from .checkerboard_calibration import CheckerboardCalibration
from .offline_motion_analysis_pipeline import analyze_offline_synthetic_motion
from .synthetic_face_polygon import SyntheticFacePolygon
from .triggered_buffer import CameraFrame, TriggeredCapture


def synthetic_motion_demo_response() -> dict:
    """Compute UI diagnostics from generated frames using the real pipeline."""
    images = []
    for centre in (240, 200, 160, 200, 240):
        image = np.zeros((240, 320), dtype=np.uint8)
        cv.rectangle(image, (35, 110), (115, 190), 230, -1)
        cv.circle(image, (centre, 150), 20, 220, -1)
        images.append(image)
    capture = TriggeredCapture(
        tuple(CameraFrame(image, (i + 1) * 100, (i + 1) * 1000, 100, 1.)
              for i, image in enumerate(images)),
        1, 1500, shot_id="synthetic-motion-demo",
        session_id="synthetic-fixture",
    )
    calibration = CheckerboardCalibration(
        (320, 240),
        np.array([[260., 0., 160.], [0., 260., 120.], [0., 0., 1.]]),
        np.zeros(5), 0., (),
    )
    landmarks = np.array([[-20., -10.], [20., -10.], [20., 10.], [-20., 10.]])
    analysis = analyze_offline_synthetic_motion(
        calibration, capture, tuple(range(len(images))),
        landmarks, SyntheticFacePolygon(landmarks),
        ball_radius_mm=21.35, max_ball_residual_rad=0.02,
        max_face_rms_px=0.5, min_face_margin_px=0.1,
        contact_tolerance_mm=0.01,
        max_sensor_gap_ns=100, max_host_gap_ns=1000,
    )
    return analysis.ui_payload
