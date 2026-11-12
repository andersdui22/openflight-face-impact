"""Socket fixture produces validated, nonphysical motion diagnostics."""

from openflight.camera.synthetic_motion_socket import synthetic_motion_demo_response


def test_synthetic_motion_socket_payload():
    payload = synthetic_motion_demo_response()
    assert payload["schema_version"] == 1
    assert payload["kind"] == "synthetic_image_space_motion"
    assert payload["physical_contact_confirmed"] is False
    assert payload["impact_frame_index"] is None
    assert payload["impact_x_mm"] is None
    assert len(payload["proximity_samples"]) == 5
    assert payload["closest_observed_frame_index"] == 2
