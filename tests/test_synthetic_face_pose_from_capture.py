"""Synthetic face pose bridge reuses existing extraction and PnP solver."""

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.synthetic_face_pose_from_capture import estimate_capture_synthetic_face_pose
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def fixture():
    image = np.zeros((240, 320), dtype=np.uint8)
    cv.rectangle(image, (100, 80), (180, 130), 220, -1)
    capture = TriggeredCapture(
        (CameraFrame(image, 100, 1000, 100, 1.0),),
        0, 1000, shot_id="shot", session_id="session",
    )
    calibration = CheckerboardCalibration(
        (320, 240),
        np.array([[260., 0., 160.], [0., 260., 120.], [0., 0., 1.]]),
        np.zeros(5), 0., (),
    )
    landmarks = np.array([[-40., -25.], [40., -25.], [40., 25.], [-40., 25.]])
    return capture, calibration, landmarks


def test_image_provenance_reaches_existing_pose_solver(monkeypatch):
    capture, calibration, landmarks = fixture()
    calls = []

    def spy(_calibration, _landmarks, pixels, **kwargs):
        calls.append((np.array(pixels, copy=True), kwargs))
        return "pose sentinel"

    monkeypatch.setattr(
        "openflight.camera.synthetic_face_pose_from_capture.estimate_synthetic_face_pose",
        spy,
    )
    result = estimate_capture_synthetic_face_pose(
        calibration, capture, 0, landmarks,
        max_rms_px=0.5, min_margin_px=0.1,
    )
    assert result.pose == "pose sentinel"
    assert result.observation.shot_id == "shot"
    assert result.observation.session_id == "session"
    assert result.observation.frame_index == 0
    np.testing.assert_array_equal(
        calls[0][0], [[100, 130], [180, 130], [180, 80], [100, 80]],
    )
    assert calls[0][1]["image_size"] == (320, 240)


def test_ambiguous_or_missing_image_never_calls_pose_solver(monkeypatch):
    capture, calibration, landmarks = fixture()
    image = np.zeros((240, 320), dtype=np.uint8)
    calls = []

    def spy(*_args, **_kwargs):
        calls.append(True)
        raise AssertionError("pose solver should not run")

    monkeypatch.setattr(
        "openflight.camera.synthetic_face_pose_from_capture.estimate_synthetic_face_pose",
        spy,
    )
    blank = TriggeredCapture(
        (CameraFrame(image, 100, 1000, 100, 1.0),),
        0, 1000, shot_id="shot", session_id="session",
    )
    with pytest.raises(ValueError, match="exactly one"):
        estimate_capture_synthetic_face_pose(
            calibration, blank, 0, landmarks, max_rms_px=0.5, min_margin_px=0.1,
        )
    assert not calls


def test_pose_rejection_propagates_without_fabricated_result(monkeypatch):
    capture, calibration, landmarks = fixture()

    def reject(*_args, **_kwargs):
        raise ValueError("ambiguous planar face pose")

    monkeypatch.setattr(
        "openflight.camera.synthetic_face_pose_from_capture.estimate_synthetic_face_pose",
        reject,
    )
    with pytest.raises(ValueError, match="ambiguous"):
        estimate_capture_synthetic_face_pose(
            calibration, capture, 0, landmarks, max_rms_px=0.5, min_margin_px=0.1,
        )


def test_invalid_frame_rejected_before_pose():
    capture, calibration, landmarks = fixture()
    with pytest.raises(ValueError, match="frame index"):
        estimate_capture_synthetic_face_pose(
            calibration, capture, 2, landmarks, max_rms_px=0.5, min_margin_px=0.1,
        )
