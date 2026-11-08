"""Hardware-free tests of the Windows USB adapter."""
import time

import numpy as np
import pytest

from openflight.camera.windows_usb import UsbCameraSettings, WindowsUsbCamera


class FakeCamera:
    def __init__(self, *, fail_after=None, opened=True):
        self.opened = opened
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
        return True, np.full((8, 12, 3), 80, dtype=np.uint8)

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
