"""Hardware-free tests of the Windows USB adapter."""
import time

import numpy as np
import pytest

from openflight.camera.offline_capture_quality import require_usable_offline_capture
from openflight.camera.offline_frame_spacing import assess_offline_frame_spacing
from openflight.camera.trigger_timing_quality import validate_candidate_frame_index
from openflight.camera.windows_usb import UsbCameraSettings, WindowsUsbCamera


class FakeCamera:
    def __init__(self, *, fail_after=None, opened=True, pixel_value=80):
        self.opened = opened
        self.pixel_value = pixel_value
        self.fail_after = fail_after
        self.reads = 0
        self.released = False
        self.properties = {}

    def isOpened(self):
        return self.opened

    def set(self, prop, value):
        self.properties[prop] = value
        return True

    def get(self, prop):
        return self.properties.get(prop, 0)

    def read(self):
        self.reads += 1
        time.sleep(0.002)
        if self.fail_after is not None and self.reads > self.fail_after:
            return False, None
        return True, np.full((8, 12, 3), self.pixel_value, dtype=np.uint8)

    def release(self):
        self.released = True


def wait_until(predicate, timeout=2):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.005)
    pytest.fail("timed out waiting for camera")


def test_usb_frames_reuse_existing_ring_and_host_clock():
    fake = FakeCamera()
    camera = WindowsUsbCamera(
        UsbCameraSettings(width=12, height=8, pre_frames=2, post_frames=2),
        camera_factory=lambda index: fake,
    )
    camera.start()
    try:
        wait_until(lambda: camera.frames_received >= 3)
        assert camera.negotiated["width"] == 12
        assert camera.negotiated["height"] == 8
        frame = camera.ring.latest_frame
        assert frame.image.shape == (8, 12)
        assert frame.sensor_timestamp_ns == frame.host_timestamp_ns
        assert frame.exposure_us == 0
        assert camera.trigger()
        capture = camera.ring.wait_for_capture(timeout_s=2)
        assert capture is not None
        assert capture.pre_trigger_count == 2
        assert capture.post_trigger_count == 2
        assert all(frame.sensor_timestamp_is_host_alias for frame in capture.frames)
        spacing = assess_offline_frame_spacing(capture, max_sensor_gap_ns=100_000_000,
                                               max_host_gap_ns=100_000_000)
        assert not spacing.accepted
        assert spacing.reason == "invalid trigger timing: independent sensor timestamp unavailable"
        with pytest.raises(ValueError, match="independent sensor timestamp unavailable"):
            validate_candidate_frame_index(capture, capture.pre_trigger_count)
        with pytest.raises(ValueError, match="independent sensor timestamp unavailable"):
            require_usable_offline_capture(capture)
    finally:
        camera.stop()
    assert fake.released
    assert not camera.is_running


def test_disconnection_and_reconnect_after_stop():
    first = FakeCamera(fail_after=3)
    second = FakeCamera()
    devices = iter([first, second])
    camera = WindowsUsbCamera(UsbCameraSettings(pre_frames=2, post_frames=2),
                              camera_factory=lambda index: next(devices))
    camera.start()
    wait_until(lambda: camera.last_error is not None)
    assert "disconnected" in camera.last_error
    camera.stop()
    assert first.released
    camera.start()
    try:
        wait_until(lambda: camera.frames_received >= 6)
        assert camera.last_error is None
    finally:
        camera.stop()
    assert second.released


def test_unavailable_camera_releases_device():
    fake = FakeCamera(opened=False)
    camera = WindowsUsbCamera(camera_factory=lambda index: fake)
    with pytest.raises(RuntimeError, match="could not be opened"):
        camera.start()
    assert fake.released


def test_preview_reads_existing_ring_without_second_device_read(monkeypatch):
    import sys
    from types import SimpleNamespace

    fake = FakeCamera()
    camera = WindowsUsbCamera(
        UsbCameraSettings(pre_frames=2, post_frames=2),
        camera_factory=lambda index: fake,
    )
    camera.start()
    try:
        wait_until(lambda: camera.frames_received >= 3)
        observed = []

        def encode(ext, image):
            observed.append((ext, image.shape))
            return True, np.frombuffer(b"jpeg-fixture", dtype=np.uint8)

        monkeypatch.setitem(sys.modules, "cv2", SimpleNamespace(imencode=encode))
        assert camera.capture_preview_jpeg() == b"jpeg-fixture"
        assert observed == [(".jpg", (8, 12))]
    finally:
        camera.stop()
    assert fake.released


def test_preview_is_not_served_after_usb_reader_stops(monkeypatch):
    import sys
    from types import SimpleNamespace

    fake = FakeCamera()
    camera = WindowsUsbCamera(
        UsbCameraSettings(pre_frames=2, post_frames=2),
        camera_factory=lambda index: fake,
    )
    camera.start()
    wait_until(lambda: camera.frames_received >= 3)
    monkeypatch.setitem(sys.modules, "cv2", SimpleNamespace(
        imencode=lambda ext, image: (True, np.frombuffer(b"jpeg", dtype=np.uint8))
    ))
    assert camera.capture_preview_jpeg() == b"jpeg"
    camera.stop()
    assert camera.capture_preview_jpeg() is None

def test_delivered_fps_is_observed_and_reset_on_restart():
    fake = FakeCamera()
    camera = WindowsUsbCamera(camera_factory=lambda index: fake)
    assert camera.delivered_fps is None
    camera.start()
    try:
        # Frame count can advance before the reader publishes its FPS samples.
        # Wait for the actual observable being asserted, not a racing counter.
        wait_until(lambda: camera.delivered_fps is not None)
        assert camera.delivered_fps > 0
        assert camera.negotiated["reported_fps"] == 120.0
    finally:
        camera.stop()
    assert camera.delivered_fps is not None


