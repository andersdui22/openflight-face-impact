"""Synthetic temporal proximity evidence and conservative rejection tests."""

from dataclasses import replace

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.offline_capture_batch import capture_fingerprint
from openflight.camera.offline_dual_object_sequence import (
    assess_synthetic_dual_object_sequence,
)
from openflight.camera.offline_synthetic_proximity import assess_synthetic_proximity
from openflight.camera.synthetic_face_polygon import SyntheticFacePolygon
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def setup(ball_centres):
    images = []
    for centre in ball_centres:
        image = np.zeros((240, 320), dtype=np.uint8)
        cv.rectangle(image, (35, 110), (115, 190), 230, -1)
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


def assess(capture, sequence):
    return assess_synthetic_proximity(
        capture, sequence, max_sensor_gap_ns=100, max_host_gap_ns=1000,
    )


def test_unique_closest_frame_is_not_physical_contact():
    capture, sequence = setup([240, 200, 160])
    evidence = assess(capture, sequence)
    assert len(evidence.samples) == 3
    assert evidence.closest_frame_index == 2
    assert evidence.samples[0].separation_px > evidence.samples[1].separation_px
    assert evidence.samples[1].separation_px > evidence.samples[2].separation_px
    assert evidence.physical_contact_confirmed is False


def test_equal_distance_is_ambiguous():
    capture, sequence = setup([240, 240])
    evidence = assess(capture, sequence)
    assert evidence.closest_frame_index is None
    assert "ambiguous" in evidence.reason


def test_timing_gap_prevents_proximity_ranking():
    capture, sequence = setup([240, 200])
    modified = replace(capture, frames=(
        capture.frames[0], replace(capture.frames[1], sensor_timestamp_ns=500),
    ))
    modified_sequence = replace(
        sequence, source_capture_fingerprint=capture_fingerprint(modified),
    )
    evidence = assess(modified, modified_sequence)
    assert evidence.closest_frame_index is None
    assert "timing" in evidence.reason


def test_capture_mismatch_rejected():
    capture, sequence = setup([240, 200])
    with pytest.raises(ValueError, match="does not belong"):
        assess(replace(capture, shot_id="other"), sequence)
