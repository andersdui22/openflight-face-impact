"""Marker raster -> labelled pixels -> offline runner boundary tests."""

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.offline_marker_runner import analyze_marker_observed_offline_capture
from openflight.camera.synthetic_face_polygon import SyntheticFacePolygon
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def _inputs():
    image = np.zeros((240, 320), dtype=np.uint8)
    for x, y in ((40, 45), (250, 50), (45, 190), (245, 185)):
        cv.circle(image, (x, y), 5, 255, -1)
    capture = TriggeredCapture(
        (CameraFrame(np.zeros_like(image), 100, 1000, 100, 1.),
         CameraFrame(np.zeros_like(image), 200, 2000, 100, 1.)),
        1, 1500, shot_id="marker-shot", session_id="marker-session",
    )
    calibration = CheckerboardCalibration(
        (320, 240), np.array([[260., 0., 160.], [0., 260., 120.], [0., 0., 1.]]),
        np.zeros(5), 0., (),
    )
    landmarks = np.array([
        [-20., -10.], [20., -10.], [20., 10.], [-20., 10.],
    ])
    reference = np.array([
        [45., 190.], [40., 45.], [245., 185.], [250., 50.],
    ])
    return image, capture, calibration, landmarks, reference


def _run(images, *, reference=None):
    image, capture, calibration, landmarks, default_reference = _inputs()
    del image
    emitted = []
    result = analyze_marker_observed_offline_capture(
        calibration, capture, images,
        default_reference if reference is None else reference,
        landmarks, SyntheticFacePolygon(landmarks),
        max_marker_distance_px=6.,
        ball_radius_mm=21.35,
        max_ball_residual_rad=0.03,
        max_face_rms_px=1.,
        min_face_margin_px=0.1,
        contact_tolerance_mm=5.,
        threshold=100,
        min_area_px=100.,
        ball_border_margin_px=2.,
        max_sensor_gap_ns=100,
        max_host_gap_ns=1000,
        emit=lambda event, body, **kwargs: emitted.append((event, body, kwargs)),
        recipient="marker-client",
    )
    return result, emitted


def test_raster_observed_markers_reach_actual_offline_runner_as_rejected_evidence():
    image, *_ = _inputs()
    payload, events = _run({0: image, 1: image.copy()})
    assert payload["source"] == "offline_synthetic_analysis"
    assert payload["shot_id"] == "marker-shot"
    assert payload["accepted"] is False  # Blank ball images: no invented contact
    assert "x_mm" not in payload
    assert events == [("offline_impact_evidence", payload, {"to": "marker-client"})]


def test_missing_fiducial_aborts_without_emitting():
    image, *_ = _inputs()
    cv.circle(image, (40, 45), 6, 0, -1)
    with pytest.raises(ValueError, match="unexpected blob count"):
        _run({0: image})


def test_untrusted_reference_displacement_aborts_without_emitting():
    image, *_ = _inputs()
    with pytest.raises(ValueError, match="distance budget"):
        _run({0: image}, reference=np.zeros((4, 2)))


@pytest.mark.parametrize("reference", [
    np.empty((0, 2)),
    np.zeros((4, 3)),
    np.array([[0., 0.], [1., 1.], [float("nan"), 2.], [3., 3.]]),
    np.zeros((9, 2)),
])
def test_invalid_reference_shape_or_values_rejected(reference):
    image, *_ = _inputs()
    with pytest.raises(ValueError, match="3..8 finite labelled"):
        _run({0: image}, reference=reference)


def test_invalid_frame_index_rejected_before_sorting_or_emission():
    image, *_ = _inputs()
    with pytest.raises(ValueError, match="frame indices must be integers"):
        _run({"bad": image})


def test_partial_marker_batch_failure_does_not_publish_previous_frame():
    image, *_ = _inputs()
    missing = image.copy()
    cv.circle(missing, (40, 45), 6, 0, -1)
    with pytest.raises(ValueError, match="unexpected blob count"):
        _run({0: image, 1: missing})


def test_no_marker_observations_rejected():
    with pytest.raises(ValueError, match="nonempty frame mapping"):
        _run({})


def test_out_of_range_marker_frame_rejected():
    image, *_ = _inputs()
    with pytest.raises(ValueError, match="outside capture"):
        _run({2: image})


def test_marker_image_shape_must_match_capture_frame():
    image, *_ = _inputs()
    with pytest.raises(ValueError, match="dimensions differ"):
        _run({0: np.zeros((100, 100), dtype=np.uint8)})


def test_marker_input_images_are_not_modified_by_extraction():
    image, *_ = _inputs()
    before = image.copy()
    _run({0: image})
    np.testing.assert_array_equal(image, before)


def test_extra_plausible_marker_rejects_entire_raster_batch():
    image, *_ = _inputs()
    ambiguous = image.copy()
    cv.circle(ambiguous, (110, 120), 5, 255, -1)
    with pytest.raises(ValueError, match="unexpected blob count"):
        _run({0: image, 1: ambiguous})
