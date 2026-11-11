"""Actual synthetic frames through the complete image-to-UI pipeline."""

import json

import cv2 as cv
import numpy as np

from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.offline_motion_analysis_pipeline import (
    analyze_offline_synthetic_motion,
)
from openflight.camera.synthetic_face_polygon import SyntheticFacePolygon
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def run(centres):
    images = []
    for centre in centres:
        image = np.zeros((240, 320), dtype=np.uint8)
        cv.rectangle(image, (35, 110), (115, 190), 230, -1)
        if centre is not None:
            cv.circle(image, (centre, 150), 20, 220, -1)
        images.append(image)
    capture = TriggeredCapture(
        tuple(CameraFrame(image, (i + 1) * 100, (i + 1) * 1000, 100, 1.)
              for i, image in enumerate(images)),
        1, 1500, shot_id="shot", session_id="session",
    )
    calibration = CheckerboardCalibration(
        (320, 240),
        np.array([[260., 0., 160.], [0., 260., 120.], [0., 0., 1.]]),
        np.zeros(5), 0., (),
    )
    landmarks = np.array([[-20., -10.], [20., -10.], [20., 10.], [-20., 10.]])
    return analyze_offline_synthetic_motion(
        calibration, capture, tuple(range(len(images))),
        landmarks, SyntheticFacePolygon(landmarks),
        ball_radius_mm=21.35, max_ball_residual_rad=0.02,
        max_face_rms_px=0.5, min_face_margin_px=0.1,
        contact_tolerance_mm=0.01,
        max_sensor_gap_ns=100, max_host_gap_ns=1000,
    )


def test_full_synthetic_image_to_ui_evidence():
    result = run([240, 200, 160, 200, 240])
    assert result.motion.trend.has_observed_approach_and_separation
    assert result.ui_payload["closest_observed_frame_index"] == 2
    assert len(result.ui_payload["proximity_samples"]) == 5
    assert result.ui_payload["physical_contact_confirmed"] is False
    assert result.ui_payload["impact_frame_index"] is None
    assert result.ui_payload["impact_x_mm"] is None
    assert json.loads(json.dumps(result.ui_payload)) == result.ui_payload


def test_incomplete_sequence_does_not_export_false_motion():
    result = run([240, None, 160])
    assert result.ui_payload["closest_observed_frame_index"] is None
    assert not result.ui_payload["has_observed_approach_and_separation"]
    assert result.ui_payload["rejected_frames"]
    assert result.ui_payload["proximity_samples"] == []
    assert result.physical_contact_confirmed is False
