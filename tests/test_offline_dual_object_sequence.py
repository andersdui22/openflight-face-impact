"""Real multi-frame synthetic dual-object processing without mocks."""

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.offline_dual_object_sequence import (
    assess_synthetic_dual_object_sequence,
)
from openflight.camera.synthetic_face_polygon import SyntheticFacePolygon
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def make_scene():
    image = np.zeros((240, 320), dtype=np.uint8)
    cv.rectangle(image, (35, 40), (115, 95), 230, -1)
    cv.circle(image, (240, 150), 20, 220, -1)
    return image


def run_sequence(images, indices):
    capture = TriggeredCapture(
        tuple(CameraFrame(image.copy(), 100 * (i + 1), 1000 * (i + 1), 100, 1.)
              for i, image in enumerate(images)),
        1, 1500, shot_id="shot", session_id="session",
    )
    calibration = CheckerboardCalibration(
        (320, 240),
        np.array([[260., 0., 160.], [0., 260., 120.], [0., 0., 1.]]),
        np.zeros(5), 0., (),
    )
    landmarks = np.array([[-20., -10.], [20., -10.], [20., 10.], [-20., 10.]])
    return assess_synthetic_dual_object_sequence(
        calibration, capture, indices, landmarks, SyntheticFacePolygon(landmarks),
        ball_radius_mm=21.35, max_ball_residual_rad=0.02,
        max_face_rms_px=0.5, min_face_margin_px=0.1,
        contact_tolerance_mm=0.01,
    )


def test_mixed_sequence_keeps_frame_identity_and_rejection_reasons():
    valid = make_scene()
    blank = np.zeros_like(valid)
    extra = valid.copy()
    cv.circle(extra, (160, 210), 10, 220, -1)
    result = run_sequence([blank, valid, extra], (0, 1, 2))
    assert tuple(index for index, _ in result.assessed) == (1,)
    assert tuple(index for index, _ in result.rejected) == (0, 2)
    assert result.assessed[0][1].observation.face.frame_index == 1
    assert result.assessed[0][1].quality.physically_validated is False
    assert result.physical_contact_confirmed is False
    assert len(result.source_capture_fingerprint) == 64


def test_multiple_detected_frames_do_not_select_contact():
    valid = make_scene()
    result = run_sequence([valid, valid.copy()], (0, 1))
    assert len(result.assessed) == 2
    assert not hasattr(result, "contact_frame_index")
    assert result.physical_contact_confirmed is False


@pytest.mark.parametrize("indices", [(), (0, 0), (-1,), (2,), (True,), [0]])
def test_invalid_frame_indices_rejected(indices):
    valid = make_scene()
    with pytest.raises(ValueError, match="frame indices"):
        run_sequence([valid, valid.copy()], indices)


def test_occluded_ball_rejected_without_affecting_other_frames():
    valid = make_scene()
    occluded = valid.copy()
    cv.circle(occluded, (240, 150), 7, 0, -1)
    result = run_sequence([occluded, valid], (0, 1))
    assert tuple(index for index, _ in result.rejected) == (0,)
    assert tuple(index for index, _ in result.assessed) == (1,)
