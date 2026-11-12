"""Offline Gate 20/22 frame-derived contour and identity tests."""

from dataclasses import replace

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.capture_ball_contour import extract_capture_ball_contour
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def capture_with_disk():
    blank = np.zeros((100, 120), dtype=np.uint8)
    disk = blank.copy()
    cv.circle(disk, (60, 50), 15, 220, thickness=-1)
    frames = (
        CameraFrame(blank, 100, 1000, 100, 1.),
        CameraFrame(blank, 200, 2000, 100, 1.),
        CameraFrame(disk, 300, 3000, 100, 1.),
    )
    return TriggeredCapture(frames, 2, 2500, shot_id="shot-a", session_id="session-b")


def extract(capture, frame_index=2):
    return extract_capture_ball_contour(
        capture, frame_index, image_size=(120, 100),
        threshold=100, min_area_px=100., border_margin_px=2.,
        min_circularity=0.8,
    )


def test_selected_frame_yields_identity_bound_contour():
    capture = capture_with_disk()
    result = extract(capture)
    assert (result.shot_id, result.session_id, result.frame_index) == (
        "shot-a", "session-b", 2,
    )
    assert result.contour_px.shape[1] == 2
    assert result.contour_px.flags.writeable is False
    assert result.contour_px[:, 0].min() == pytest.approx(45.)
    capture.frames[2].image[:] = 0
    assert result.contour_px[:, 0].min() == pytest.approx(45.)


def test_wrong_frame_does_not_inherit_contour_from_other_frame():
    with pytest.raises(ValueError, match="exactly one"):
        extract(capture_with_disk(), frame_index=1)


def test_rejects_invalid_capture_identity_and_frame_shape():
    capture = capture_with_disk()
    with pytest.raises(ValueError, match="capture identity"):
        extract(replace(capture, shot_id=""))
    bad_frame = replace(capture.frames[2], image=np.zeros((20, 20), dtype=np.uint8))
    with pytest.raises(ValueError, match="grayscale dimensions"):
        extract(replace(capture, frames=capture.frames[:2] + (bad_frame,)))


def test_rejects_ambiguous_components_in_selected_frame():
    capture = capture_with_disk()
    cv.circle(capture.frames[2].image, (20, 20), 10, 220, thickness=-1)
    with pytest.raises(ValueError, match="exactly one"):
        extract(capture)
