"""Loopback camera preparation using the current adapter and ring."""

import io
import json
import math
import os
import re
import sqlite3
import subprocess
import sys
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
from secrets import compare_digest
from tempfile import TemporaryDirectory
from threading import Lock
from time import sleep
from zipfile import ZipFile

from flask import Blueprint, Response, current_app, request

from .offline_recording_routes import _producer_sha
from .offline_session_archive import OfflineSessionArchive

camera_setup_routes = Blueprint("camera_setup", __name__, url_prefix="/api/face-impact/camera-setup")
_lock = Lock()
_managed = None
FIXTURE_ID = "fixture:camera-setup-v1"
CAPTURE_PURPOSES = ("diagnostic", "checkerboard", "club_landmarks", "setup_reference", "golf_diagnostic")


class DiagnosticFixture:
    """Monochrome test source for the ordinary Windows adapter."""

    opened_identity = FIXTURE_ID

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

    width, height = data.get("width"), data.get("height")
    fps = data.get("fps")
    controls = (data.get("exposure"), data.get("gain"))
    if any(value is not None and (type(value) not in (int, float) or not math.isfinite(value)
                                          or abs(value) > 10000) for value in controls):
        raise ValueError("Invalid camera control values")
    pre, post = data.get("pre_frames", 3), data.get("post_frames", 3)
    if any(type(value) is not int or not 1 <= value <= 16 for value in (pre, post)):
        raise ValueError("Pre-trigger and post-trigger frame counts must each be 1 to 16")
    if data.get("identity") == FIXTURE_ID and (
            (width, height) not in ((320, 200), (640, 400)) or fps not in (30, 60, 120)):
        raise ValueError("Unsupported fixture settings")
    return UsbCameraSettings(width=int(width), height=int(height), requested_fps=float(fps),
                             pre_frames=pre, post_frames=post, driver_exposure=controls[0], driver_gain=controls[1])


def _record(camera, purpose):
    from .offline_capture_recording import save_offline_capture

    if purpose not in CAPTURE_PURPOSES:
        raise ValueError("Unknown diagnostic capture purpose")
    if not camera.trigger():
        raise ValueError("Wait for fresh pre-trigger frames before recording")
    capture = camera.ring.wait_for_capture(2)
    if capture is None:
        raise ValueError("No complete post-trigger frame sequence")
    producer = _producer_sha()
    identity = camera.identity_diagnostics
    physical = identity["status"] == "handle_match" and identity["backend"] == "media_foundation"
    if not physical and identity["status"] != "fixture_match":
        raise ValueError("Camera identity continuity was lost; capture cannot be exported")
    with TemporaryDirectory() as tmp:
        path = save_offline_capture(Path(tmp), capture, app_sha=producer, source="usb_preview_adapter")
        combined = io.BytesIO()
        with ZipFile(combined, "w") as package:
            payload = path.read_bytes()
            package.writestr("capture.zip", payload)
            native = []
            if physical:
                for index, frame in enumerate(capture.frames):
                    if frame.native_payload is None:
                        raise ValueError("Native frame payload missing")
                    name = f"native/{index:03}.{'jpg' if camera.reported_native_mode['pixel_format'] == 'MJPG' else 'bin'}"
                    package.writestr(name, frame.native_payload)
                    native.append({"file": name, "sha256": sha256(frame.native_payload).hexdigest(),
                                   "driver_sample": frame.driver_sample,
                                   "host_timestamp_ns": frame.host_timestamp_ns})
            manifest = {
                "schema_version": 1,
                "source": "physical_camera_diagnostic" if physical else "synthetic_camera_setup_fixture",
                "physically_validated": False, "camera_identity": identity["opened"],
                "native_frames": native, "native_mode": camera.reported_native_mode,
                "exposure_mode": camera.reported_exposure_mode,
                "purpose": purpose, "capture_zip_sha256": sha256(payload).hexdigest(),
                "identity": camera.identity_diagnostics,
                "delivered_dimensions": [capture.frames[0].image.shape[1], capture.frames[0].image.shape[0]],
                "host_intervals_ns": [later.host_timestamp_ns - earlier.host_timestamp_ns
                                      for earlier, later in zip(capture.frames, capture.frames[1:])],
                "observed_host_fps": camera.delivered_fps,
                "sample_timestamp_source": "media_foundation_stream_sample" if physical else None,
                "timing_source": "host_arrival_monotonic",
                "sensor_exposure_timestamp": None,
                "app_sha": producer, "session_id": capture.session_id, "shot_id": capture.shot_id,
                "requested": asdict(camera.settings), "driver_reported": camera.negotiated,
                "driver_controls": camera.reported_controls,
            }
            package.writestr("diagnostic.json", json.dumps(manifest, allow_nan=False))
    archive_path = current_app.config.get("OFFLINE_IMPACT_ARCHIVE_PATH")
    if archive_path is not None:
        OfflineSessionArchive(archive_path).save_diagnostic_manifest(manifest)
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
    except (OSError, sqlite3.Error, subprocess.SubprocessError):
        return {"error": "Camera inventory or diagnostic export unavailable"}, 503


