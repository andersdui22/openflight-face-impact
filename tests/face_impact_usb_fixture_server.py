"""Loopback-only backend entry point for hardware-free browser and Windows smoke tests."""

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Lock
from time import sleep

import numpy as np

from openflight import server
from openflight.camera.calibration_profile import CameraCalibrationProfile
from openflight.camera.calibration_store import save_calibration_profile
from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.offline_capture_preflight import preflight_offline_capture
from openflight.camera.windows_usb import UsbCameraSettings, WindowsUsbCamera


class FixtureDevice:
    """Deterministic images, including a different raster after reopening."""

    def __init__(self, width, height, level):
        self.image = np.tile(np.arange(width, dtype=np.uint8) + level, (height, 1))
        self.failure = None
        self.released = False

    def isOpened(self):
        return True

    def set(self, _prop, _value):
        return True

    def get(self, prop):
        return {3: 640, 4: 400, 5: 120}[prop]

    def read(self):
        sleep(0.015)
        if self.failure == "disconnect":
            return False, None
        if self.failure == "invalid":
            return True, self.image.astype(np.uint16)
        return True, self.image

    def release(self):
        self.released = True


def install_fixture():
    devices = []

    def open_device(_index):
        if devices and not devices[-1].released:
            raise RuntimeError("fixture tried to open a competing camera")
        device = FixtureDevice(96, 64, 32) if not devices else FixtureDevice(80, 48, 64)
        devices.append(device)
        return device

    camera = WindowsUsbCamera(
        UsbCameraSettings(pre_frames=1, post_frames=1), camera_factory=open_device,
    )
    server.windows_usb_runtime = camera
    lifecycle = Lock()

    @server.app.post("/api/test/usb-camera/<action>")
    def control_fixture(action):
        if server.request.remote_addr != "127.0.0.1" or server.request.headers.get(
            "X-OpenFlight-Smoke"
        ) != "usb-fixture":
            return {"error": "fixture control unavailable"}, 404
        with lifecycle:
            if action in ("disconnect", "invalid"):
                devices[-1].failure = action
                return {"action": action}
            if action == "restart":
                camera.stop()
                camera.start()
                return {"previous_handle_released": devices[-2].released}
            if action != "trigger":
                return {"error": "unknown fixture action"}, 404
            if not camera.trigger():
                return {"error": "fixture trigger unavailable"}, 409
            capture = camera.ring.wait_for_capture(2.0)
            if capture is None:
                return {"error": "fixture capture did not complete"}, 503
            try:
                preflight_offline_capture(capture)
            except ValueError as error:
                return {
                    "frame_sizes": [[f.image.shape[1], f.image.shape[0]] for f in capture.frames],
                    "pixel_levels": [int(f.image[0, 0]) for f in capture.frames],
                    "host_clock_aliases": [f.sensor_timestamp_is_host_alias for f in capture.frames],
                    "rejection": str(error),
                }
            raise RuntimeError("fixture capture unexpectedly passed independent timing preflight")


def main():
    sys.argv[1:] = ["--mock", "--host", "127.0.0.1", "--web-port", "8080", "--no-logging"]
    with TemporaryDirectory(prefix="openflight-usb-fixture-") as directory:
        profile = Path(directory) / "optics.json"
        calibration = CheckerboardCalibration(
            (96, 64), np.array([[100., 0., 48.], [0., 100., 32.], [0., 0., 1.]]),
            np.zeros(5), 0., (0.25,),
        )
        save_calibration_profile(profile, CameraCalibrationProfile(calibration, "fixture:96x64"))
        os.environ["OPENFLIGHT_FACE_IMPACT_CALIBRATION_PROFILE"] = str(profile)
        install_fixture()
        server.windows_usb_runtime.start()
        try:
            server.main()
        finally:
            server.windows_usb_runtime.stop()


if __name__ == "__main__":
    main()
