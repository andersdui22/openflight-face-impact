"""Gate 22 offline timing-provenance checks without camera hardware."""

from dataclasses import replace

import numpy as np
import pytest

from openflight.camera.trigger_timing_quality import assess_trigger_timing
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def frame(sensor, host):
    return CameraFrame(np.zeros((2, 2), dtype=np.uint8), sensor, host, 100, 1.0)


@pytest.fixture
def capture():
    return TriggeredCapture(
        frames=(frame(100, 1000), frame(200, 2000), frame(300, 3000)),
        pre_trigger_count=2,
        trigger_host_timestamp_ns=2500,
        shot_id="shot-1",
        session_id="session-1",
    )


def test_valid_timing_reports_provenance_not_contact(capture):
    quality = assess_trigger_timing(capture)
    assert quality.valid
    assert quality.reason is None
    assert quality.frame_count == 3
    assert quality.trigger_between_host_frames


@pytest.mark.parametrize(("change", "reason"), [
    ({"pre_trigger_count": 0}, "missing pre-trigger"),
    ({"pre_trigger_count": 3}, "missing pre-trigger"),
    ({"trigger_host_timestamp_ns": 3500}, "not bracketed"),
    ({"trigger_host_timestamp_ns": -1}, "invalid host"),
    ({"shot_id": ""}, "missing capture identity"),
    ({"session_id": ""}, "missing capture identity"),
])
def test_invalid_capture_rejected(capture, change, reason):
    quality = assess_trigger_timing(replace(capture, **change))
    assert not quality.valid
    assert reason in quality.reason


def test_nonmonotonic_sensor_clock_rejected(capture):
    bad = replace(capture, frames=(frame(100, 1000), frame(100, 2000), frame(300, 3000)))
    quality = assess_trigger_timing(bad)
    assert not quality.valid
    assert "sensor_timestamp_ns" in quality.reason


def test_nonmonotonic_host_clock_rejected(capture):
    bad = replace(capture, frames=(frame(100, 1000), frame(200, 1000), frame(300, 3000)))
    quality = assess_trigger_timing(bad)
    assert not quality.valid
    assert "host_timestamp_ns" in quality.reason


def test_trigger_host_time_not_compared_to_sensor_clock(capture):
    shifted = replace(capture, frames=(
        frame(900_000, 1000), frame(900_100, 2000), frame(900_200, 3000),
    ))
    assert assess_trigger_timing(shifted).valid


def test_gate22_validates_actual_ring_buffer_capture():
    from openflight.camera.triggered_buffer import TriggeredFrameBuffer

    ring = TriggeredFrameBuffer(pre_trigger_frames=2, post_trigger_frames=1)
    ring.add_frame(frame(100, 1000))
    ring.add_frame(frame(200, 2000))
    assert ring.trigger(host_timestamp_ns=2500)
    ring.add_frame(frame(300, 3000))
    completed = ring.pop_capture()
    assert completed is not None
    assert completed.shot_id
    assert completed.session_id
    quality = assess_trigger_timing(completed)
    assert quality.valid
    assert quality.trigger_between_host_frames


def test_gate22_rejects_trigger_before_pre_frame_host_clock(capture):
    quality = assess_trigger_timing(
        replace(capture, trigger_host_timestamp_ns=1500)
    )
    assert not quality.valid
    assert "not bracketed" in quality.reason


@pytest.mark.parametrize("index", [0, 1, 2])
def test_gate22_candidate_frame_selection_requires_explicit_index(capture, index):
    from openflight.camera.trigger_timing_quality import validate_candidate_frame_index

    assert validate_candidate_frame_index(capture, index) == index


@pytest.mark.parametrize("index", [-1, 3, True, None, "1", 1.0])
def test_gate22_candidate_frame_selection_rejects_invalid_index(capture, index):
    from openflight.camera.trigger_timing_quality import validate_candidate_frame_index

    with pytest.raises(ValueError, match="candidate frame index"):
        validate_candidate_frame_index(capture, index)


def test_gate22_candidate_frame_selection_rejects_invalid_capture(capture):
    from openflight.camera.trigger_timing_quality import validate_candidate_frame_index

    invalid = replace(capture, session_id="")
    with pytest.raises(ValueError, match="invalid capture timing"):
        validate_candidate_frame_index(invalid, 1)


@pytest.mark.parametrize("field,value", [
    ("shot_id", 123),
    ("session_id", True),
    ("shot_id", "   "),
    ("session_id", []),
])
def test_gate22_malformed_capture_identity_fails_closed(capture, field, value):
    quality = assess_trigger_timing(replace(capture, **{field: value}))
    assert not quality.valid
    assert "capture identity" in quality.reason
    assert not quality.trigger_between_host_frames
