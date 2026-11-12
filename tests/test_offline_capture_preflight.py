"""Synthetic offline preflight provenance and tamper detection tests."""
from dataclasses import replace

import numpy as np
import pytest

from openflight.camera.offline_capture_preflight import (
    preflight_offline_capture,
    require_matching_preflight,
)
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def _capture():
    image = np.tile(np.array([20, 60, 120, 200], dtype=np.uint8), (4, 1))
    return TriggeredCapture(
        frames=(CameraFrame(image, 100, 1000, 100, 1.),
                CameraFrame(image.copy(), 200, 1100, 100, 1.)),
        pre_trigger_count=1,
        trigger_host_timestamp_ns=1050,
        shot_id="preflight-shot",
        session_id="preflight-session",
    )


def test_preflight_binds_valid_capture_and_reports_quality():
    capture = _capture()
    evidence = preflight_offline_capture(capture)
    assert len(evidence.source_fingerprint) == 64
    assert require_matching_preflight(capture, evidence).frame_count == 2


def test_changed_frame_bytes_rejected():
    capture = _capture()
    evidence = preflight_offline_capture(capture)
    capture.frames[0].image[0, 0] = 21
    with pytest.raises(ValueError, match="differs"):
        require_matching_preflight(capture, evidence)


@pytest.mark.parametrize("change", [
    {"shot_id": "different"},
    {"session_id": "different"},
    {"trigger_host_timestamp_ns": 999},
])
def test_changed_capture_identity_rejected(change):
    capture = _capture()
    evidence = preflight_offline_capture(capture)
    with pytest.raises(ValueError, match="differs"):
        require_matching_preflight(replace(capture, **change), evidence)


def test_changed_frame_timing_rejected():
    capture = _capture()
    evidence = preflight_offline_capture(capture)
    new_frame = replace(capture.frames[1], sensor_timestamp_ns=201)
    with pytest.raises(ValueError, match="differs"):
        require_matching_preflight(
            replace(capture, frames=(capture.frames[0], new_frame)), evidence
        )


def test_host_arrival_alias_changes_capture_provenance():
    capture = _capture()
    evidence = preflight_offline_capture(capture)
    frame = replace(capture.frames[0], sensor_timestamp_is_host_alias=True)
    aliased = replace(capture, frames=(frame, capture.frames[1]))
    with pytest.raises(ValueError, match="differs"):
        require_matching_preflight(aliased, evidence)


def test_invalid_capture_cannot_generate_preflight():
    capture = _capture()
    capture.frames[1].image[:] = 0
    with pytest.raises(ValueError, match="underexposed"):
        preflight_offline_capture(capture)


def test_invalid_preflight_object_rejected():
    with pytest.raises(ValueError, match="typed"):
        require_matching_preflight(_capture(), None)
