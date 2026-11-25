import json
from dataclasses import replace
from hashlib import sha256
from zipfile import ZipFile

import numpy as np
import pytest

from openflight.camera.offline_capture_batch import capture_fingerprint
from openflight.camera.offline_capture_recording import save_offline_capture
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture

SHA = "a" * 40


def fixture_capture():
    a = CameraFrame(np.arange(32, dtype=np.uint8).reshape(4, 8), 100, 100, 0, 0., True)
    b = replace(a, image=a.image + 10, sensor_timestamp_ns=300, host_timestamp_ns=300)
    return TriggeredCapture((a, b), 1, 200, "fixture-shot", "fixture-session")


def test_recording_retains_exact_rasters_and_does_not_invent_sensor_metadata(tmp_path):
    capture = fixture_capture()
    path = save_offline_capture(tmp_path, capture, app_sha=SHA, source="synthetic_fixture")
    with ZipFile(path) as recording:
        manifest = json.loads(recording.read("manifest.json"))
        assert manifest["capture_fingerprint"] == capture_fingerprint(capture)
        assert manifest["app_sha"] == SHA
        assert (manifest["width"], manifest["height"]) == (8, 4)
        assert (manifest["shot_id"], manifest["session_id"]) == ("fixture-shot", "fixture-session")
        assert manifest["trigger_host_timestamp_ns"] == 200
        assert manifest["physically_validated"] is False
        for frame, item in zip(capture.frames, manifest["frames"]):
            assert recording.read(item["file"]) == frame.image.tobytes()
            assert item["sha256"] == sha256(frame.image.tobytes()).hexdigest()
            assert item["host_timestamp_ns"] == frame.host_timestamp_ns
            assert item["sensor_timestamp_is_host_alias"] is True
            assert item["sensor_timestamp_ns"] is item["exposure_us"] is item["analogue_gain"] is None
    assert list(tmp_path.iterdir()) == [path]


def test_recording_rejects_mixed_dimensions_without_leaving_files(tmp_path):
    capture = fixture_capture()
    bad = replace(capture.frames[-1], image=np.ones((1, 1), dtype=np.uint8))
    with pytest.raises(ValueError, match="share uint8 dimensions"):
        save_offline_capture(tmp_path, replace(capture, frames=(capture.frames[0], bad)),
                             app_sha=SHA, source="synthetic_fixture")
    assert list(tmp_path.iterdir()) == []