def _camera_action(action, server):
    global _managed  # pylint: disable=global-statement
    from .calibration_club_binding import CalibrationClubBinding, require_calibration_club_binding
    from .calibration_profile import CameraCalibrationProfile
    from .club_face_model import ClubFaceModel, ClubFamily, FaceSurface
    from .calibration_revision import calibration_revision
    from .calibration_revision_status import revision_bound_calibration_status
    from .windows_usb import WindowsUsbCamera
    from .windows_media_foundation import MediaFoundationCamera, announced_modes, scan_devices, validated_mode

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return {"error": "Expected camera setup JSON"}, 400
    if action == "inventory":
        return {"devices": scan_devices() if sys.platform == "win32" else [], "fixture_identity": FIXTURE_ID}
    with _lock:
        if server.shutdown_cleanup_started or server.camera_capture_runtime is not None:
            return {"error": "Camera setup unavailable during shutdown or another camera owner"}, 409
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
        if current is not None and current is not _managed:
            return {"error": "Existing camera owner must be stopped by its operator"}, 409
        physical_owner = current is not None and (
            current.reported_native_mode is not None or
            (current.identity_diagnostics["selected"] not in (FIXTURE_ID, None))
        )
        physical_request = (action == "modes" or
                            (action == "start" and data.get("identity") != FIXTURE_ID))
        if (physical_request or physical_owner) and action in ("modes", "start", "stop", "record"):
            if physical_request:
                _physical_identity(data)
            if not physical_camera_authorized():
                return {"error": "Physical camera controls require the portable desktop app"}, 403
        if action == "record":
            if current is None:
                raise ValueError("Start the diagnostic fixture first")
            return _record(current, data.get("purpose", "diagnostic"))
        if action == "modes":
            if data.get("activate_physical") is not True:
                raise ValueError("Enable physical diagnostics before querying native modes")
            if current is not None:
                return {"error": "Stop the current capture before querying native modes"}, 409
            return {"modes": announced_modes(_physical_identity(data))}
        if action == "start":
            identity = data.get("identity")
            if identity == FIXTURE_ID:
                settings = _settings(data)
                factory = lambda _identity: DiagnosticFixture(settings)
            else:
                identity = _physical_identity(data)
                if data.get("activate_physical") is not True:
                    raise ValueError("Explicit physical diagnostic activation is required")
                pre, post = data.get("pre_frames", 3), data.get("post_frames", 3)
                if any(type(value) is not int or not 1 <= value <= 16 for value in (pre, post)):
                    raise ValueError("Invalid diagnostic window")
                mode = validated_mode(data.get("mode"), 2 * pre + post + 2)
                if any(value is not None and type(value) is not int for value in (data.get("exposure"), data.get("gain"))):
                    raise ValueError("Native driver controls require integers")
                exposure_mode = data.get("exposure_mode", "unchanged")
                if exposure_mode not in ("unchanged", "auto", "manual"):
                    raise ValueError("Invalid exposure mode")
                if exposure_mode == "manual" and data.get("exposure") is None:
                    raise ValueError("Enter a manual exposure value in driver units")
                settings = _settings({**data, "width": mode.width, "height": mode.height,
                                      "fps": mode.numerator / mode.denominator})
                factory = lambda link: MediaFoundationCamera(link, mode, exposure_mode)
            if current is not None:
                current.stop()
            _managed = WindowsUsbCamera(settings, selected_identity=identity, identity_factory=factory)
            server.windows_usb_runtime = _managed
            _managed.start()
            return {"source": identity}
        if action == "stop":
            if current is not None:
                current.stop()
            server.windows_usb_runtime = None
            _managed = None
            return {"stopped": True}
    return {"error": "Unknown camera setup action"}, 404


def physical_camera_authorized():
    """Require the desktop main process capability, not a renderer-supplied flag."""
    token = os.environ.get("OPENFLIGHT_PHYSICAL_CAMERA_TOKEN", "")
    provided = request.headers.get("X-OpenFlight-Physical-Camera", "")
    return (request.remote_addr in ("127.0.0.1", "::1")
            and bool(token) and compare_digest(token.encode(), provided.encode()))


def _physical_identity(data):
    identity = data.get("identity")
    if sys.platform != "win32" or not isinstance(identity, str) or identity.startswith("fixture:") or not identity:
        raise ValueError("Select an advertised Media Foundation device on Windows")
    return identity
