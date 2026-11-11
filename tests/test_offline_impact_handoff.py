"""Real offline image -> batch -> timing -> export rejection integration."""

from dataclasses import replace

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.offline_capture_batch import assess_offline_capture_batch
from openflight.camera.offline_impact_handoff import prepare_offline_impact_handoff
from openflight.camera.synthetic_face_polygon import SyntheticFacePolygon
from openflight.camera.synthetic_frame_candidates import SyntheticFrameCandidate
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def fixture():
    calibration = CheckerboardCalibration(
        (320, 240),
        np.array([[260., 0., 160.], [0., 260., 120.], [0., 0., 1.]]),
        np.zeros(5), 0., (),
    )
    blank = np.zeros((240, 320), dtype=np.uint8)
    disk = blank.copy()
    cv.circle(disk, (160, 120), 20, 220, -1)
    capture = TriggeredCapture(
        (CameraFrame(blank.copy(), 100, 1000, 100, 1.),
         CameraFrame(disk, 200, 2000, 100, 1.)),
        1, 1500, shot_id="shot", session_id="session",
    )
    landmarks = np.array([[-20., -10.], [20., -10.], [20., 10.], [-20., 10.]])
    batch = assess_offline_capture_batch(
        calibration, capture,
        (SyntheticFrameCandidate(0, landmarks),
         SyntheticFrameCandidate(1, np.zeros((4, 2)))),
        landmarks, SyntheticFacePolygon(landmarks),
        ball_radius_mm=21.35, max_ball_residual_rad=0.02,
        max_face_rms_px=0.5, min_face_margin_px=0.1,
        contact_tolerance_mm=0.01, threshold=100,
        min_area_px=100., ball_border_margin_px=2.,
        min_circularity=0.8,
    )
    return capture, batch


def test_real_image_batch_through_quality_and_export_fails_closed():
    capture, batch = fixture()
    result = prepare_offline_impact_handoff(
        capture, batch, max_sensor_gap_ns=100, max_host_gap_ns=1000,
    )
    assert batch.audit.total == 2
    assert batch.audit.rejected_invalid_geometry == 2
    assert result.temporal.spacing.accepted is True
    assert result.impact.shot_id == "shot"
    assert result.impact.session_id == "session"
    assert result.impact.accepted_for_offline_analysis is False
    assert result.impact.frame_index is None
    assert result.impact.x_mm is None and result.impact.y_mm is None
    assert result.impact.physically_validated is False


def test_temporal_gap_rejects_without_leaking_coordinates():
    capture, batch = fixture()
    result = prepare_offline_impact_handoff(
        capture, batch, max_sensor_gap_ns=99, max_host_gap_ns=1000,
    )
    assert result.temporal.spacing.accepted is False
    assert result.impact.frame_index is None
    assert result.impact.x_mm is None


def test_tampered_audit_is_rejected_before_export():
    capture, batch = fixture()
    tampered = replace(batch, audit=replace(batch.audit, total=3))
    with pytest.raises(ValueError, match="audit does not match"):
        prepare_offline_impact_handoff(
            capture, tampered, max_sensor_gap_ns=100,
            max_host_gap_ns=1000,
        )


def test_cross_capture_handoff_rejected_even_with_same_frame_indices():
    capture, batch = fixture()
    other = replace(capture, shot_id="different-shot")
    with pytest.raises(ValueError, match="does not belong"):
        prepare_offline_impact_handoff(
            other, batch, max_sensor_gap_ns=100, max_host_gap_ns=1000,
        )


def test_modified_capture_frame_bytes_rejected():
    capture, batch = fixture()
    altered = capture.frames[1].image.copy()
    altered[0, 0] = 255
    other = replace(capture, frames=(capture.frames[0], replace(
        capture.frames[1], image=altered,
    )))
    with pytest.raises(ValueError, match="does not belong"):
        prepare_offline_impact_handoff(
            other, batch, max_sensor_gap_ns=100, max_host_gap_ns=1000,
        )


def test_modified_capture_timing_rejected():
    capture, batch = fixture()
    other = replace(capture, frames=(capture.frames[0], replace(
        capture.frames[1], sensor_timestamp_ns=201,
    )))
    with pytest.raises(ValueError, match="does not belong"):
        prepare_offline_impact_handoff(
            other, batch, max_sensor_gap_ns=100, max_host_gap_ns=1000,
        )


def test_wrong_batch_type_rejected():
    capture, _ = fixture()
    with pytest.raises(ValueError, match="typed offline"):
        prepare_offline_impact_handoff(
            capture, None, max_sensor_gap_ns=100,
            max_host_gap_ns=1000,
        )
