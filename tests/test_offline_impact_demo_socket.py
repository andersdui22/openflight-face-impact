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
    assert contact["provenance"]["quality"]["preflight"]["frame_count"] == 2
    assert missing["provenance"]["quality"]["impact_status"] == "rejected"
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
