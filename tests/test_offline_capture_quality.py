"""Capture-wide offline preflight with synthetic arrays only."""
from dataclasses import replace

import numpy as np
import pytest

from openflight.camera.offline_capture_quality import require_usable_offline_capture
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def _capture():
    image = np.tile(np.array([20, 60, 120, 200], dtype=np.uint8), (4, 1))
    return TriggeredCapture(
        frames=(
            CameraFrame(image.copy(), 100, 1000, 100, 1.),
            CameraFrame(image.copy(), 200, 1100, 100, 1.),
        ),
        pre_trigger_count=1,
        trigger_host_timestamp_ns=1050,
        shot_id="shot-1",
        session_id="session-1",
    )


def test_valid_capture_reports_per_frame_diagnostics_and_cadence():
    result = require_usable_offline_capture(_capture())
    assert result.frame_count == 2
    assert len(result.frame_quality) == 2
    assert result.min_sensor_interval_ns == 100
    assert result.max_sensor_interval_ns == 100


@pytest.mark.parametrize("change,reason", [
    ({"shot_id": ""}, "shot identity"),
    ({"session_id": ""}, "session identity"),
    ({"pre_trigger_count": 3}, "pre-trigger"),
    ({"frames": ()}, "frame count"),
])
def test_invalid_capture_metadata_fails_closed(change, reason):
    with pytest.raises(ValueError, match=reason):
        require_usable_offline_capture(replace(_capture(), **change))


@pytest.mark.parametrize("sensor,host,reason", [
    (100, 1100, "sensor timestamp"),
    (201, 1000, "host timestamp"),
    (5000, 1100, "sensor timestamp"),
    (200, 9000, "host timestamp"),
])
def test_discontinuous_timestamps_rejected(sensor, host, reason):
    capture = _capture()
    second = replace(capture.frames[1], sensor_timestamp_ns=sensor, host_timestamp_ns=host)
    with pytest.raises(ValueError, match=reason):
        require_usable_offline_capture(
            replace(capture, frames=(capture.frames[0], second)),
            max_sensor_gap_ns=1000,
            max_host_gap_ns=1000,
        )


def test_mixed_dimensions_and_bad_exposure_rejected():
    capture = _capture()
    different = replace(capture.frames[1], image=np.tile(
        np.array([20, 60, 120, 200, 220], dtype=np.uint8), (4, 1)
    ))
    with pytest.raises(ValueError, match="dimensions changed"):
        require_usable_offline_capture(replace(capture, frames=(capture.frames[0], different)))
    dark = replace(capture.frames[1], image=np.zeros((4, 4), dtype=np.uint8))
    with pytest.raises(ValueError, match="underexposed"):
        require_usable_offline_capture(replace(capture, frames=(capture.frames[0], dark)))


def test_capture_bounds_and_single_frame():
    capture = _capture()
    with pytest.raises(ValueError, match="frame count"):
        require_usable_offline_capture(capture, max_frames=1)
    single = replace(capture, frames=capture.frames[:1])
    result = require_usable_offline_capture(single)
    assert result.min_sensor_interval_ns is None


@pytest.mark.parametrize("options", [
    {"max_frames": 0},
    {"max_sensor_gap_ns": True},
    {"max_host_gap_ns": -1},
])
def test_invalid_limits_rejected(options):
    with pytest.raises(ValueError, match="positive integer"):
        require_usable_offline_capture(_capture(), **options)
