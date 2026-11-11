"""Integration of image-space proximity and conservative motion trends."""

from dataclasses import replace

import cv2 as cv
import numpy as np

from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.offline_dual_object_motion import assess_offline_dual_object_motion
from openflight.camera.offline_dual_object_sequence import (
    assess_synthetic_dual_object_sequence,
)
from openflight.camera.synthetic_face_polygon import SyntheticFacePolygon
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def pipeline(centres):
    images = []
    for centre in centres:
        image = np.zeros((240, 320), dtype=np.uint8)
        cv.rectangle(image, (35, 40), (115, 95), 230, -1)
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
    sequence = assess_synthetic_dual_object_sequence(
        calibration, capture, tuple(range(len(images))),
        landmarks, SyntheticFacePolygon(landmarks),
        ball_radius_mm=21.35, max_ball_residual_rad=0.02,
        max_face_rms_px=0.5, min_face_margin_px=0.1,
        contact_tolerance_mm=0.01,
    )
    return capture, sequence


def test_real_sequence_through_motion_pipeline():
    capture, sequence = pipeline([240, 200, 160, 200, 240])
    result = assess_offline_dual_object_motion(
        capture, sequence, max_sensor_gap_ns=100, max_host_gap_ns=1000,
    )
    assert len(result.proximity.samples) == 5
    assert result.trend.has_observed_approach_and_separation is True
    assert result.trend.closest_frame_index == 2
    assert result.physical_contact_confirmed is False
    assert result.trend.physical_contact_confirmed is False


def test_monotonic_approach_does_not_infer_contact():
    capture, sequence = pipeline([240, 200, 160])
    result = assess_offline_dual_object_motion(
        capture, sequence, max_sensor_gap_ns=100, max_host_gap_ns=1000,
    )
    assert result.trend.closest_frame_index is None
    assert result.trend.has_observed_approach_and_separation is False


def test_missing_observation_blocks_motion_classification():
    capture, sequence = pipeline([240, 200, 160])
    sequence = replace(sequence, rejected=((1, "synthetic occlusion"),))
    result = assess_offline_dual_object_motion(
        capture, sequence, max_sensor_gap_ns=100, max_host_gap_ns=1000,
    )
    assert not result.proximity.samples
    assert result.trend.closest_frame_index is None
