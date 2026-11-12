"""Tests for image-derived synthetic face to impact pipeline adapter."""

from unittest.mock import patch

import cv2 as cv
import numpy as np

from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.synthetic_face_polygon import SyntheticFacePolygon
import pytest

from openflight.camera.offline_image_impact_pipeline import (
    assess_image_derived_synthetic_impact,
)
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def capture(images):
    return TriggeredCapture(
        tuple(CameraFrame(image, 100 * (i + 1), 1000 * (i + 1), 100, 1.)
              for i, image in enumerate(images)),
        1, 1500, shot_id="shot", session_id="session",
    )


def run_pipeline(images, indices):
    return assess_image_derived_synthetic_impact(
        None, capture(images), indices, None, None,
        image_size=(240, 160),
        ball_radius_mm=21.35, max_ball_residual_rad=0.02,
        max_face_rms_px=0.5, min_face_margin_px=0.1,
        contact_tolerance_mm=0.01, ball_threshold=180,
        ball_min_area_px=100., ball_border_margin_px=2.,
    )


def test_no_detected_face_does_not_invoke_impact_assessment():
    blank = np.zeros((160, 240), dtype=np.uint8)
    with patch(
        "openflight.camera.offline_image_impact_pipeline.assess_offline_capture_batch",
    ) as assess:
        result = run_pipeline([blank, blank], (0, 1))
    assert result.assessment is None
    assert len(result.observations.rejected) == 2
    assert result.physical_contact_confirmed is False
    assess.assert_not_called()


def test_observed_face_candidates_are_forwarded_without_guessing_contact():
    image = np.zeros((160, 240), dtype=np.uint8)
    image[45:115, 60:170] = 230
    with patch(
        "openflight.camera.offline_image_impact_pipeline.assess_offline_capture_batch",
    ) as assess:
        result = run_pipeline([image, np.zeros_like(image)], (0, 1))
    assert len(result.observations.candidates) == 1
    assert result.observations.candidates[0].frame_index == 0
    assert len(result.observations.rejected) == 1
    assert result.assessment is assess.return_value
    assert assess.call_args.args[2] == result.observations.candidates
    assert result.physical_contact_confirmed is False


@pytest.mark.parametrize("indices", [(), (0, 0), (3,), (True,)])
def test_invalid_frame_selection_fails_before_assessment(indices):
    image = np.zeros((160, 240), dtype=np.uint8)
    with pytest.raises(ValueError, match="frame indices"):
        run_pipeline([image, image], indices)


def test_real_geometry_pipeline_rejects_mixed_ball_and_face_scene():
    """One grayscale mask cannot disambiguate a bright ball and bright face."""
    image = np.zeros((240, 320), dtype=np.uint8)
    cv.rectangle(image, (35, 40), (115, 95), 230, -1)
    cv.circle(image, (240, 150), 20, 220, -1)
    calibration = CheckerboardCalibration(
        (320, 240),
        np.array([[260., 0., 160.], [0., 260., 120.], [0., 0., 1.]]),
        np.zeros(5), 0., (),
    )
    landmarks = np.array([[-20., -10.], [20., -10.], [20., 10.], [-20., 10.]])
    result = assess_image_derived_synthetic_impact(
        calibration, capture([image, image.copy()]), (0, 1),
        landmarks, SyntheticFacePolygon(landmarks),
        image_size=(320, 240), ball_radius_mm=21.35,
        max_ball_residual_rad=0.02, max_face_rms_px=0.5,
        min_face_margin_px=0.1, contact_tolerance_mm=0.01,
        ball_threshold=100, ball_min_area_px=100.,
        ball_border_margin_px=2.,
    )
    assert result.assessment is None
    assert len(result.observations.rejected) == 2
    assert all("exactly one" in reason for _, reason in result.observations.rejected)
    assert result.physical_contact_confirmed is False


def test_real_geometry_pipeline_rejects_ball_only_scene():
    image = np.zeros((240, 320), dtype=np.uint8)
    cv.circle(image, (160, 120), 20, 220, -1)
    calibration = CheckerboardCalibration(
        (320, 240),
        np.array([[260., 0., 160.], [0., 260., 120.], [0., 0., 1.]]),
        np.zeros(5), 0., (),
    )
    landmarks = np.array([[-20., -10.], [20., -10.], [20., 10.], [-20., 10.]])
    result = assess_image_derived_synthetic_impact(
        calibration, capture([image, image.copy()]), (0, 1),
        landmarks, SyntheticFacePolygon(landmarks),
        image_size=(320, 240), ball_radius_mm=21.35,
        max_ball_residual_rad=0.02, max_face_rms_px=0.5,
        min_face_margin_px=0.1, contact_tolerance_mm=0.01,
        ball_threshold=100, ball_min_area_px=100.,
        ball_border_margin_px=2.,
    )
    assert result.assessment is None
    assert len(result.observations.rejected) == 2
    assert result.physical_contact_confirmed is False
