"""Gate 22: exercise the real Flask-SocketIO event path in process.

No TCP listener, camera acquisition, radar initialization or physical hardware.
"""

import pytest

from openflight import server


@pytest.fixture
def socket_client():
    """Use Flask-SocketIO's actual event dispatch and ack serialization."""
    client = server.socketio.test_client(server.app)
    assert client.is_connected()
    try:
        yield client
    finally:
        if client.is_connected():
            client.disconnect()


@pytest.mark.parametrize(("case_id", "status", "coordinates"), [
    ("toe-high", "ok", (12, 5)),
    ("heel-low", "ok", (-12, -5)),
    ("outside-face", "outside_face", None),
    ("no-tangency", "no_tangency", None),
])
def test_synthetic_ack_through_socketio_dispatch(socket_client, case_id, status, coordinates):
    acknowledgements = socket_client.emit(
        "get_synthetic_face_impact", {"case_id": case_id}, callback=True,
    )
    assert len(acknowledgements) == 1
    payload = acknowledgements[0]
    assert payload["schema_version"] == 1
    assert payload["source"] == "synthetic_python_pipeline"
    assert payload["case_id"] == case_id
    assert payload["result"]["status"] == status
    assert len(payload["polygon_face_mm"]) == 4
    if coordinates is None:
        assert "x_mm" not in payload["result"]
        assert "y_mm" not in payload["result"]
        assert payload["result"]["rejection_reason"]
    else:
        assert (payload["result"]["x_mm"], payload["result"]["y_mm"]) == coordinates


@pytest.mark.parametrize("request", [
    {"case_id": "not-registered"}, {"case_id": None}, {"case_id": []}, {},
])
def test_invalid_case_ack_contains_no_measurement(socket_client, request):
    acknowledgements = socket_client.emit(
        "get_synthetic_face_impact", request, callback=True,
    )
    assert len(acknowledgements) == 1
    payload = acknowledgements[0]
    assert payload["ok"] is False
    assert "result" not in payload
    assert "polygon_face_mm" not in payload


def test_reconnect_creates_fresh_socket_session_and_still_serves_requests(socket_client):
    before = socket_client.emit(
        "get_synthetic_face_impact", {"case_id": "toe-high"}, callback=True,
    )[0]
    assert before["result"]["status"] == "ok"
    socket_client.disconnect()
    assert not socket_client.is_connected()
    reconnect = server.socketio.test_client(server.app)
    try:
        assert reconnect.is_connected()
        after = reconnect.emit(
            "get_synthetic_face_impact", {"case_id": "heel-low"}, callback=True,
        )[0]
        assert after["result"]["status"] == "ok"
        assert after["result"]["x_mm"] == -12
    finally:
        reconnect.disconnect()
