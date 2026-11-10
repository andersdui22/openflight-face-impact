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
    assert capture.shot_id and capture.session_id
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
    ring.add_frame(frame(10))
    next_capture = ring.pop_capture()
    assert next_capture is not None
    assert next_capture.shot_id != replay.shot_id
    assert next_capture.session_id == replay.session_id
    assert next_capture.trigger_host_timestamp_ns == 9


def test_gate15_single_slot_backpressure_rejects_unconsumed_capture():
    ring = TriggeredFrameBuffer(pre_trigger_frames=1, post_trigger_frames=1)
    ring.add_frame(frame(1))
    assert ring.trigger(host_timestamp_ns=2)
    ring.add_frame(frame(3))
    ring.add_frame(frame(4))
    assert not ring.trigger(host_timestamp_ns=5)
    first = ring.pop_capture()
    assert first is not None and first.shot_id
    assert first.trigger_host_timestamp_ns == 2
    assert ring.trigger(host_timestamp_ns=6)
    ring.add_frame(frame(7))
    second = ring.pop_capture()
    assert second is not None
    assert second.shot_id != first.shot_id
    assert second.session_id == first.session_id


def test_gate15_replay_preserves_trigger_snapshot_after_new_frames():
    ring = TriggeredFrameBuffer(pre_trigger_frames=2, post_trigger_frames=1)
    ring.add_frame(frame(11))
    ring.add_frame(frame(12))
    assert ring.trigger(host_timestamp_ns=13)
    ring.add_frame(frame(14))
    capture = ring.pop_capture()
    assert capture is not None
    snapshot = tuple(f.host_timestamp_ns for f in capture.frames)
    ring.add_frame(frame(15))
    ring.add_frame(frame(16))
    assert snapshot == (11, 12, 14)
    assert tuple(f.host_timestamp_ns for f in capture.frames) == snapshot
    assert capture.shot_id
    assert capture.session_id


def test_gate15_rejected_trigger_does_not_allocate_another_shot():
    ring = TriggeredFrameBuffer(pre_trigger_frames=1, post_trigger_frames=1)
    ring.add_frame(frame(21))
    assert ring.trigger(host_timestamp_ns=22)
    assert not ring.trigger(host_timestamp_ns=23)
    ring.add_frame(frame(24))
    first = ring.pop_capture()
    assert first is not None
    assert first.trigger_host_timestamp_ns == 22
    ring.add_frame(frame(25))
    assert ring.trigger(host_timestamp_ns=26)
    ring.add_frame(frame(27))
    second = ring.pop_capture()
    assert second is not None
    assert first.shot_id != second.shot_id
    assert first.session_id == second.session_id
