import ctypes as c
import io
import json
from time import monotonic, sleep
from zipfile import ZipFile

import numpy as np
import pytest

from openflight import server
from openflight.camera import camera_setup_routes, windows_media_foundation as mf


def test_announced_modes_are_bounded_and_raster_preserves_luminance():
    mode = mf.validated_mode({"width": 4, "height": 2, "numerator": 120, "denominator": 1, "format": 1})
    raw = bytes(range(16))
    assert np.array_equal(mf.analysis_raster(raw, mode), [[0, 2, 4, 6], [8, 10, 12, 14]])
    with pytest.raises(ValueError, match="stride"):
        mf.analysis_raster(raw + b"X", mode)
    from openflight.camera.windows_usb import UsbCameraSettings

    assert camera_setup_routes._capture_capacity(UsbCameraSettings(width=1920, height=1080), "YUY2") == 10


def test_mjpg_is_kept_as_received_and_checks_negotiated_dimensions():
    import cv2

    source = np.arange(64, dtype=np.uint8).reshape(8, 8)
    ok, encoded = cv2.imencode(".jpg", source)
    assert ok
    data = encoded.tobytes()
    assert mf.analysis_raster(data, mf.Mode(8, 8, 120, 1, 3)).shape == (8, 8)
    with pytest.raises(ValueError, match="dimensions"):
        mf.analysis_raster(data, mf.Mode(16, 8, 120, 1, 3))


def test_native_scan_drops_ambiguous_links(monkeypatch):
    class Library:
        def ofi_scan(self, callback):
            callback("abc", "Same model")
            callback("ABC", "Same model")
            callback("xyz", "Same model")
            return 0

    monkeypatch.setattr(mf, "_library", Library)
    assert [device["identity"] for device in mf.scan_devices()] == ["xyz"]


def test_physical_route_preserves_sample_times_without_publishing_impact(monkeypatch):
    class NativeLibrary:
        def ofi_modes(self, identity, callback):
            assert identity == "selected-device"
            for mode in (mf.Mode(4, 2, 10_000_000, 83_333, 1), mf.Mode(4, 2, 10_000_000, 47_619, 2)):
                callback(c.pointer(mode))
            return 0

        def ofi_open(self, identity, mode, output):
            assert identity == "selected-device"
            opened.append(mode._obj.settings())
            output._obj.value = 123
            return 0

        def ofi_identity(self, _handle):
            return "selected-device"

        def ofi_control(self, _handle, prop, setting, value, flags):
            if prop == 15:
                if setting:
                    assert (value._obj.value, flags._obj.value) == (-6, 2)
                else:
                    value._obj.value = -5
                    flags._obj.value = 2
                return 0
            return -1

        def ofi_control_range(self, _handle, prop, *outputs):
            if prop != 15:
                return -1
            for field, value in zip(outputs, (-12, -2, 1, -6, 3)):
                field._obj.value = value
            return 0

        def ofi_read(self, _handle, output, _capacity, sample):
            sleep(0.01)
            c.memmove(output, bytes(range(16)), 16)
            sample._obj.size = 16
            sample._obj.time_100ns = -1
            sample._obj.duration_100ns = 200
            sample._obj.callback_time_100ns = 500
            sample._obj.discontinuity = 1
            sample._obj.callback_qpc_ticks = 7_000
            sample._obj.readout_qpc_ticks = 7_100
            sample._obj.qpc_frequency_hz = 1_000_000
            return 0

        def ofi_close(self, handle):
            closed.append(handle.value)

    opened, closed = [], []
    monkeypatch.setattr(mf, "_library", NativeLibrary)
    monkeypatch.setattr(camera_setup_routes, "_physical_identity", lambda data: data["identity"])
    monkeypatch.setattr(camera_setup_routes, "_producer_sha", lambda: "a" * 40)
    monkeypatch.setattr(server, "mock_mode", True)
    monkeypatch.setattr(server, "windows_usb_runtime", None)
    monkeypatch.setenv("OPENFLIGHT_PHYSICAL_CAMERA_TOKEN", "trusted-desktop")
    client = server.app.test_client()
    base = "/api/face-impact/camera-setup/"
    headers = {"X-OpenFlight-Camera-Setup": "1", "X-OpenFlight-Physical-Camera": "trusted-desktop"}
    config = {"identity": "selected-device", "activate_physical": True, "pre_frames": 2, "post_frames": 2,
              "exposure_mode": "manual", "exposure": -6, "gain": 7,
              "mode": {"width": 4, "height": 2, "numerator": 10_000_000, "denominator": 83_333, "format": 1}}
    assert client.post(base + "start", json=config, headers={"X-OpenFlight-Camera-Setup": "1"}).status_code == 403
    assert client.post(base + "start", json={**config, "activate_physical": False}, headers=headers).status_code == 422
    advertised = client.post(base + "modes", json=config, headers=headers)
    assert advertised.status_code == 200, advertised.json
    faster, original = advertised.json["modes"]
    assert original == config["mode"] | {"pixel_format": "YUY2"}
    assert faster == {**config["mode"], "denominator": 47_619, "format": 2, "pixel_format": "NV12"}
    started = client.post(base + "start", json={**config, "mode": original}, headers=headers)
    assert started.status_code == 200, started.json
    try:
        deadline = monotonic() + 2
        while server.windows_usb_runtime.frames_received < 4 and monotonic() < deadline:
            sleep(.01)
        assert client.get("/api/camera/preview.jpg").status_code == 403
        assert client.get("/api/camera/preview.jpg", headers=headers).status_code == 200
        response = client.post(base + "record", json={"purpose": "golf_diagnostic"}, headers=headers)
        assert response.status_code == 200, response.json
        with ZipFile(io.BytesIO(response.data)) as archive:
            manifest = json.loads(archive.read("diagnostic.json"))
            assert manifest["source"] == "physical_camera_diagnostic"
            assert manifest["physically_validated"] is False
            assert manifest["sensor_exposure_timestamp"] is None
            assert len(manifest["native_frames"]) == 4
            assert manifest["capture_timing"]["callback_to_readout_ms"]["median"] == 0.1
            assert manifest["adjacent_equal_native_payloads"] == 3
            assert manifest["capture_timing"]["dropped_frames"] is None
            assert manifest["driver_ranges"]["exposure"]["supports_auto"] is True
            assert manifest["driver_ranges"]["gain"] is None
            assert manifest["driver_controls"]["exposure"] == {
                "requested": -6, "accepted_by_driver": True, "reported": -5,
            }
            assert manifest["driver_controls"]["gain"] == {
                "requested": 7, "accepted_by_driver": False, "reported": None,
            }
            for item in manifest["native_frames"]:
                assert archive.read(item["file"]) == bytes(range(16))
                assert item["driver_sample"]["sample_time_100ns"] is None
                assert item["driver_sample"]["sample_duration_100ns"] == 200
                assert item["driver_sample"]["source_reader_time_100ns"] == 500
                assert item["driver_sample"]["discontinuity"] is True
    finally:
        assert client.post(base + "stop", json={}, headers=headers).status_code == 200
    assert closed == [123]
    assert opened == [config["mode"] | {"pixel_format": "YUY2"}]
    restarted = client.post(base + "start", json={**config, "mode": faster}, headers=headers)
    assert restarted.status_code == 200, restarted.json
    try:
        assert opened[-1] == faster
    finally:
        assert client.post(base + "stop", json={}, headers=headers).status_code == 200
    assert closed == [123, 123]


