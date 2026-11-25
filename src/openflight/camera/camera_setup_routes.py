"""Loopback camera preparation using the current adapter and ring."""

import io
import json
import math
import re
import subprocess
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Lock
from time import sleep
from zipfile import ZipFile

from flask import Blueprint, Response, request

from .offline_recording_routes import _producer_sha
from .windows_camera_inventory import windows_camera_inventory

camera_setup_routes = Blueprint("camera_setup", __name__, url_prefix="/api/face-impact/camera-setup")
_lock = Lock()
_fixture = None
FIXTURE_ID = "fixture:camera-setup-v1"


class DiagnosticFixture:
    """Monochrome test source for the ordinary Windows adapter."""

    def __init__(self, settings):
        import numpy as np

        self.image = np.broadcast_to(np.arange(settings.width, dtype=np.uint8), (settings.height, settings.width))
        self.controls = {}

    def isOpened(self):
        return True

    def set(self, prop, value):
        self.controls[prop] = value
        return True

    def get(self, prop):
        return self.controls.get(prop, 0)

    def read(self):
        sleep(1 / self.controls.get(5, 30))
        return True, self.image

    def release(self):
        pass


def _settings(data):
    from .windows_usb import UsbCameraSettings

    if data.get("identity") != FIXTURE_ID:
        raise ValueError("Selected device has no verified capture identity; only the fixture can start")
    width, height = data.get("width"), data.get("height")
    fps = data.get("fps")
    controls = (data.get("exposure"), data.get("gain"))
    if ((width, height) not in ((320, 200), (640, 400))
            or fps not in (30, 60, 120)
            or any(value is not None and (type(value) not in (int, float) or not math.isfinite(value)
                                          or abs(value) > 10000) for value in controls)):
        raise ValueError("Unsupported fixture settings")
    return UsbCameraSettings(width=int(width), height=int(height), requested_fps=float(fps),
                             pre_frames=3, post_frames=3, driver_exposure=controls[0], driver_gain=controls[1])


def _record(camera):
    from .offline_capture_recording import save_offline_capture

    if not camera.trigger():
        raise ValueError("Wait for fresh pre-trigger frames before recording")
    capture = camera.ring.wait_for_capture(2)
    if capture is None:
        raise ValueError("No complete post-trigger frame sequence")
    producer = _producer_sha()
    with TemporaryDirectory() as tmp:
        path = save_offline_capture(Path(tmp), capture, app_sha=producer, source="usb_preview_adapter")
        combined = io.BytesIO()
        with ZipFile(combined, "w") as package:
            package.write(path, "capture.zip")
            package.writestr("diagnostic.json", json.dumps({
                "schema_version": 1, "source": "synthetic_camera_setup_fixture",
                "physically_validated": False, "camera_identity": FIXTURE_ID,
                "timing_source": "host_arrival_monotonic",
                "sensor_exposure_timestamp": None,
                "app_sha": producer, "session_id": capture.session_id, "shot_id": capture.shot_id,
                "requested": asdict(camera.settings), "driver_reported": camera.negotiated,
                "driver_controls": camera.reported_controls,
            }, allow_nan=False))
    return Response(combined.getvalue(), mimetype="application/zip", headers={
        "Content-Disposition": 'attachment; filename="face-impact-diagnostic.zip"',
    })


@camera_setup_routes.post("/<action>")
def camera_setup(action):
    from openflight import server

    if (request.remote_addr not in ("127.0.0.1", "::1")
            or request.headers.get("X-OpenFlight-Camera-Setup") != "1"):
        return {"error": "Local camera setup unavailable"}, 403
    origin = request.headers.get("Origin", "")
    if origin not in ("", "null") and not re.fullmatch(r"https?://(?:localhost|127\.0\.0\.1)(?::\d+)?", origin):
        return {"error": "Local camera origin required"}, 403
    if not server.mock_mode:
        return {"error": "Camera setup is available in software test mode"}, 409
    if request.content_length and request.content_length > 128 * 1024:
        return {"error": "Camera setup request too large"}, 413
    try:
        return _camera_action(action, server)
    except (ValueError, TypeError, KeyError, RuntimeError) as error:
        return {"error": str(error)}, 422
    except (OSError, subprocess.SubprocessError):
        return {"error": "Camera inventory or diagnostic export unavailable"}, 503


def _camera_action(action, server):
    global _fixture  # pylint: disable=global-statement
    from .calibration_club_binding import CalibrationClubBinding, require_calibration_club_binding
    from .calibration_profile import CameraCalibrationProfile
    from .club_face_model import ClubFaceModel, ClubFamily, FaceSurface
    from .calibration_revision import calibration_revision
    from .calibration_revision_status import revision_bound_calibration_status
    from .windows_usb import WindowsUsbCamera

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return {"error": "Expected camera setup JSON"}, 400
    if action == "inventory":
        return {"devices": windows_camera_inventory(), "fixture_identity": FIXTURE_ID}
    with _lock:
        current = server.windows_usb_runtime
        if action == "profile":
            profile = CameraCalibrationProfile.from_json(data.get("profile", ""))
            size = current.delivered_size if current is not None else None
            result = revision_bound_calibration_status(
                profile, expected_revision=data.get("expected_revision"),
                camera_mode_id=None, image_size=size,
            )
            binding_status = "not_supplied"
            if data.get("club_evidence"):
                evidence = json.loads(data["club_evidence"])
                fields = evidence["club"]
                club = ClubFaceModel(**{**fields, "family": ClubFamily(fields["family"]),
                                       "surface": FaceSurface(fields["surface"])})
                binding = CalibrationClubBinding(**evidence["binding"])
                require_calibration_club_binding(binding, profile=profile, club_model=club)
                binding_status = "offline_revision_match"
            return {"profile_revision": calibration_revision(profile), "status": result,
                    "club_binding_status": binding_status}
        if current is not None and current is not _fixture:
            return {"error": "Existing camera owner must be stopped by its operator"}, 409
        if action == "record":
            if current is None:
                raise ValueError("Start the diagnostic fixture first")
            return _record(current)
        if action == "start":
            settings = _settings(data)
            if current is not None:
                current.stop()
            _fixture = WindowsUsbCamera(settings, camera_factory=lambda _index: DiagnosticFixture(settings))
            server.windows_usb_runtime = _fixture
            _fixture.start()
            return {"source": FIXTURE_ID}
        if action == "stop":
            if current is not None:
                current.stop()
            server.windows_usb_runtime = None
            _fixture = None
            return {"stopped": True}
    return {"error": "Unknown camera setup action"}, 404
