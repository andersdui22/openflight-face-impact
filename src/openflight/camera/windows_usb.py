"""Windows USB monochrome acquisition using OpenFlight's existing frame ring.

OpenCV is imported lazily. A camera factory can be injected for hardware-free
tests. Timestamps are host arrival times, never camera exposure timestamps.
"""
from __future__ import annotations

import math
import threading
import time
from collections import deque
from dataclasses import dataclass
from statistics import fmean, pstdev
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
    driver_exposure: float | None = None
    driver_gain: float | None = None


class WindowsUsbCamera:
    """Single reader owns a USB device and feeds the existing ring buffer."""

    def __init__(self, settings: UsbCameraSettings | None = None, *,
                 camera_factory: Callable | None = None, selected_identity: str | None = None,
                 identity_factory: Callable | None = None):
        self.settings = settings or UsbCameraSettings()
        if identity_factory is not None and (camera_factory is not None or not selected_identity):
            raise ValueError("identity factory requires one selected device identity")
        if selected_identity is not None and identity_factory is None:
            raise ValueError("selected identity requires an identity-capable capture provider")
        self._factory = camera_factory
        self._identity_factory = identity_factory
        self._selected_identity = selected_identity
        self._opened_identity = None
        self._identity_status = "not_opened" if selected_identity else "unverified_index"
        self.ring = TriggeredFrameBuffer(self.settings.pre_frames, self.settings.post_frames)
        self._camera = None
        self._thread = None
        self._stop = threading.Event()
        self._last_error: str | None = None
        self.negotiated: dict[str, float] | None = None
        self._frames = 0
        self._started_ns = None
        self._arrival_times_ns = deque(maxlen=256)
        self._arrival_lock = threading.Lock()
        self._lifecycle_lock = threading.Lock()
        self._recovery_stop = threading.Event()
        self._recovery = None
        self._reported_controls = {}
        self.reported_native_mode = None
        self.reported_exposure_mode = None

    @property
    def reported_controls(self) -> dict:
        """Unverified driver control values, without conversion to sensor units."""
        return self._reported_controls

    @property
    def reconnect_enabled(self) -> bool:
        """Whether this adapter owns a recovery worker."""
        return self._recovery is not None and self._recovery.is_alive()

    def start_reconnecting(self, *, interval_s: float = 2.0) -> None:
        """Retry the selected device index without owning two camera handles."""
        if not math.isfinite(interval_s) or interval_s <= 0:
            raise ValueError("invalid reconnect interval")
        self._validate_settings()
        with self._lifecycle_lock:
            if self.reconnect_enabled:
                return
            if self._camera is not None:
                raise RuntimeError("stop the existing reader before enabling recovery")
            self._recovery_stop.clear()
            self._recovery = threading.Thread(
                target=self._recover, args=(interval_s,), name="openflight-usb-recovery", daemon=True,
            )
            self._recovery.start()

    def _recover(self, interval_s):
        while not self._recovery_stop.is_set():
            if not self.is_running:
                try:
                    self._stop_reader(0)
                    if not self._recovery_stop.is_set():
                        self._start_reader()
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    self._last_error = str(exc)
            self._recovery_stop.wait(interval_s)

    def _validate_settings(self):
        if (self.settings.device_index < 0 or self.settings.width < 1 or self.settings.height < 1
                or not math.isfinite(self.settings.requested_fps) or self.settings.requested_fps <= 0
                or any(value is not None and not math.isfinite(value)
                       for value in (self.settings.driver_exposure, self.settings.driver_gain))):
            raise ValueError("invalid USB camera settings")

    def _read_controls(self, camera):
        result = {}
        # CAP_PROP_EXPOSURE and CAP_PROP_GAIN are driver-dependent, including their units.
        for label, prop, value in (
            ("exposure", 15, self.settings.driver_exposure),
            ("gain", 14, self.settings.driver_gain),
        ):
            if value is not None:
                applied = bool(camera.set(prop, value))
                reported = camera.get(prop) if applied else None
                result[label] = {
                    "requested": value, "accepted_by_driver": applied,
                    "reported": reported if reported is not None and math.isfinite(reported) else None,
                }
        return result

    @property
    def last_error(self) -> str | None:
        return self._last_error

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def frames_received(self) -> int:
        return self._frames

    @property
    def delivered_size(self) -> tuple[int, int] | None:
        """Width and height of the latest delivered frame, in pixels."""
        frame = self.ring.latest_frame
        if frame is None:
            return None
        height, width = frame.image.shape
        return width, height

    @property
    def identity_diagnostics(self) -> dict:
        """Report selected identity and identity read from the actual open handle."""
        return {
            "selected": self._selected_identity,
            "opened": self._opened_identity,
            "status": self._identity_status,
            "backend": (getattr(self._camera, "capture_backend", None) or ("fixture" if (self._selected_identity or "").startswith("fixture:") else
                        "identity_provider" if self._identity_factory else
                        "injected_fixture" if self._factory else "opencv_directshow")),
        }

    @property
    def host_frame_intervals_ms(self) -> dict | None:
        """Describe the rolling delivery window without inferring exposure times."""
        with self._arrival_lock:
            samples = tuple(self._arrival_times_ns)
        intervals = [(later - earlier) / 1_000_000 for earlier, later in zip(samples, samples[1:])]
        if not intervals:
            return None
        return {
            "count": len(intervals), "min": min(intervals), "max": max(intervals),
            "mean": fmean(intervals), "stddev": pstdev(intervals),
        }

    @property
    def delivered_fps(self) -> float | None:
        """Observed frame arrivals over a rolling window, not sensor FPS."""
        with self._arrival_lock:
            samples = tuple(self._arrival_times_ns)
        if len(samples) < 2 or samples[-1] <= samples[0]:
            return None
        return (len(samples) - 1) * 1_000_000_000 / (samples[-1] - samples[0])

    def start(self) -> None:
        with self._lifecycle_lock:
            if not self.reconnect_enabled:
                self._start_reader()

    def _start_reader(self):
        if self.is_running:
            return
        if self._camera is not None:
            raise RuntimeError("camera shutdown is still in progress")
        self._validate_settings()
        if self._identity_factory is not None:
            factory = self._identity_factory
            properties = (3, 4, 5)
        elif self._factory is None:
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
        self.negotiated = None
        self._reported_controls = {}
        self.reported_native_mode = None
        self.reported_exposure_mode = None
        self._opened_identity = None
        if self._selected_identity:
            self._identity_status = "opening"
        try:
            camera = factory(self._selected_identity if self._identity_factory else self.settings.device_index)
        except Exception:
            if self._selected_identity:
                self._identity_status = "identity_unavailable"
            raise
        try:
            if not camera.isOpened():
                raise RuntimeError(f"USB camera index {self.settings.device_index} could not be opened")
            if self._selected_identity:
                identity = getattr(camera, "opened_identity", None)
                if (not isinstance(identity, str)
                        or identity.casefold() != self._selected_identity.casefold()):
                    self._identity_status = "identity_mismatch"
                    raise RuntimeError("Opened camera identity does not match selected camera")
                self._opened_identity = identity
                self._identity_status = "fixture_match" if identity.startswith("fixture:") else "handle_match"
            for prop, value in zip(properties, (self.settings.width, self.settings.height, self.settings.requested_fps)):
                camera.set(prop, value)
            reported_mode = (camera.get(prop) for prop in properties)
            self.negotiated = {
                label: value if math.isfinite(value) and value > 0 else None
                for label, value in zip(("width", "height", "reported_fps"), reported_mode)
            }
            if hasattr(camera, "configure_driver_exposure"):
                camera.configure_driver_exposure()
            self._reported_controls = self._read_controls(camera)
            if hasattr(camera, "mode_diagnostics"):
                self.reported_native_mode = camera.mode_diagnostics()
                self.reported_exposure_mode = camera.exposure_diagnostics()
        except Exception:
            camera.release()
            self._opened_identity = None
            if self._selected_identity and self._identity_status != "identity_mismatch":
                self._identity_status = "identity_unavailable"
            raise
        # The previous reader is fully stopped before a new session starts.
        # Reuse the same ring while discarding stale frames and shot identity.
        self.ring.reset()
        self._camera = camera
        self._last_error = None
        with self._arrival_lock:
            self._arrival_times_ns.clear()
            self._frames = 0
            self._started_ns = time.monotonic_ns()
        self._stop.clear()
        self._thread = threading.Thread(target=self._read_loop, name="openflight-usb-reader", daemon=True)
        self._thread.start()

    def _read_loop(self) -> None:
        shape = None
        try:
            while not self._stop.is_set():
                ok, image = self._camera.read()
                host_ns = getattr(self._camera, "host_arrival_ns", None) or time.monotonic_ns()
                if not ok or image is None:
                    raise RuntimeError("USB camera read failed or disconnected")
                if not isinstance(image, np.ndarray) or image.dtype != np.uint8 or image.size == 0:
                    raise RuntimeError("unsupported USB frame format")
                if image.ndim == 3 and image.shape[2] in (3, 4):
                    # BGR to grayscale without requiring another OpenCV call.
                    image = np.clip(np.rint(
                        image[:, :, 0].astype(np.float32) * 0.114
                        + image[:, :, 1].astype(np.float32) * 0.587
                        + image[:, :, 2].astype(np.float32) * 0.299
                    ), 0, 255).astype(np.uint8)
                if image.ndim != 2:
                    raise RuntimeError("unsupported USB frame format")
                if shape is not None and shape != image.shape:
                    raise RuntimeError("USB frame dimensions changed during acquisition")
                shape = image.shape
                self.ring.add_frame(CameraFrame(
                    image=np.array(image, copy=True, order="C"),
                    sensor_timestamp_ns=host_ns,  # host-clock alias; NOT sensor exposure
                    host_timestamp_ns=host_ns,
                    exposure_us=0,  # unknown until hardware controls are validated
                    analogue_gain=0.0,  # unknown
                    sensor_timestamp_is_host_alias=True,
                    driver_sample=getattr(self._camera, "sample_metadata", None),
                    native_payload=getattr(self._camera, "native_payload", None),
                ))
                with self._arrival_lock:
                    self._arrival_times_ns.append(host_ns)
                    self._frames += 1
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self._last_error = str(exc)
            if self._selected_identity:
                self._opened_identity = None
                self._identity_status = "continuity_lost"
        finally:
            self._stop.set()

    def stop(self, timeout_s: float = 3.0) -> None:
        with self._lifecycle_lock:
            self._recovery_stop.set()
            if self._recovery is not None:
                self._recovery.join(timeout_s)
                if self._recovery.is_alive():
                    raise TimeoutError("USB camera recovery did not stop; device still owned")
                self._recovery = None
            self._stop_reader(timeout_s)

    def _stop_reader(self, timeout_s):
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
        self._opened_identity = None
        if self._selected_identity:
            self._identity_status = "not_opened"

    @property
    def last_frame_age_ms(self) -> float | None:
        """Host-clock age of the last frame delivered by this session."""
        with self._arrival_lock:
            if not self._arrival_times_ns:
                return None
            return (time.monotonic_ns() - self._arrival_times_ns[-1]) / 1_000_000

    @property
    def delivery_stale(self) -> bool:
        """Reject old frames even if the underlying driver is still blocked in read."""
        with self._arrival_lock:
            last = self._arrival_times_ns[-1] if self._arrival_times_ns else self._started_ns
        return (last is not None
                and time.monotonic_ns() - last > max(1e9, 3e9 / self.settings.requested_fps))

    def capture_preview_jpeg(self) -> bytes | None:
        """Encode the latest buffered frame; never read the device twice.

        OpenCV is only needed when preview is requested. This method never
        owns a camera handle or consumes a triggered capture.
        """
        if not self.is_running or self._stop.is_set() or self.delivery_stale:
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
        return (self.is_running and not self._stop.is_set() and not self.delivery_stale
                and self.ring.trigger(time.monotonic_ns()))
