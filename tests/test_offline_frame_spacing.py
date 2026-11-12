"""Offline frame-spacing checks do not invent a contact frame."""

from dataclasses import replace

import numpy as np
import pytest

from openflight.camera.offline_frame_spacing import (
    OfflineFrameSpacing, assess_offline_frame_spacing,
)
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def capture():
    image = np.zeros((12, 12), dtype=np.uint8)
    return TriggeredCapture(
        (CameraFrame(image.copy(), 100, 1000, 100, 1.),
         CameraFrame(image.copy(), 200, 2000, 100, 1.),
         CameraFrame(image.copy(), 300, 3000, 100, 1.)),
        1, 1500, shot_id="shot", session_id="session",
    )


def assess(item, **kwargs):
    return assess_offline_frame_spacing(
        item, max_sensor_gap_ns=kwargs.get("sensor", 100),
        max_host_gap_ns=kwargs.get("host", 1000),
    )


def test_valid_offline_spacing_preserves_both_clock_intervals():
    result = assess(capture())
    assert result.accepted is True
    assert result.sensor_intervals_ns == (100, 100)
    assert result.host_intervals_ns == (1000, 1000)
    assert result.physical_contact_confirmed is False
    assert "contact unverified" in result.reason


def test_sensor_and_host_limits_are_independent():
    assert "sensor clock gap" in assess(capture(), sensor=99).reason
    assert "host clock gap" in assess(capture(), host=999).reason


def test_invalid_trigger_timing_fails_closed():
    invalid = replace(capture(), trigger_host_timestamp_ns=4000)
    result = assess(invalid)
    assert result.accepted is False
    assert result.sensor_intervals_ns == ()
    assert "invalid trigger timing" in result.reason


@pytest.mark.parametrize("bad", [0, -1, True, 2.5, None])
def test_invalid_sensor_limit_rejected(bad):
    with pytest.raises(ValueError, match="max_sensor_gap_ns"):
        assess_offline_frame_spacing(
            capture(), max_sensor_gap_ns=bad, max_host_gap_ns=1000,
        )


@pytest.mark.parametrize("bad", [0, -1, True, 2.5, None])
def test_invalid_host_limit_rejected(bad):
    with pytest.raises(ValueError, match="max_host_gap_ns"):
        assess_offline_frame_spacing(
            capture(), max_sensor_gap_ns=100, max_host_gap_ns=bad,
        )


def test_contact_claim_cannot_be_inserted():
    with pytest.raises(ValueError, match="physical contact"):
        OfflineFrameSpacing(True, "synthetic", (100,), (1000,), True)
