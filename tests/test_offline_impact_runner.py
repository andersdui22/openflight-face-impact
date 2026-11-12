"""Unmocked offline capture to Socket.IO payload integration regression."""

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.offline_capture_preflight import preflight_offline_capture
from openflight.camera.offline_impact_runner import analyze_and_publish_offline_capture
from openflight.camera.synthetic_face_polygon import SyntheticFacePolygon
from openflight.camera.synthetic_frame_candidates import SyntheticFrameCandidate
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def _fixture():
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
        1, 1500, shot_id="offline-shot", session_id="offline-session",
    )
    landmarks = np.array([[-20., -10.], [20., -10.],
                          [20., 10.], [-20., 10.]])
    return calibration, capture, landmarks


def _run(emit, recipient="ui-client", preflight=None):
    calibration, capture, landmarks = _fixture()
    return analyze_and_publish_offline_capture(
        calibration, capture,
        (SyntheticFrameCandidate(0, landmarks),
         SyntheticFrameCandidate(1, np.zeros((4, 2)))),
        landmarks, SyntheticFacePolygon(landmarks),
        ball_radius_mm=21.35,
        max_ball_residual_rad=0.02,
        max_face_rms_px=0.5,
        min_face_margin_px=0.1,
        contact_tolerance_mm=0.01,
        threshold=100,
        min_area_px=100.,
        ball_border_margin_px=2.,
        min_circularity=0.8,
        max_sensor_gap_ns=100,
        max_host_gap_ns=1000,
        emit=emit,
        recipient=recipient,
        preflight=preflight,
    )


def test_real_offline_pipeline_emits_rejected_synthetic_evidence():
    messages = []
    result = _run(
        lambda event, payload, **kw: messages.append((event, payload, kw))
    )
    assert result["source"] == "offline_synthetic_analysis"
    assert result["shot_id"] == "offline-shot"
    assert result["session_id"] == "offline-session"
    assert result["accepted"] is False
    assert result["physically_validated"] is False
    assert "x_mm" not in result
    assert "y_mm" not in result
    assert messages == [("offline_impact_evidence", result, {"to": "ui-client"})]


def test_missing_recipient_aborts_before_emission():
    messages = []
    with pytest.raises(ValueError, match="explicit recipient"):
        _run(lambda *args, **kwargs: messages.append((args, kwargs)), recipient="")
    assert messages == []

def test_opt_in_preflight_rejects_unchecked_capture_before_publication():
    messages = []
    calibration, capture, landmarks = _fixture()
    del calibration, landmarks
    # Blank synthetic frames in legacy fixtures are intentionally not quality-approved.
    with pytest.raises(ValueError, match="underexposed"):
        preflight_offline_capture(capture)
    with pytest.raises(ValueError, match="typed offline preflight"):
        _run(lambda *args, **kwargs: messages.append((args, kwargs)),
             preflight="untrusted")
    assert messages == []


def test_opt_in_preflight_checks_capture_identity_before_assessment(monkeypatch):
    from openflight.camera import offline_impact_runner as runner
    calibration, capture, landmarks = _fixture()
    del calibration, landmarks
    image = np.tile(np.array([20, 60, 120, 200], dtype=np.uint8), (240, 80))
    checked = TriggeredCapture(
        (CameraFrame(image.copy(), 100, 1000, 100, 1.),
         CameraFrame(image.copy(), 200, 2000, 100, 1.)),
        1, 1500, shot_id="checked-shot", session_id="checked-session",
    )
    evidence = preflight_offline_capture(checked)
    # Mutate the originally validated capture to prove early fail-closed.
    checked.frames[0].image[0, 0] = 22
    called = []
    monkeypatch.setattr(runner, "assess_offline_capture_batch",
                        lambda *args, **kwargs: called.append(True))
    with pytest.raises(ValueError, match="differs from offline preflight"):
        runner.analyze_and_publish_offline_capture(
            None, checked, (), None, None,
            ball_radius_mm=21.35, max_ball_residual_rad=0.03,
            max_face_rms_px=1., min_face_margin_px=0.1,
            contact_tolerance_mm=5., threshold=100,
            min_area_px=100., ball_border_margin_px=2.,
            max_sensor_gap_ns=100, max_host_gap_ns=1000,
            emit=lambda *args, **kwargs: called.append(True),
            recipient="test-client", preflight=evidence,
        )
    assert called == []
