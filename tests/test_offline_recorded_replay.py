import json
from dataclasses import replace
from zipfile import ZipFile

import numpy as np
import pytest

from openflight import server
from openflight.camera.calibration_club_binding import CalibrationClubBinding
from openflight.camera.calibration_profile import CameraCalibrationProfile
from openflight.camera.calibration_revision import calibration_revision
from openflight.camera.checkerboard_calibration import CheckerboardCalibration
from openflight.camera.club_face_model import ClubFaceModel, ClubFamily, FaceSurface
from openflight.camera.club_geometry_revision import club_geometry_revision
from openflight.camera.offline_capture_batch import capture_fingerprint
from openflight.camera.offline_capture_recording import load_offline_capture, save_offline_capture
from openflight.camera.offline_recorded_replay import (
    RecordedCaptureAdmission,
    RecordedReplayRejected,
    prepare_recorded_replay,
)
from openflight.camera.offline_session_archive import OfflineSessionArchive
from openflight.camera.synthetic_offline_impact_demo import publish_synthetic_offline_impact_demo
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture

SHA = "a" * 40


def test_saved_fixture_uses_same_analysis_and_session_export(tmp_path, monkeypatch):
    archive = OfflineSessionArchive(tmp_path / "sessions.sqlite3")

    def emit(*_args, **_kwargs):
        return None

    live = publish_synthetic_offline_impact_demo(
        "contact", emit, recipient="test", recording_directory=tmp_path, app_sha=SHA,
    )
    path = next(tmp_path.glob("*.zip"))
    replay = publish_synthetic_offline_impact_demo(
        "contact", emit, recipient="test", recording_path=path, app_sha=SHA, save=archive.save,
    )
    assert live == replay and replay["accepted"]
    assert replay["physically_validated"] is False
    shot, = archive.load(replay["session_id"])["shots"]
    assert shot["provenance"]["capture"]["acquisition"] == "synthetic-recording-v1"
    assert shot["provenance"]["capture"]["sha256"] == load_offline_capture(path).fingerprint
    monkeypatch.setitem(server.app.config, "OFFLINE_IMPACT_ARCHIVE_PATH", archive.path)
    response = server.app.test_client().get(f"/api/face-impact/sessions/{replay['session_id']}?download=1")
    assert response.status_code == 200
    assert response.json["shots"] == [shot]
    assert response.json["analysis"]["clubs"][0]["points_mm"]
    with pytest.raises(RecordedReplayRejected, match="provenance"):
        publish_synthetic_offline_impact_demo(
            "heel-contact", emit, recipient="test", recording_path=path, app_sha=SHA,
        )


@pytest.mark.parametrize("change, message", [
    ("raster", "raster hash"),
    ("metadata", "capture fingerprint"),
    ("extra", "unexpected or duplicate"),
])
def test_recording_tampering_is_rejected(tmp_path, change, message):
    image = np.arange(128, dtype=np.uint8).reshape(8, 16)
    frame = CameraFrame(image, 100, 200, 1_000, 1.)
    capture = TriggeredCapture((frame, replace(frame, sensor_timestamp_ns=300, host_timestamp_ns=400)),
                               1, 250, "shot", "session")
    original = save_offline_capture(tmp_path, capture, app_sha=SHA, source="synthetic_fixture")
    with ZipFile(original) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    if change == "raster":
        files["frames/0000.gray8"] = bytes(128)
    elif change == "metadata":
        metadata = json.loads(files["manifest.json"])
        metadata["trigger_host_timestamp_ns"] += 1
        files["manifest.json"] = json.dumps(metadata)
    else:
        files["../foreign"] = b"x"
    candidate = tmp_path / "edited.zip"
    with ZipFile(candidate, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    with pytest.raises(ValueError, match=message):
        load_offline_capture(candidate)


def test_replay_rejects_identity_profile_geometry_and_host_alias(tmp_path):
    image = np.arange(128, dtype=np.uint8).reshape(8, 16)
    before = CameraFrame(image, 200, 200, 0, 0., True)
    after = replace(before, sensor_timestamp_ns=400, host_timestamp_ns=400)
    capture = TriggeredCapture((before, after), 1, 300, "shot", "session")
    path = save_offline_capture(tmp_path, capture, app_sha=SHA, source="usb_preview_adapter")
    assert load_offline_capture(path).fingerprint == capture_fingerprint(capture)
    mode = "fixture:mode"
    calibration = CheckerboardCalibration((16, 8), np.diag([20., 20., 1.]), np.zeros(5), 0., (0.,))
    profile = CameraCalibrationProfile(calibration, mode)
    club = ClubFaceModel(ClubFamily.IRON, "fixture", FaceSurface.PLANAR, 80., 40., evidence_source="fixture")
    binding = CalibrationClubBinding(calibration_revision(profile), club.model_id, club_geometry_revision(club))
    admission = RecordedCaptureAdmission(capture_fingerprint(capture), SHA, "usb_preview_adapter",
                                         "windows-device-interface:fixture", mode, binding)
    options = dict(admission=admission, camera_identity="windows-device-interface:fixture", profile=profile, club=club,
                   max_sensor_gap_ns=1000, max_host_gap_ns=1000)
    for patch, message in [
        ({"camera_identity": "0"}, "camera_identity"),
        ({"camera_identity": "index:0", "admission": replace(admission, camera_identity="index:0")}, "camera_identity"),
        ({"profile": replace(profile, calibration=replace(calibration, fit_rms_px=0.1))}, "revision is stale"),
        ({"club": replace(club, width_mm=81.)}, "geometry revision is stale"),
        ({}, "independent sensor timestamp unavailable"),
    ]:
        with pytest.raises(RecordedReplayRejected, match=message):
            prepare_recorded_replay(path, **(options | patch))


def test_replay_rejects_monotonic_frames_when_trigger_is_outside_capture(tmp_path):
    scene = np.tile(np.arange(32, dtype=np.uint8) * 4 + 16, (16, 1))
    first = CameraFrame(scene, 100, 200, 1, 1.)
    second = replace(first, sensor_timestamp_ns=150, host_timestamp_ns=250)
    capture = TriggeredCapture((first, second), 1, 199, "shot", "session")
    path = save_offline_capture(tmp_path, capture, app_sha=SHA, source="synthetic_fixture")
    mode = "fixture:mode"
    profile = CameraCalibrationProfile(
        CheckerboardCalibration((32, 16), np.diag([30., 30., 1.]), np.zeros(5), 0., (0.,)), mode,
    )
    club = ClubFaceModel(ClubFamily.IRON, "fixture", FaceSurface.PLANAR, 80., 40., evidence_source="fixture")
    binding = CalibrationClubBinding(calibration_revision(profile), club.model_id, club_geometry_revision(club))
    admission = RecordedCaptureAdmission(capture_fingerprint(capture), SHA, "synthetic_fixture",
                                         "fixture:camera", mode, binding)
    with pytest.raises(RecordedReplayRejected, match="trigger not bracketed"):
        prepare_recorded_replay(path, admission=admission, camera_identity="fixture:camera",
                                profile=profile, club=club, max_sensor_gap_ns=100, max_host_gap_ns=100)
