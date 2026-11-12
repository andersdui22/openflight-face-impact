"""Exercise server-owned raster replay through the real Socket.IO handler."""

import pytest

from openflight import server


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
