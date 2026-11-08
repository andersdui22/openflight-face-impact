"""Windows USB monochrome acquisition using OpenFlight's existing frame ring.

OpenCV is imported lazily. A camera factory can be injected for hardware-free
tests. Timestamps are host arrival times, never camera exposure timestamps.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Callable

import numpy as np

from .triggered_buffer import CameraFrame, TriggeredFrameBuffer


@dataclass(frozen=True)
class UsbCameraSettings:
    device_index: int = 0
    width: int = 640
    height: int = 400
    requested_fps: float = 120.0
    pre_frames: int = 18
    post_frames: int = 6


class WindowsUsbCamera:
    """Single reader owns a USB device and feeds the existing ring buffer."""

    def __init__(self, settings: UsbCameraSettings | None = None, *,
                 camera_factory: Callable | None = None):
        self.settings = settings or UsbCameraSettings()
        self._factory = camera_factory
        self.ring = TriggeredFrameBuffer(self.settings.pre_frames, self.settings.post_frames)
        self._camera = None
        self._thread = None
        self._stop = threading.Event()
        self._last_error: str | None = None
        self.negotiated: dict[str, float] | None = None
        self._frames = 0

    @property
    def last_error(self) -> str | None:
        return self._last_error

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def frames_received(self) -> int:
        return self._frames

    def start(self) -> None:
        if self.is_running:
            return
        if self._camera is not None:
            raise RuntimeError("camera shutdown is still in progress")
        if self.settings.device_index < 0 or self.settings.width < 1 or self.settings.height < 1 or self.settings.requested_fps <= 0:
            raise ValueError("invalid USB camera settings")
        if self._factory is None:
            try:
                import cv2  # pylint: disable=import-outside-toplevel
            except ImportError as exc:
                raise RuntimeError("Windows USB capture requires opencv-python") from exc
            factory = lambda index: cv2.VideoCapture(index, cv2.CAP_DSHOW)
            properties = (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS)
        else:
            factory = self._factory
            # OpenCV's stable numeric CAP_PROP_* IDs; fixtures use the same.
            properties = (3, 4, 5)
        camera = factory(self.settings.device_index)
        try:
            if not camera.isOpened():
                raise RuntimeError(f"USB camera index {self.settings.device_index} could not be opened")
            for prop, value in zip(properties, (self.settings.width, self.settings.height, self.settings.requested_fps)):
                camera.set(prop, value)
            self.negotiated = {
                "width": camera.get(properties[0]),
                "height": camera.get(properties[1]),
                "reported_fps": camera.get(properties[2]),
            }
        except Exception:
            camera.release()
            raise
        self._camera = camera
        self._last_error = None
        self._stop.clear()
        self._thread = threading.Thread(target=self._read_loop, name="openflight-usb-reader", daemon=True)
        self._thread.start()

    def _read_loop(self) -> None:
        try:
            while not self._stop.is_set():
                ok, image = self._camera.read()
                host_ns = time.monotonic_ns()
                if not ok or image is None:
                    raise RuntimeError("USB camera read failed or disconnected")
                if image.ndim == 3 and image.shape[2] >= 3:
                    # BGR to grayscale without requiring another OpenCV call.
                    image = np.clip(np.rint(
                        image[:, :, 0].astype(np.float32) * 0.114
                        + image[:, :, 1].astype(np.float32) * 0.587
                        + image[:, :, 2].astype(np.float32) * 0.299
                    ), 0, 255).astype(np.uint8)
                if image.ndim != 2 or image.dtype != np.uint8:
                    raise RuntimeError("unsupported USB frame format")
                self.ring.add_frame(CameraFrame(
                    image=np.ascontiguousarray(image),
                    sensor_timestamp_ns=host_ns,  # host-clock alias; NOT sensor exposure
                    host_timestamp_ns=host_ns,
                    exposure_us=0,  # unknown until hardware controls are validated
                    analogue_gain=0.0,  # unknown
                ))
                self._frames += 1
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self._last_error = str(exc)
        finally:
            self._stop.set()

    def stop(self, timeout_s: float = 3.0) -> None:
        self._stop.set()
        thread = self._thread
        if thread is not None:
            thread.join(timeout=timeout_s)
            if thread.is_alive():
                raise TimeoutError("USB camera reader did not stop; device still owned")
        if self._camera is not None:
            self._camera.release()
            self._camera = None
        self._thread = None

    def capture_preview_jpeg(self) -> bytes | None:
        """Encode the latest buffered frame; never read the device twice.

        OpenCV is only needed when preview is requested. This method never
        owns a camera handle or consumes a triggered capture.
        """
        if not self.is_running or self._stop.is_set():
            return None
        frame = self.ring.latest_frame
        if frame is None:
            return None
        try:
            import cv2  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise RuntimeError("USB preview requires opencv-python") from exc
        ok, encoded = cv2.imencode(".jpg", frame.image)
        if not ok:
            raise RuntimeError("USB camera JPEG preview encoding failed")
        return encoded.tobytes()

    def trigger(self) -> bool:
        """Explicit software trigger; shot detection is outside Gate 03."""
        return self.ring.trigger(time.monotonic_ns())
