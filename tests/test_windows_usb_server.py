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
    assert response.json == {"enabled": False, "state": "disabled"}


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
