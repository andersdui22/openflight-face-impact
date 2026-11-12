"""Exercise server-owned raster replay through the real Socket.IO handler."""

from concurrent.futures import ThreadPoolExecutor

import pytest

from openflight import server
from openflight.camera.offline_session_archive import OfflineSessionArchive


@pytest.fixture
def clients():
    requesting = server.socketio.test_client(server.app)
    observing = server.socketio.test_client(server.app)
    try:
        yield requesting, observing
    finally:
        requesting.disconnect()
        observing.disconnect()


def _offline_events(client):
    return [event["args"][0] for event in client.get_received()
            if event["name"] == "offline_impact_evidence"]


def test_offline_raster_demo_emits_validated_contact_and_rejection_to_requester(clients):
    requesting, observing = clients
    accepted_ack = requesting.emit("request_offline_impact_demo", {"case_id": "contact"}, callback=True)
    assert accepted_ack == {"ok": True, "shot_id": "synthetic-contact"}
    accepted, = _offline_events(requesting)
    assert accepted["source"] == "offline_synthetic_analysis"
    assert accepted["session_id"] == "synthetic-offline-demo-v1"
    assert accepted["shot_id"] == accepted_ack["shot_id"]
    assert accepted["frame_index"] == 1
    assert accepted["accepted"] is True
    assert accepted["x_mm"] == pytest.approx(12, abs=3)
    assert accepted["y_mm"] == pytest.approx(5, abs=3)
    assert accepted["physically_validated"] is False
    assert accepted["position_uncertainty_mm"] is None

    rejected_ack = requesting.emit("request_offline_impact_demo", {"case_id": "missing-ball"}, callback=True)
    assert rejected_ack == {"ok": True, "shot_id": "synthetic-missing-ball"}
    rejected, = _offline_events(requesting)
    assert rejected["session_id"] == accepted["session_id"]
    assert rejected["shot_id"] == rejected_ack["shot_id"]
    assert rejected["accepted"] is False
    assert not {"frame_index", "x_mm", "y_mm", "horizontal_region", "vertical_region"} & rejected.keys()
    assert _offline_events(observing) == []


@pytest.mark.parametrize("data", [
    "contact", {}, {"case_id": "unknown"}, {"case_id": ["contact"]},
    {"case_id": "contact", "request_id": "INVALID"}, {"case_id": "contact", "request_id": None},
    {"case_id": "contact", "x_mm": 999}, {"case_id": "contact", "recipient": "other-client"},
])
def test_offline_raster_demo_rejects_untrusted_inputs_without_emitting(clients, data):
    requesting, observing = clients
    ack = requesting.emit("request_offline_impact_demo", data, callback=True)
    assert ack["ok"] is False
    assert _offline_events(requesting) == _offline_events(observing) == []


def test_saved_sessions_round_trip_and_export(tmp_path, monkeypatch, clients):
    archive_path = tmp_path / "face-impact.sqlite3"
    monkeypatch.setitem(server.app.config, "OFFLINE_IMPACT_ARCHIVE_PATH", archive_path)
    monkeypatch.setattr(server, "_local_offline_archive", lambda: OfflineSessionArchive(archive_path))
    requesting, observing = clients

    first = requesting.emit(
        "request_offline_impact_demo", {"case_id": "contact", "session_id": None}, callback=True,
    )
    accepted, = _offline_events(requesting)
    session_id = accepted["session_id"]
    assert first["shot_id"] == accepted["shot_id"]
    assert session_id != "synthetic-offline-demo-v1"
    for _ in range(2):
        ack = requesting.emit(
            "request_offline_impact_demo",
            {"case_id": "missing-ball", "session_id": session_id}, callback=True,
        )
        rejected, = _offline_events(requesting)
        assert ack["shot_id"] == rejected["shot_id"]
    assert _offline_events(observing) == []

    http = server.app.test_client()
    root = "/api/face-impact/sessions"
    sessions, = http.get(root).json["sessions"]
    assert sessions["session_id"] == session_id
    assert sessions["shot_count"] == 2
    response = http.get(f"{root}/{session_id}?download=1")
    assert response.status_code == 200
    assert "attachment" in response.headers["Content-Disposition"]
    contact, missing = response.json["shots"]
    assert contact["evidence"] == accepted
    assert missing["evidence"] == rejected
    assert "x_mm" not in missing["evidence"]
    assert contact["provenance"]["club"]["model_id"] == "synthetic-planar-face-v1"
    assert contact["provenance"]["calibration"]["image_size_px"] == [640, 400]
    assert contact["provenance"]["calculation"]["version"] == "offline-marker-impact-v1"
    assert len(contact["provenance"]["capture"]["sha256"]) == 64
    buffered = contact["provenance"]["capture"]
    assert buffered["acquisition"] == "synthetic-triggered-ring-v1"
    assert buffered["pre_trigger_count"] == 1
    assert [frame["host_timestamp_ns"] for frame in buffered["frames"]] == [16_000_000, 24_000_000]
    assert buffered["trigger_host_timestamp_ns"] == 20_000_000
    assert contact["provenance"]["quality"]["preflight"]["frame_count"] == 2
    assert missing["provenance"]["quality"]["impact_status"] == "rejected"
    analysis = http.get(f"{root}/{session_id}?analysis=1").json
    assert analysis["evidence"] == [accepted, rejected]
    assert analysis["clubs"][0]["mean_mm"] == [accepted["x_mm"], accepted["y_mm"]]
    assert analysis["clubs"][0]["spread_mm"] is None
    assert analysis["clubs"][0]["rejected_count"] == 1
    assert response.json["analysis"]["diagnostics"] == analysis["diagnostics"]
    assert http.get(f"{root}/missing").status_code == 404


