"""Gate 21: verify synthetic-only socket response data and rejection behavior."""

import pytest

from openflight.camera.synthetic_impact_socket import synthetic_face_impact_response


@pytest.mark.parametrize(("case_id", "status", "coordinates"), [
    ("toe-high", "ok", (12., 5.)),
    ("heel-low", "ok", (-12., -5.)),
    ("outside-face", "outside_face", None),
    ("no-tangency", "no_tangency", None),
])
def test_synthetic_socket_result(case_id, status, coordinates):
    payload = synthetic_face_impact_response(case_id)
    assert payload["schema_version"] == 1
    assert payload["source"] == "synthetic_python_pipeline"
    assert payload["ok"] is True
    assert payload["case_id"] == case_id
    assert len(payload["polygon_face_mm"]) == 4
    assert payload["result"]["status"] == status
    if coordinates is None:
        assert "x_mm" not in payload["result"]
        assert "y_mm" not in payload["result"]
        assert payload["result"]["rejection_reason"]
    else:
        assert payload["result"]["x_mm"] == coordinates[0]
        assert payload["result"]["y_mm"] == coordinates[1]
        assert "rejection_reason" not in payload["result"]


@pytest.mark.parametrize("case_id", ["unknown", "", None, 12, [], {}])
def test_unknown_case_never_fabricates_measurements(case_id):
    payload = synthetic_face_impact_response(case_id)
    assert payload["ok"] is False
    assert "result" not in payload
    assert "polygon_face_mm" not in payload


@pytest.mark.parametrize("case_id", ["toe-high", "heel-low", "outside-face", "no-tangency"])
def test_synthetic_socket_never_claims_physical_calibration(case_id):
    """Gate 19 boundary: a demo result is not verified ELP evidence."""
    payload = synthetic_face_impact_response(case_id)
    assert payload["source"] == "synthetic_python_pipeline"
    assert "physical_validation" not in payload
    assert "camera_mode_compatible" not in payload
    assert "calibration_revision" not in payload
    assert "club_geometry_compatible" not in payload
    assert "physical_validation" not in payload["result"]


@pytest.mark.parametrize("case_id", ["outside-face", "no-tangency"])
def test_rejected_synthetic_results_never_publish_regions_or_coordinates(case_id):
    """A rejected demo contact must not look like a measured impact."""
    result = synthetic_face_impact_response(case_id)["result"]
    for key in ("x_mm", "y_mm", "horizontal_region", "vertical_region"):
        assert key not in result
