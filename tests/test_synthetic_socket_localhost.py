"""Gate 23: real loopback TCP Socket.IO transport, isolated from hardware startup.

The Flask application is hosted in a child process without calling main(),
start_monitor(), camera acquisition, or any radar initialization. The client
is a distinct python-socketio client in the pytest process.
"""

import multiprocessing
import socket
import time

import pytest
import socketio


def _serve_synthetic_socket(port):
    """Run only the existing Flask-SocketIO application on loopback."""
    from openflight.server import app, socketio as server_socketio

    server_socketio.run(
        app, host="127.0.0.1", port=port,
        debug=False, use_reloader=False, allow_unsafe_werkzeug=True,
    )


def _available_loopback_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


@pytest.fixture(scope="module")
def localhost_socket_server():
    """Bounded startup and guaranteed child-process teardown."""
    port = _available_loopback_port()
    process = multiprocessing.get_context("spawn").Process(
        target=_serve_synthetic_socket, args=(port,), daemon=True,
    )
    process.start()
    url = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 20
    ready = False
    try:
        while time.monotonic() < deadline:
            if not process.is_alive():
                pytest.fail(f"Socket.IO server child exited: {process.exitcode}")
            probe = socketio.Client(reconnection=False, logger=False, engineio_logger=False)
            try:
                probe.connect(url, transports=["polling"], wait_timeout=1)
                ready = True
                break
            except (socketio.exceptions.ConnectionError, OSError):
                time.sleep(0.2)
            finally:
                if probe.connected:
                    probe.disconnect()
        if not ready:
            pytest.fail("Isolated localhost Socket.IO server did not become ready")
        yield url
    finally:
        if process.is_alive():
            process.terminate()
        process.join(timeout=5)
        if process.is_alive():
            process.kill()
            process.join(timeout=5)
        assert not process.is_alive(), "Socket.IO test server child leaked"


@pytest.fixture
def network_client(localhost_socket_server):
    """A real client connection over the local TCP stack."""
    client = socketio.Client(reconnection=False, logger=False, engineio_logger=False)
    client.connect(localhost_socket_server, transports=["polling"], wait_timeout=3)
    try:
        yield client
    finally:
        if client.connected:
            client.disconnect()


@pytest.mark.parametrize(("case_id", "status", "coordinates"), [
    ("toe-high", "ok", (12, 5)),
    ("heel-low", "ok", (-12, -5)),
    ("outside-face", "outside_face", None),
    ("no-tangency", "no_tangency", None),
])
def test_real_localhost_acknowledgement(network_client, case_id, status, coordinates):
    payload = network_client.call(
        "get_synthetic_face_impact", {"case_id": case_id}, timeout=3,
    )
    assert payload["schema_version"] == 1
    assert payload["source"] == "synthetic_python_pipeline"
    assert payload["case_id"] == case_id
    assert payload["ok"] is True
    assert payload["result"]["status"] == status
    if coordinates is None:
        assert "x_mm" not in payload["result"]
        assert "y_mm" not in payload["result"]
        assert payload["result"]["rejection_reason"]
    else:
        assert (payload["result"]["x_mm"], payload["result"]["y_mm"]) == coordinates


@pytest.mark.parametrize("case_payload", [
    {"case_id": "unknown"}, {"case_id": None}, {"case_id": []}, {},
])
def test_real_localhost_rejects_invalid_cases(network_client, case_payload):
    payload = network_client.call("get_synthetic_face_impact", case_payload, timeout=3)
    assert payload["schema_version"] == 1
    assert payload["ok"] is False
    assert "result" not in payload
    assert "polygon_face_mm" not in payload


def test_real_localhost_disconnect_and_new_connection(localhost_socket_server):
    first = socketio.Client(reconnection=False)
    first.connect(localhost_socket_server, transports=["polling"], wait_timeout=3)
    try:
        assert first.call("get_synthetic_face_impact", {"case_id": "toe-high"}, timeout=3)[
            "result"
        ]["status"] == "ok"
    finally:
        first.disconnect()
    assert not first.connected
    second = socketio.Client(reconnection=False)
    second.connect(localhost_socket_server, transports=["polling"], wait_timeout=3)
    try:
        payload = second.call(
            "get_synthetic_face_impact", {"case_id": "heel-low"}, timeout=3,
        )
        assert payload["result"]["status"] == "ok"
        assert payload["result"]["x_mm"] == -12
    finally:
        second.disconnect()
