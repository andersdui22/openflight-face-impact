import io
import json
from pathlib import Path
from time import monotonic, sleep
from zipfile import ZipFile

from openflight import server
from openflight.camera.offline_capture_recording import load_offline_capture

HEADERS = {"X-OpenFlight-Camera-Setup": "1"}
BASE = "/api/face-impact/camera-setup/"


def test_fixture_reconnect_and_diagnostic_archive(monkeypatch, tmp_path):
    monkeypatch.setattr(server, "mock_mode", True)
    monkeypatch.setattr(server, "windows_usb_runtime", None)
    monkeypatch.setattr("openflight.camera.camera_setup_routes._producer_sha", lambda: "a" * 40)
    client = server.app.test_client()
    settings = {"identity": "fixture:camera-setup-v1", "width": 320, "height": 200, "fps": 60,
                "exposure": -6, "gain": 10}
    assert client.post(BASE + "start", json=settings, headers=HEADERS).status_code == 200
    first = server.windows_usb_runtime
    try:
        denied = client.post(BASE + "start", json={**settings, "identity": "index:0"}, headers=HEADERS)
        assert denied.status_code == 422
        assert server.windows_usb_runtime is first
        assert client.post(BASE + "start", json=settings, headers=HEADERS).status_code == 200
        assert not first.is_running
        deadline = monotonic() + 2
        while server.windows_usb_runtime.frames_received < 4 and monotonic() < deadline:
            sleep(.01)
        status = client.get("/api/camera/usb/status").json
        assert status["requested"]["requested_fps"] == 60
        assert status["delivered_size"] == [320, 200]
        assert status["driver_controls"]["exposure"]["reported"] == -6
        export = client.post(BASE + "record", json={}, headers=HEADERS)
        assert export.status_code == 200, export.json
        with ZipFile(io.BytesIO(export.data)) as package:
            meta = json.loads(package.read("diagnostic.json"))
            path = Path(tmp_path) / "capture.zip"
            path.write_bytes(package.read("capture.zip"))
        capture = load_offline_capture(path).capture
        assert capture.pre_trigger_count == capture.post_trigger_count == 3
        assert all(frame.sensor_timestamp_is_host_alias for frame in capture.frames)
        assert meta["session_id"] == capture.session_id and meta["shot_id"] == capture.shot_id
        assert meta["sensor_exposure_timestamp"] is None
        assert meta["physically_validated"] is False
    finally:
        assert client.post(BASE + "stop", json={}, headers=HEADERS).status_code == 200


def test_pnp_inventory_preserves_identity_without_capture_index(monkeypatch):
    from types import SimpleNamespace

    from openflight.camera import windows_camera_inventory as inventory

    rows = [
        {"FriendlyName": "USB Camera", "InstanceId": "USB\\VID_A\\PORT_1", "Status": "OK"},
        {"FriendlyName": "USB Camera", "InstanceId": "USB\\VID_A\\PORT_2", "Status": "OK"},
        {"FriendlyName": "USB Camera", "InstanceId": "usb\\vid_a\\port_2", "Status": "OK"},
    ]
    monkeypatch.setattr(inventory.sys, "platform", "win32")
    monkeypatch.setattr(inventory.subprocess, "CREATE_NO_WINDOW", 0, raising=False)
    monkeypatch.setattr(inventory.subprocess, "run", lambda *_a, **_kw: SimpleNamespace(stdout=json.dumps(rows)))
    result = inventory.windows_camera_inventory()
    assert {item["identity"].casefold() for item in result} == {"usb\\vid_a\\port_1", "usb\\vid_a\\port_2"}
    assert all(item["capture_identity_verified"] is False and "index" not in item for item in result)