@pytest.mark.parametrize(("numerator", "denominator", "pixel_format", "fps"), [
    (30, 1, 1, 30),
    (640, 1, 2, 640),
    (10_000_000, 83_333, 2, 120.00048000192001),
    (10_000_000, 47_619, 2, 210.00021000021),
    (10_000_000, 23_809, 3, 420.0092402032845),
])
def test_native_mode_preserves_advertised_ratio(numerator, denominator, pixel_format, fps):
    data = {"width": 640, "height": 480, "numerator": numerator,
            "denominator": denominator, "format": pixel_format}
    mode = mf.validated_mode(json.loads(json.dumps(data)))
    assert mode.settings() == {**data, "pixel_format": mf._FORMATS[pixel_format]}
    assert mode.numerator / mode.denominator == fps


@pytest.mark.parametrize(("field", "value", "reason"), [
    ("numerator", 2**32, "numerator"),
    ("denominator", 0, "denominator"),
    ("numerator", 120.0, "numerator"),
    ("format", 4, "pixel format"),
    ("width", 641, "raster dimensions"),
])
def test_rejects_invalid_native_mode(field, value, reason):
    data = {"width": 640, "height": 480, "numerator": 10_000_000, "denominator": 83_333, "format": 2}
    with pytest.raises(ValueError, match=reason):
        mf.validated_mode({**data, field: value})


def test_large_recording_window_does_not_block_native_mode_validation():
    data = {"width": 640, "height": 480, "numerator": 10_000_000, "denominator": 47_619, "format": 2}
    assert mf.validated_mode(data).settings() == {**data, "pixel_format": "NV12"}


@pytest.mark.parametrize(("data", "capacity", "ten_ms"), [
    ((1280, 800, 10_000_000, 83_333, 2), 26, 2),
    ((640, 480, 10_000_000, 47_619, 2), 87, 3),
    ((320, 240, 10_000_000, 23_809, 3), 174, 5),
    ((160, 120, 640, 1, 2), 512, 7),
])
def test_native_mode_record_capacity_and_nominal_ms(data, capacity, ten_ms):
    from types import SimpleNamespace

    from openflight.camera.triggered_buffer import TriggeredFrameBuffer
    from openflight.camera.windows_usb import UsbCameraSettings

    mode = mf.Mode(*data).settings()
    settings = UsbCameraSettings(width=mode["width"], height=mode["height"])
    assert camera_setup_routes._capture_capacity(settings, mode["pixel_format"]) == capacity
    camera = SimpleNamespace(settings=settings, reported_native_mode=mode,
                             ring=TriggeredFrameBuffer(3, 3, capacity=capacity))
    assert camera_setup_routes._recording_window(camera, {"pre_ms": 10, "post_ms": 10}) == (ten_ms, ten_ms)
    with pytest.raises(ValueError, match="total recording frames"):
        camera_setup_routes._recording_window(camera, {"pre_frames": capacity, "post_frames": 1})
