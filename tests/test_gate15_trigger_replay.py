"""Gate 15: hardware-free trigger/replay contract for the shared camera ring.

These tests do not claim a real impact detector or physical timing accuracy.
"""
import numpy as np

from openflight.camera.triggered_buffer import CameraFrame, TriggeredFrameBuffer


def frame(stamp):
    return CameraFrame(
        image=np.full((2, 3), stamp, dtype=np.uint8),
        sensor_timestamp_ns=stamp,
        host_timestamp_ns=stamp,
        exposure_us=0,
        analogue_gain=0.0,
    )


def test_gate15_trigger_preserves_ordered_pre_and_post_frames():
    ring = TriggeredFrameBuffer(pre_trigger_frames=3, post_trigger_frames=2)
    for stamp in (1, 2, 3, 4):
        ring.add_frame(frame(stamp))
    assert ring.trigger(host_timestamp_ns=5)
    assert ring.capture_busy
    assert not ring.trigger(host_timestamp_ns=6)
    ring.add_frame(frame(7))
    assert ring.pop_capture() is None
    ring.add_frame(frame(8))
    capture = ring.pop_capture()
    assert capture is not None
    assert capture.pre_trigger_count == 3
    assert capture.post_trigger_count == 2
    assert capture.trigger_host_timestamp_ns == 5
    assert [f.host_timestamp_ns for f in capture.frames] == [2, 3, 4, 7, 8]
    assert ring.pop_capture() is None


def test_gate15_replay_is_snapshot_and_cannot_trigger_twice_before_consumed():
    ring = TriggeredFrameBuffer(pre_trigger_frames=2, post_trigger_frames=1)
    ring.add_frame(frame(1))
    ring.add_frame(frame(2))
    assert ring.trigger(host_timestamp_ns=3)
    ring.add_frame(frame(4))
    assert not ring.trigger(host_timestamp_ns=5)
    replay = ring.pop_capture()
    assert replay is not None
    assert tuple(f.image[0, 0] for f in replay.frames) == (1, 2, 4)
    ring.add_frame(frame(6))
    assert not ring.trigger(host_timestamp_ns=7)  # insufficient new preframes
    ring.add_frame(frame(8))
    assert ring.trigger(host_timestamp_ns=9)
