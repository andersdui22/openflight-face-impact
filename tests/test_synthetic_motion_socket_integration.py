"""Gate 24: exercise the actual Flask-SocketIO synthetic diagnostic route.

This does not use physical camera hardware and never confirms club-ball contact.
"""

from openflight import server


def test_motion_demo_socket_emits_to_requesting_client_only():
    first = server.socketio.test_client(server.app)
    second = server.socketio.test_client(server.app)
    try:
        first.get_received()
        second.get_received()
        acknowledgement = first.emit("request_synthetic_motion_demo", callback=True)
        assert acknowledgement == {"ok": True, "kind": "synthetic_image_space_motion"}
        messages = [
            item["args"][0]
            for item in first.get_received()
            if item["name"] == "synthetic_motion_diagnostics"
        ]
        assert len(messages) == 1
        payload = messages[0]
        assert payload["schema_version"] == 1
        assert payload["physical_contact_confirmed"] is False
        assert payload["impact_frame_index"] is None
        assert payload["impact_x_mm"] is None
        assert payload["impact_y_mm"] is None
        assert payload["position_uncertainty_mm"] is None
        assert len(payload["proximity_samples"]) == 5
        assert not any(
            item["name"] == "synthetic_motion_diagnostics"
            for item in second.get_received()
        )
    finally:
        first.disconnect()
        second.disconnect()


def test_motion_demo_socket_requires_explicit_request():
    client = server.socketio.test_client(server.app)
    try:
        assert not any(
            item["name"] == "synthetic_motion_diagnostics"
            for item in client.get_received()
        )
    finally:
        client.disconnect()
