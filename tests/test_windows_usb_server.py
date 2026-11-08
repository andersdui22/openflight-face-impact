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
