import sqlite3

import pytest

from openflight import server

HEAD = "a" * 40
PREFIX = "/api/face-impact/recordings"
HEADERS = {"X-OpenFlight-Recording": "1"}


def test_independent_receipts_multiple_sessions_and_reopen(tmp_path, monkeypatch):
    archive = tmp_path / "sessions.sqlite"
    monkeypatch.setitem(server.app.config, "OFFLINE_IMPACT_ARCHIVE_PATH", archive)
    monkeypatch.setattr("openflight.camera.offline_recording_routes._producer_sha", lambda: HEAD)
    client = server.app.test_client()
    assert client.get(PREFIX).status_code == 403
    assert client.get(PREFIX, headers={**HEADERS, "Origin": "https://example.org"}).status_code == 403
    for case in ("contact", "heel-contact", "missing-markers", "ambiguous-contact"):
        receipt = client.post(PREFIX + "/fixtures", json={"case": case}, headers=HEADERS)
        assert receipt.status_code == 200, receipt.json
        digest = receipt.json["digest"]
        raw = client.get(f"{PREFIX}/{digest}", headers=HEADERS).data
        assert client.post(PREFIX, data=raw + b"x", headers=HEADERS).status_code == 422
        imported = client.post(PREFIX, data=raw, headers=HEADERS)
        assert imported.status_code == 200, imported.json
        meta = imported.json["recording"]
        client = server.app.test_client()
        assert any(item["zip_sha"] == digest for item in client.get(PREFIX, headers=HEADERS).json["recordings"])
        result = client.post(PREFIX + "/replay", json={"digest": digest}, headers=HEADERS)
        if case == "missing-markers":
            assert result.status_code == 422
            assert "landmark_or_geometry" in result.json["error"]
            continue
        assert result.status_code == 200, result.json
        expected = case != "ambiguous-contact"
        assert result.json["result"]["accepted"] is expected
        assert result.json["result"]["physically_validated"] is False
        repeated = client.post(PREFIX + "/replay", json={"digest": digest}, headers=HEADERS)
        assert repeated.json == result.json
        export = client.get(f"/api/face-impact/sessions/{meta['session_id']}?download=1")
        assert export.status_code == (200 if expected else 404)
        if expected:
            assert len(export.json["shots"]) == 1

    with sqlite3.connect(archive) as db:
        db.execute("UPDATE offline_recording_receipts SET receipt = '{}' WHERE zip_sha = ?", (digest,))
    result = client.post(PREFIX + "/replay", json={"digest": digest}, headers=HEADERS)
    assert result.status_code == 422
    assert "receipt changed" in result.json["error"]


def test_removing_import_retains_receipt_and_saved_session(tmp_path, monkeypatch):
    monkeypatch.setitem(server.app.config, "OFFLINE_IMPACT_ARCHIVE_PATH", tmp_path / "sessions.sqlite")
    monkeypatch.setattr("openflight.camera.offline_recording_routes._producer_sha", lambda: HEAD)
    client = server.app.test_client()
    digest = client.post(PREFIX + "/fixtures", json={"case": "contact"}, headers=HEADERS).json["digest"]
    raw = client.get(f"{PREFIX}/{digest}", headers=HEADERS).data
    session = client.post(PREFIX, data=raw, headers=HEADERS).json["recording"]["session_id"]
    assert client.post(PREFIX + "/replay", json={"digest": digest}, headers=HEADERS).status_code == 200
    assert client.post(PREFIX + "/remove-import", json={"digest": digest}, headers=HEADERS).json["removed"]
    assert client.get(PREFIX, headers=HEADERS).json["recordings"] == []
    assert client.get(f"/api/face-impact/sessions/{session}?download=1").status_code == 200
    assert client.post(PREFIX, data=raw, headers=HEADERS).status_code == 200
