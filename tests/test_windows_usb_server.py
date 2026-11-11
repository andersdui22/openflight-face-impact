"""USB preview HTTP contract without a physical camera."""
from types import SimpleNamespace

from openflight import server


def test_usb_preview_uses_single_existing_runtime(monkeypatch):
    calls = []
    camera = SimpleNamespace(capture_preview_jpeg=lambda: calls.append("preview") or b"jpeg")
    monkeypatch.setattr(server, "windows_usb_runtime", camera)
    monkeypatch.setattr(server, "camera_capture_runtime", None)
    response = server.app.test_client().get("/api/camera/preview.jpg")
    assert response.status_code == 200
    assert response.data == b"jpeg"
    assert response.mimetype == "image/jpeg"
    assert calls == ["preview"]


def test_usb_preview_unavailable_is_503(monkeypatch):
    def fail():
        raise RuntimeError("camera disconnected")

    monkeypatch.setattr(server, "windows_usb_runtime",
                        SimpleNamespace(capture_preview_jpeg=fail))
    monkeypatch.setattr(server, "camera_capture_runtime", None)
    response = server.app.test_client().get("/api/camera/preview.jpg")
    assert response.status_code == 503
    assert b"unavailable" in response.data


def test_usb_preview_disabled_is_404(monkeypatch):
    monkeypatch.setattr(server, "windows_usb_runtime", None)
    monkeypatch.setattr(server, "camera_capture_runtime", None)
    assert server.app.test_client().get("/api/camera/preview.jpg").status_code == 404


def test_usb_status_disabled(monkeypatch):
    monkeypatch.setattr(server, "windows_usb_runtime", None)
    response = server.app.test_client().get("/api/camera/usb/status")
    assert response.status_code == 200
    assert response.json["enabled"] is False
    assert response.json["state"] == "disabled"
    assert response.json["calibration"]["state"] == "not_calibrated"
    assert response.json["calibration"]["physical_validation"] is False


def test_usb_status_running_does_not_claim_measured_fps(monkeypatch):
    camera = SimpleNamespace(
        is_running=True, frames_received=12, last_error=None,
        negotiated={"width": 640, "height": 400, "reported_fps": 120.0},
    )
    monkeypatch.setattr(server, "windows_usb_runtime", camera)
    response = server.app.test_client().get("/api/camera/usb/status")
    assert response.status_code == 200
    assert response.json["state"] == "running"
    assert response.json["frames_received"] == 12
    assert response.json["actual_fps_measured"] is False
    assert response.json["timestamp_source"] == "host_arrival_monotonic"
    assert response.json["calibration"]["physical_validation"] is False


def test_usb_status_reports_disconnect_error(monkeypatch):
    camera = SimpleNamespace(
        is_running=False, frames_received=3,
        last_error="USB camera read failed or disconnected", negotiated=None,
    )
    monkeypatch.setattr(server, "windows_usb_runtime", camera)
    response = server.app.test_client().get("/api/camera/usb/status")
    assert response.status_code == 200
    assert response.json["state"] == "error"
    assert "disconnected" in response.json["last_error"]


def test_usb_preview_stopped_returns_503_not_stale_jpeg(monkeypatch):
    monkeypatch.setattr(
        server, "windows_usb_runtime",
        SimpleNamespace(capture_preview_jpeg=lambda: None),
    )
    monkeypatch.setattr(server, "camera_capture_runtime", None)
    response = server.app.test_client().get("/api/camera/preview.jpg")
    assert response.status_code == 503
    assert response.mimetype != "image/jpeg"


def test_usb_status_starting_before_first_frame(monkeypatch):
    camera = SimpleNamespace(
        is_running=True, frames_received=0, last_error=None, negotiated=None,
    )
    monkeypatch.setattr(server, "windows_usb_runtime", camera)
    response = server.app.test_client().get("/api/camera/usb/status")
    assert response.status_code == 200
    assert response.json["state"] == "starting"

def test_usb_status_exposes_observed_fps_only_while_running(monkeypatch):
    camera = SimpleNamespace(
        is_running=True, frames_received=12, last_error=None,
        negotiated={"reported_fps": 120.0}, delivered_fps=87.5,
    )
    monkeypatch.setattr(server, "windows_usb_runtime", camera)
    response = server.app.test_client().get("/api/camera/usb/status")
    assert response.json["actual_fps_measured"] is True
    assert response.json["delivered_fps"] == 87.5
    assert response.json["negotiated"]["reported_fps"] == 120.0
    camera.is_running = False
    stopped = server.app.test_client().get("/api/camera/usb/status")
    assert stopped.json["actual_fps_measured"] is False
    assert stopped.json["delivered_fps"] is None


def test_usb_status_invalid_profile_is_reported_without_camera_access(monkeypatch, tmp_path):
    monkeypatch.setattr(server, "windows_usb_runtime", None)
    missing = tmp_path / "missing-optics.json"
    monkeypatch.setenv("OPENFLIGHT_FACE_IMPACT_CALIBRATION_PROFILE", str(missing))
    response = server.app.test_client().get("/api/camera/usb/status")
    assert response.status_code == 200
    assert response.json["calibration"]["state"] == "profile_invalid"
    assert response.json["calibration"]["physical_validation"] is False


def test_usb_status_valid_offline_profile_never_claims_physical_mode(monkeypatch, tmp_path):
    import numpy as np  # pylint: disable=import-outside-toplevel
    from openflight.camera.calibration_profile import CameraCalibrationProfile  # pylint: disable=import-outside-toplevel
    from openflight.camera.calibration_store import save_calibration_profile  # pylint: disable=import-outside-toplevel
    from openflight.camera.checkerboard_calibration import CheckerboardCalibration  # pylint: disable=import-outside-toplevel

    calibration = CheckerboardCalibration(
        (640, 400),
        np.array([[530., 0., 315.], [0., 525., 198.], [0., 0., 1.]]),
        np.array([-0.24, 0.08, 0.002, -0.003, 0.]),
        0.22, (0.3, 0.25, 0.28),
    )
    path = tmp_path / "optics.json"
    save_calibration_profile(path, CameraCalibrationProfile(calibration, "synthetic:640x400"))
    monkeypatch.setenv("OPENFLIGHT_FACE_IMPACT_CALIBRATION_PROFILE", str(path))
    camera = SimpleNamespace(
        is_running=True, frames_received=1, last_error=None,
        negotiated={"width": 640, "height": 400, "reported_fps": 120.0},
        delivered_fps=None,
    )
    monkeypatch.setattr(server, "windows_usb_runtime", camera)
    response = server.app.test_client().get("/api/camera/usb/status")
    assert response.status_code == 200
    assert response.json["calibration"]["profile_loaded"] is True
    assert response.json["calibration"]["state"] == "mode_unknown"
    assert response.json["calibration"]["mode_compatible"] is False
    assert response.json["calibration"]["physical_validation"] is False