def test_save_failure_prevents_publication(tmp_path, monkeypatch, clients):
    # A directory cannot be opened as a SQLite database.
    monkeypatch.setattr(server, "_local_offline_archive", lambda: OfflineSessionArchive(tmp_path))
    requesting, observing = clients
    ack = requesting.emit("request_offline_impact_demo", {"case_id": "contact"}, callback=True)
    assert ack["ok"] is False
    assert _offline_events(requesting) == _offline_events(observing) == []


def test_saved_history_requires_loopback(tmp_path, monkeypatch):
    monkeypatch.setitem(server.app.config, "OFFLINE_IMPACT_ARCHIVE_PATH", tmp_path / "offline.sqlite3")
    client = server.app.test_client()
    url = "/api/face-impact/sessions"
    assert client.get(url, environ_overrides={"REMOTE_ADDR": "192.0.2.4"}).status_code == 404
    assert client.get(url).json["sessions"] == []


def test_concurrent_writes_keep_first_evidence_and_provenance_together(tmp_path):
    archive = OfflineSessionArchive(tmp_path / "offline.sqlite3")

    def save(attempt):
        return archive.save({"session_id": "session", "shot_id": "shot", "reason": attempt},
                            {"attempt": attempt})

    with ThreadPoolExecutor(max_workers=2) as executor:
        first, second = executor.map(save, ("first writer", "second writer"))

    assert first == second
    shot, = archive.load("session")["shots"]
    assert shot["evidence"] == first
    assert shot["provenance"]["attempt"] == first["reason"]


def test_repeated_fixture_is_a_new_shot_but_retry_is_idempotent(tmp_path, monkeypatch, clients):
    path = tmp_path / "offline.sqlite3"
    monkeypatch.setattr(server, "_local_offline_archive", lambda: OfflineSessionArchive(path))
    requesting, observing = clients
    first_id, second_id = "a" * 32, "b" * 32
    events = []
    for request_id, session_id in ((first_id, None), (first_id, None), (second_id, f"synthetic-{first_id}")):
        ack = requesting.emit(
            "request_offline_impact_demo",
            {"case_id": "contact", "session_id": session_id, "request_id": request_id},
            callback=True,
        )
        assert ack["ok"] is True
        evidence, = _offline_events(requesting)
        assert ack["shot_id"] == evidence["shot_id"]
        assert ack["session_id"] == evidence["session_id"] == f"synthetic-{first_id}"
        assert ack["archived"] is True
        events.append(evidence)

    assert events[0] == events[1]
    assert events[0]["shot_id"] != events[2]["shot_id"]
    assert _offline_events(observing) == []

    export = server.app.test_client().get(f"/api/face-impact/sessions/synthetic-{first_id}?download=1").json
    assert [shot["evidence"] for shot in export["shots"]] == [events[0], events[2]]
    club, = export["analysis"]["clubs"]
    assert len(club["points_mm"]) == 2
    assert club["spread_mm"] == [0., 0.]


@pytest.mark.parametrize(("case_id", "message"), [
    ("invalid-frame", "Synthetic capture rejected"),
    ("missing-markers", "Synthetic marker or geometry analysis rejected"),
])
def test_bad_camera_replay_never_publishes_or_archives(tmp_path, monkeypatch, clients, case_id, message):
    archive = OfflineSessionArchive(tmp_path / "offline.sqlite3")
    monkeypatch.setattr(server, "_local_offline_archive", lambda: archive)
    requesting, observing = clients
    ack = requesting.emit("request_offline_impact_demo", {"case_id": case_id}, callback=True)
    assert ack == {"ok": False, "error": message}
    assert _offline_events(requesting) == _offline_events(observing) == []
    assert archive.list_sessions() == []



def test_two_admissible_frames_export_rejection_without_coordinates(tmp_path, monkeypatch, clients):
    archive = OfflineSessionArchive(tmp_path / "offline.sqlite3")
    monkeypatch.setattr(server, "_local_offline_archive", lambda: archive)
    requesting, observing = clients
    ack = requesting.emit(
        "request_offline_impact_demo", {"case_id": "ambiguous-contact"}, callback=True,
    )
    rejected, = _offline_events(requesting)
    assert ack == {"ok": True, "shot_id": rejected["shot_id"]}
    assert not rejected["accepted"]
    assert "multiple frames have accepted synthetic geometry" in rejected["reason"]
    assert not {"frame_index", "x_mm", "y_mm"} & rejected.keys()
    assert _offline_events(observing) == []
    response = server.app.test_client().get(
        f"/api/face-impact/sessions/{rejected['session_id']}?download=1",
    )
    assert response.status_code == 200
    assert response.json["shots"][0]["evidence"] == rejected
    club, = response.json["analysis"]["clubs"]
    assert club["points_mm"] == []
    assert club["rejected_count"] == 1
