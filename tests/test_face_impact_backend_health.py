"""Face Impact-specific backend identity endpoint regression."""

from openflight import server


def test_face_impact_health_is_explicit_and_does_not_claim_camera_validation():
    response = server.app.test_client().get("/api/face-impact/health")
    assert response.status_code == 200
    assert response.get_json() == {
        "service": "openflight-face-impact",
        "protocol_version": 1,
        "status": "ready",
        "camera_validated": False,
    }