def test_repeated_start_reuses_single_reader_and_device():
    """A second start must not create a second acquisition owner."""
    opened = []
    def factory(index):
        fake = FakeCamera()
        opened.append((index, fake))
        return fake

    camera = WindowsUsbCamera(
        UsbCameraSettings(pre_frames=2, post_frames=2), camera_factory=factory
    )
    camera.start()
    try:
        wait_until(lambda: camera.frames_received >= 2)
        camera.start()
        assert len(opened) == 1
        assert camera.is_running
    finally:
        camera.stop()
    assert opened[0][1].released


def test_failed_open_does_not_leave_owned_device_and_allows_retry():
    """Failed device acquisition leaves the owner free for a later retry."""
    unavailable = FakeCamera(opened=False)
    available = FakeCamera()
    devices = iter((unavailable, available))
    camera = WindowsUsbCamera(camera_factory=lambda index: next(devices))

    with pytest.raises(RuntimeError, match="could not be opened"):
        camera.start()
    assert unavailable.released
    assert not camera.is_running

    camera.start()
    try:
        wait_until(lambda: camera.frames_received >= 2)
        assert camera.is_running
    finally:
        camera.stop()
    assert available.released


def test_usb_reconnect_rotates_session_and_preserves_single_reader():
    """An actual adapter restart must reset capture identity and stale frames."""
    first = FakeCamera(fail_after=20)
    second = FakeCamera()
    devices = iter((first, second))
    camera = WindowsUsbCamera(
        UsbCameraSettings(pre_frames=1, post_frames=1),
        camera_factory=lambda index: next(devices),
    )
    camera.start()
    try:
        wait_until(lambda: camera.frames_received >= 2)
        assert camera.trigger()
        first_capture = camera.ring.wait_for_capture(timeout_s=1)
        assert first_capture is not None
        assert first_capture.shot_id and first_capture.session_id
        wait_until(lambda: camera.last_error is not None)
    finally:
        camera.stop()
    assert first.released

    camera.start()
    try:
        wait_until(lambda: camera.ring.buffered_frames >= 1)
        assert camera.trigger()
        second_capture = camera.ring.wait_for_capture(timeout_s=1)
        assert second_capture is not None
        assert second_capture.session_id != first_capture.session_id
        assert second_capture.shot_id != first_capture.shot_id
        assert camera.ring.pop_capture() is None
    finally:
        camera.stop()
    assert second.released

def test_restart_discards_stale_preview_frames_before_new_reader_delivers():
    """A new camera session must not reuse buffered frames from the prior one."""
    first = FakeCamera(fail_after=3, pixel_value=17)
    second = FakeCamera(pixel_value=211)
    devices = iter((first, second))
    camera = WindowsUsbCamera(
        UsbCameraSettings(pre_frames=2, post_frames=2),
        camera_factory=lambda index: next(devices),
    )
    camera.start()
    wait_until(lambda: camera.last_error is not None)
    assert camera.ring.latest_frame is not None
    camera.stop()
    camera.start()
    try:
        # New reader may already have delivered frames, but any visible frame
        # must belong to the restarted session, not the failed first session.
        assert camera.ring is not None
        assert camera.last_error is None
        wait_until(lambda: camera.frames_received >= 5)
        assert camera.ring.latest_frame is not None
        assert np.all(camera.ring.latest_frame.image == 211), 'stale frame from previous acquisition'
    finally:
        camera.stop()


def test_shared_ring_reset_discards_pending_capture_and_preview():
    """Restart resets both pre-trigger preview and a completed replay."""
    from openflight.camera.triggered_buffer import CameraFrame, TriggeredFrameBuffer

    ring = TriggeredFrameBuffer(2, 1)
    for stamp in (1, 2):
        ring.add_frame(CameraFrame(np.zeros((2, 2), dtype=np.uint8), stamp, stamp, 0, 0.0))
    assert ring.trigger(3)
    ring.add_frame(CameraFrame(np.zeros((2, 2), dtype=np.uint8), 4, 4, 0, 0.0))
    assert ring.latest_frame is not None
    ring.reset()
    assert ring.latest_frame is None
    assert ring.pop_capture() is None
    assert not ring.capture_busy
    assert ring.buffered_frames == 0


def test_reset_cancels_waiting_capture_consumer_without_timeout():
    """A consumer waiting for a capture must unblock when acquisition resets."""
    import threading
    from openflight.camera.triggered_buffer import CameraFrame, TriggeredFrameBuffer

    ring = TriggeredFrameBuffer(1, 2)
    ring.add_frame(CameraFrame(np.zeros((2, 2), dtype=np.uint8), 1, 1, 0, 0.0))
    assert ring.trigger(2)
    wait_entered = threading.Event()
    results = []
    original_wait_for = ring._condition.wait_for

    def tracked_wait_for(predicate, timeout=None):
        # Called while the condition lock is held. reset() cannot acquire
        # the lock until the actual wait releases it.
        wait_entered.set()
        return original_wait_for(predicate, timeout)

    ring._condition.wait_for = tracked_wait_for

    def consumer():
        results.append(ring.wait_for_capture(timeout_s=5))

    thread = threading.Thread(target=consumer)
    thread.start()
    assert wait_entered.wait(timeout=1)
    ring.reset()
    thread.join(timeout=1)
    assert not thread.is_alive(), "capture consumer remained blocked after reset"
    assert results == [None]
